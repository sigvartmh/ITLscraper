import appJar
import itl_scrape
import os

from appJar import gui
from itl_scrape import itslearning_scraper

app = gui("It's learning scraper")
scraper = itslearning_scraper()

def download(btn):
    courses = scraper.find_all_courses()
    course_links = {}
    for i, label in enumerate(courses):
        selected = app.getCheckBox(courses[label])
        if selected:
            course_links[label]=courses[label]
    #print(course_links.encode('utf-8'))

    print("Download selected")
    scraper.download_links(course_links)

def select_none(btn):
    courses = scraper.find_all_courses()
    for i, label in enumerate(courses):
        app.setCheckBox(courses[label], ticked=False, callFunction=False)
    print("select none")

def select_all(btn):
    courses = scraper.find_all_courses()
    for i, label in enumerate(courses):
        app.setCheckBox(courses[label], ticked=True, callFunction=False)
    print("select all")

def select_folder(btn):
    path = app.directoryBox(title="Folder to save into", dirName=None)
    print(path)
    app.setLabel("path", path)
    scraper.select_path(path)

def press(btn):
    user = app.getEntry("feideuser")
    password = app.getEntry("password")
    scraper.login(user,password)
    courses = scraper.find_all_courses()

    app.removeAllWidgets()

    app.addLabel("title", "Courses you want to download", 0, 0, 2)
    app.setFont(12)
    space = 0

    app.startLabelFrame("Courses to download")
    j = 0
    k = 1
    for i, label in enumerate(courses):
        app.addCheckBox(courses[label],  k, j )
        #app.setCheckBox(courses[label],ticked=True, callFunction=False)
        k += 1
        if k >= 20:
            k=0
            j+=1
        space = i

    app.stopLabelFrame()
    print(space)
    app.startLabelFrame("Select folder")
    app.addButton("Chose folder", select_folder, space+2, 0, 0)
    path = os.path.abspath(os.path.curdir)
    app.addLabel("path", path, space+2, 1)
    app.stopLabelFrame()
    app.startLabelFrame("Optional Actions")
    app.addButton("Select none", select_none, 0, 0, 0)
    app.addButton("Select all", select_all, 0, 1, 0)
    app.stopLabelFrame()
    app.startLabelFrame("Final step")
    app.addButton("Download", download, 0, 0, 2)
    app.stopLabelFrame()

app.startLabelFrame("It's Learning time")
app.setSticky("ew")
app.setFont(20)

app.addLabel("feideuser", "Username:", 0,0)
app.addEntry("feideuser",0,1)
app.addLabel("password", "Password:", 1, 0)
app.addSecretEntry("password", 1 , 1)
app.stopLabelFrame()
app.addButton("Login", press, 2, 0, 2)
app.setFocus("feideuser")
app.go()
