# "utf-8".
from selenium import webdriver
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import tkinter as tk
from tkinter.filedialog import askopenfilename
from tkinter.filedialog import askdirectory
import timeit
import wget
import os
import urllib3
import sqlite3
import queue

downloadDir = 'C:\\download\\'
configDir = 'C:\\config\\'
myDriver = 'C:\\Program Files\\Google\\Chrome\\Application\\chromedriver.exe'
homePage = 'http://www.gaoyao.gov.cn/'
q = queue.Queue()
keys = []


def findChildPage(myURL):
    print('find child page of ' + myURL)
    # Timer Starts
    start = timeit.default_timer()
    # instantiate a chrome options object so you can set the size and headless preference
    chrome_options = Options()

    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")

    # Initialize driver
    driver = webdriver.Chrome(chrome_options=chrome_options,
                              executable_path=myDriver)

    # Go to vk.com and get element. Print for fun/testing
    driver.get(myURL)

    # Dynamically pull page information
    wait = WebDriverWait(driver, 30)
    try:
        wait.until(
            expected_conditions.presence_of_element_located(
                (By.CSS_SELECTOR, 'a')))
    except Exception:
        print("It could not find the child page")
        return 1

    # record down main page
    pageUrl = myURL
    filePath = downloadDir + pageUrl.replace(':', '').replace('/', '').replace(
        '\\', '').replace('"', '').replace('*', '').replace('<', '').replace(
            '>', '').replace('?', '').replace('|', '')
    recordDownProcess(pageUrl, filePath, 'P', 'P')
    downloadPage(pageUrl, filePath)
    searchFile(pageUrl, filePath, keys)

    # record down child link
    pageElements = driver.find_elements(By.CSS_SELECTOR, "a")
    if len(pageElements) < 1:
        return 1

    for pageElement in pageElements:
        # check if it's already recorded down
        pageUrl = pageElement.get_attribute('href')
        print(pageUrl)
        if not pageUrl.__contains__(homePage):
            continue
        conn = sqlite3.connect('gaoyao.db')
        cursor = conn.cursor()
        cursor.execute(
            "select x0url,x0file,x0download,x0search from searchControl where x0url = '{}'"
            .format(pageUrl))
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        if len(result) > 0:
            continue
        # record down next page
        if pageUrl.endswith('.doc'):
            continue
        if pageUrl.endswith('.docx'):
            continue
        if pageUrl.endswith('.xls'):
            continue
        filePath = downloadDir + pageUrl.replace(':', '').replace(
            '/',
            '').replace('\\', '').replace('"', '').replace('*', '').replace(
                '<', '').replace('>', '').replace('?', '').replace('|', '')
        recordDownProcess(pageUrl, filePath, 'P', 'P')
        downloadPage(pageUrl, filePath)
        searchFile(pageUrl, filePath, keys)
        q.put(pageUrl)

    while not q.empty():
        pageUrl = q.get()
        findChildPageWithoutInit(driver, pageUrl)

    # Timer Stops
    stop = timeit.default_timer()

    # Prints the Start and End Time to Console
    print('Time: ', stop - start)


def findChildPageWithoutInit(driver, fatherUrl):
    try:
        driver.get(fatherUrl)

        # Dynamically pull page information
        wait = WebDriverWait(driver, 30)
        try:
            wait.until(
                expected_conditions.presence_of_element_located(
                    (By.CSS_SELECTOR, 'a')))
        except Exception:
            print("It could not find the child page")
            return 1
        pageElements = driver.find_elements(By.CSS_SELECTOR, 'a')
    except:
        print('driver get fail ' + fatherUrl)
        return 1
    # record down child link
    if len(pageElements) < 1:
        return 1

    for pageElement in pageElements:

        # check if it's already recorded down
        try:
            pageUrl = pageElement.get_attribute('href')
        except:
            continue
        # if no href for this a element, skip this element
        if not pageUrl:
            continue
        print(pageUrl)
        if not pageUrl.__contains__(homePage):
            continue
        try:
            conn = sqlite3.connect('gaoyao.db')
            cursor = conn.cursor()
            cursor.execute(
                "select x0url,x0file,x0download,x0search from searchControl where x0url = '{}'"
                .format(pageUrl))
            result = cursor.fetchall()
            cursor.close()
            conn.close()
        except:
            print('db connect/query fail')
            return 1
        if len(result) > 0:
            continue
        # record down next page
        if pageUrl.endswith('.doc'):
            continue
        if pageUrl.endswith('.docx'):
            continue
        if pageUrl.endswith('.xls'):
            continue
        filePath = downloadDir + pageUrl.replace(':', '').replace(
            '/',
            '').replace('\\', '').replace('"', '').replace('*', '').replace(
                '<', '').replace('>', '').replace('?', '').replace('|', '')
        recordDownProcess(pageUrl, filePath, 'P', 'P')
        downloadPage(pageUrl, filePath)
        searchFile(pageUrl, filePath, keys)
        q.put(pageUrl)

    while not q.empty():
        pageUrl = q.get()
        findChildPageWithoutInit(driver, pageUrl)


def downloadPage(pageUrl, filePath):
    print('downloadPage ' + pageUrl + " to " + filePath)
    # create dir
    if not os.path.exists(downloadDir):
        os.mkdir(downloadDir)
        print(downloadDir + ' created')
    # download page
    http = urllib3.PoolManager()
    response = http.request('GET', pageUrl)
    with open(filePath, 'wb') as f:
        f.write(response.data)
    # record down initial record S- sccuss, P- pending
    recordDownProcess(pageUrl, filePath, 'S', 'P')


def searchFile(pageUrl, filePath, keyWords):
    print('search ' + str(keyWords) + ' in ' + filePath)
    fr = open(filePath, 'r+', encoding='utf8')
    fb = fr.read()
    containsKeyword = ''
    for keyWord in keyWords:
        if fb.__contains__(keyWord):
            containsKeyword += keyWord + ','

    if containsKeyword and containsKeyword != '':
        recordDownProcess(pageUrl, filePath, 'S', 'E', containsKeyword)
    else:
        recordDownProcess(pageUrl, filePath, 'S', 'S', containsKeyword)
    fr.close()


def readKeysControl(keyFilePath):
    global keys
    fr = open(keyFilePath, 'r+', encoding='utf8')
    for key in fr.readlines():
        keys.append(key.replace('\n', ''))
    fr.close()


def recordDownProcess(pageUrl,
                      filePath,
                      downloadStatus,
                      searchStatus,
                      containsKeyword=''):
    print('record down url :' + pageUrl + ' file path :' + filePath +
          ' download status :' + downloadStatus + ' search status ' +
          searchStatus)
    conn = sqlite3.connect('gaoyao.db')
    cursor = conn.cursor()
    cursor.execute(
        "select x0url,x0file,x0download,x0search from searchControl where x0url = '{}' and x0file = '{}'"
        .format(pageUrl, filePath))
    result = cursor.fetchall()
    if len(result) > 0:
        cursor.execute(
            "update searchControl set x0download='{}',x0search='{}',x0keys='{}' where x0url='{}' and x0file='{}'"
            .format(downloadStatus, searchStatus, containsKeyword, pageUrl,
                    filePath))
        print('record updated')
    else:
        cursor.execute(
            "insert into searchControl values ('{}','{}','{}','{}','{}')".
            format(pageUrl, filePath, containsKeyword, downloadStatus,
                   searchStatus))
        print('record inserted')
    # verify db result
    conn.commit()
    cursor.execute(
        "select x0url,x0file,x0download,x0search from searchControl where x0url = '{}' and x0file = '{}'"
        .format(pageUrl, filePath))
    result = cursor.fetchall()
    print(result)
    # close db
    cursor.close()
    conn.close()


def main():
    # searchFile('http://www.gaoyao.gov.cn/', downloadDir + 'test.txt', '政民互吧动')
    readKeysControl(configDir + 'keys.txt')
    findChildPage(homePage)
    print(keys)


if __name__ == "__main__":
    main()
