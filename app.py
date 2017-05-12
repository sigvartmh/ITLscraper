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
    print(course_links)

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
        app.addCheckBox(courses[label],  k, j, )
        #app.setCheckBox(courses[label],ticked=True, callFunction=False)
        k += 1
        if k >= 20:
            k=0
            j+=1
        space = i

    app.stopLabelFrame()
    print(space)
    app.addButton("Download", download, space+2, 0)
    app.addButton("Select none", select_none, space+2, 1)
    app.addButton("Select all", select_all, space+2, 3)

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
