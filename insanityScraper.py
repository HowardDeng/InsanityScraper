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
myDriver = 'C:\\Program Files\\Google\\Chrome\\Application\\chromedriver.exe'
homePage = 'http://www.gaoyao.gov.cn/'
q = queue.Queue()


def page1(myDriver, myFolder):
    myURL = input("Please enter the link and press ENTER. \n")
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
                (By.CLASS_NAME, 'pv_counter')))
    except Exception:
        print("It could not find the picture are you on vk.com?")
        return 1
    counter = driver.find_element(By.CLASS_NAME, 'pv_counter').text
    counter = counter.split(' ')
    lastImgCount = counter[2]

    # Pull the image
    while True:
        wait = WebDriverWait(driver, 30)
        try:
            wait.until(
                expected_conditions.presence_of_element_located(
                    (By.XPATH, "//div[@id='pv_photo']/img[1]")))
        except Exception:
            print("It could not find the picture are you on vk.com?")
            return 1
        imgElement = driver.find_element(By.XPATH,
                                         "//div[@id='pv_photo']/img[1]")
        imgURL = imgElement.get_attribute('src')
        wget.download(imgURL, out=myFolder)
        counter = driver.find_element(By.CLASS_NAME, 'pv_counter').text
        counter = counter.split(' ')
        currentImgCount = counter[0]
        print(" Current Image Count: ", currentImgCount)
        if lastImgCount == currentImgCount:
            break
        imgElement.click()

    # Timer Stops
    stop = timeit.default_timer()

    # Prints the Start and End Time to Console
    print('Time: ', stop - start)


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
        filePath = downloadDir + pageUrl.replace(':', '').replace('/', '')
        recordDownProcess(pageUrl, filePath, 'P', 'P')
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
        filePath = downloadDir + pageUrl.replace(':', '').replace('/', '')
        recordDownProcess(pageUrl, filePath, 'P', 'P')
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


def searchFile(pageUrl, filePath, keyWord):
    print('search ' + keyWord + ' in ' + filePath)
    fr = open(filePath, 'r+', encoding='utf8')
    fb = fr.read()
    if fb.__contains__(keyWord):
        recordDownProcess(pageUrl, filePath, 'S', 'E')
    else:
        recordDownProcess(pageUrl, filePath, 'S', 'S')
    fr.close()


def recordDownProcess(pageUrl, filePath, downloadStatus, searchStatus):
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
            "update searchControl set x0download='{}',x0search='{}' where x0url='{}' and x0file='{}'"
            .format(downloadStatus, searchStatus, pageUrl, filePath))
        print('record updated')
    else:
        cursor.execute(
            "insert into searchControl values ('{}','{}','{}','{}')".format(
                pageUrl, filePath, downloadStatus, searchStatus))
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


def main2():
    tk.Tk().withdraw()
    myDriver = askopenfilename()
    myFolder = askdirectory()
    myAnswer = input("Is this the first page? y/n \n")

    if myAnswer == 'y' or myAnswer == 'Y':
        page1(myDriver, myFolder)
    elif myAnswer == 'n' or myAnswer == 'N':
        print("More to come.....")
    else:
        print("Disaster......")


def main():
    # downloadPage('http://www.gaoyao.gov.cn/', downloadDir + 'test.txt')
    # searchFile('http://www.gaoyao.gov.cn/', downloadDir + 'test.txt', '政民互吧动')
    findChildPage(homePage)


if __name__ == "__main__":
    main()
