from appJar import gui
from itl_scrape import itslearning_scraper
app = gui("It's learning scraper")
scraper = itslearning_scraper()

def press(btn):
    user = app.getEntry("feideuser")
    password = app.getEntry("password")
    scraper.login(user,password)

#if course_url:
#else:
    print("pressed button", app.getEntry("feideuser"), app.getEntry("password"))
    app.removeAllWidgets()
    app.addLabel("title", "Courses to be selected", 0, 0, 2)
    test = scraper.get_courses()
    for i, label in enumerate(test):
        app.addCheckBox(test[label], i+1 ,0)

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
