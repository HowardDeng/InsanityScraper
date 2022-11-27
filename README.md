# InsanityScraper
Scraper to search sensitive content from html plain web site

-----
MsInsanity Links:

sample: http:***

-----
Why?
  On government request

-----
Prerequisites:

You need pip, wget, and Selenium modules installed. You need Chrome (bleh) and chrome web driver for your version of chrome. Will probably work with chromium too.

Installing pip (if you don't have it. if on linux you probably do.):

https://www.geeksforgeeks.org/how-to-install-pip-in-macos/

Selenium: (From terminal/cmd) pip install selenium

Chrome Web Driver: https://chromedriver.chromium.org/downloads

Note: Download the right one for your version of Chrome. To check chrome version do the following:
  Open Chrome > 3 dots/hamburger icon > Help > About

Chrome: https://www.google.com/chrome/

Chromium (untested): https://www.chromium.org/getting-involved/download-chromium/

-----
Use:
When running the program, it will ask you for your web driver path FIRST, and your desired target folder/directory SECOND. Just select them from the dialogue windows and you are set.

How to Run:
Run the py file from the directory you want the downloads to be. (I downloaded it to my MsInsanity Folder for example.)
python3 insanityScraper.py

Download Link:
When you find an artist you like, you need to click on the first picture of their collection (On their main page). Click the 'x' when it asks you to sign in, the post and picture will load. Then supply that link. An example of this is below:

https://vk.com/albums-72806334?z=photo-72806334_457241182%2Fphotos-72806334

Removing Duplicates:
Unfortunately, duplicate removal is not implemented yet. If you can use the following commands in the directory to remove dupes For MacOS, Linux, and Windows.


Windows:
powershell -c "Remove-Item * -Include '*(*'"

-----
Please read below for updates on bugs and whatnot.

To-do:
 1.create config dir in C:\ driver
 2.create download dir in C:\ driver
 3.put sensitive words in C:\keys.txt
 4.in your working lib, execute python createGaoYaoDB.py to create DB (a little change might need for this script,pls look into detail of the script)
