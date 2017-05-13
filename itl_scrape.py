import os
import sys
import re
import requests as rq
import mechanicalsoup as ms
import html2text
import multiprocessing
import bs4
import getpass

from multiprocessing import Process
from bs4 import BeautifulSoup as bs
from getpass import getpass



base_url = "https://ntnu.itslearning.com/"
folder_url = "https://ntnu.itslearning.com/Folder/processfolder.aspx?FolderID="

def make_folder(curpath, title):
    folder_path = os.path.join(curpath,title)
    #print("making dir:",folder_path)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    os.chdir(folder_path)

class itslearning_scraper():
    def __init__(self):
        self.failure=0
        self.browser = ms.StatefulBrowser()
        self.html2text = html2text.HTML2Text()
        self.start_url = "https://innsida.ntnu.no/lms-ntnu"
        #path = os.path.abspath(os.path.curdir)

    def select_path(self, path):
        newpath = os.path.join(path, "scraped")
        if not os.path.exists(newpath):
            os.makedirs(newpath)
        os.chdir(newpath)

    def login(self, username, password):
        self.browser.open(self.start_url)
        try:
            self.browser.select_form("form[name=f]")
            self.browser["feidename"]=username
            self.browser["password"]=password
            self.browser.submit_selected()
        except:
            print("Something weird happened")
        try:
            self.browser.select_form("form[action=https://sats.itea.ntnu.no/sso-wrapper/feidelogin]")
            self.browser.submit_selected()
            self.key = self.browser.session.cookies.get_dict()
            self.jsession={"JSESSIONID": self.key["JSESSIONID"]}
            resp = rq.get(self.start_url, cookies=self.jsession)
            self.get_cookies(resp)
            self.find_all_courses()
        except:
            print("Didn't get login redirect")

    def get_cookies(self, resp):
        split_cookie = resp.request.headers["Cookie"].split(";")
        self.cookies = dict([[elm.split("=",1)[0].strip(), elm.split("=",1)[1].strip()] for elm in split_cookie])

    def enter(self):
        username = input("Enter NTNU-username: ")
        password = getpass("Enter your NTNU-password: ")
        self.login(username,password)

    def find_courses(self):
        resp = rq.get("https://ntnu.itslearning.com/Course/AllCourses.aspx", cookies=self.cookies)
        print(resp.url)

        three = bs(resp.text, "html.parser")
        course = three.find("table",{"class":"h-table-show-first-4-columns"})
        active_courses = course.find_all("a",{"class":"ccl-iconlink"})
        courses = {}

        for link in active_courses:
            courses[link.get("href")]=link.contents[0].contents[0]
        self.courses = courses

    def find_all_courses(self):
        get_all = { "__EVENTARGUMENT":"",
        "__EVENTTARGET":"ctl26$ctl00$ctl25$ctl02",
        "__EVENTVALIDATION":"",
        "__LASTFOCUS":"",
        "__VIEWSTATE":"",
        "__VIEWSTATEGENERATOR":"",
        "ctl26$ctl00$ctl25$ctl02":"All",
        }

        course_url = "https://ntnu.itslearning.com/Course/AllCourses.aspx"
        self.browser.open(course_url)
        resp = rq.get(course_url, cookies=self.cookies)

        target = "ctl26$ctl00$ctl25$ctl02"
        three = bs(resp.text, "html.parser")

        __VIEWSTATE = bs(resp.text, "html.parser").find("input", {"id":"__VIEWSTATE"}).attrs["value"]
        __EVENTVALIDATION = bs(resp.text, "html.parser").find("input", {"id":"__EVENTVALIDATION"}).attrs["value"]
        __VIEWSTATEGENERATOR = bs(resp.text, "html.parser").find("input", {"id":"__VIEWSTATEGENERATOR"}).attrs["value"]

        get_all["__VIEWSTATE"] = __VIEWSTATE
        get_all["__EVENTVALIDATION"] = __EVENTVALIDATION
        get_all["__VIEWSTATEGENERATOR"]=__VIEWSTATEGENERATOR
        headers = resp.headers
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        post = rq.post(course_url, cookies=self.cookies, data=get_all)

        __VIEWSTATE = bs(post.text, "html.parser").find("input", {"id":"__VIEWSTATE"}).attrs["value"]
        __EVENTVALIDATION = bs(post.text, "html.parser").find("input", {"id":"__EVENTVALIDATION"}).attrs["value"]
        __VIEWSTATEGENERATOR = bs(post.text, "html.parser").find("input", {"id":"__VIEWSTATEGENERATOR"}).attrs["value"]
        get_all["ctl26$PageSizeSelect"]="200"
        get_all["__EVENTTARGET"]="ctl26:7:Pagesize:100"
        post = rq.post(course_url, cookies=self.cookies, data=get_all)

        with open("courses.html","wb") as f:
            f.write(bytes(post.text.encode("utf-8")))
            f.close()

        three = bs(post.text, "html.parser")
        course = three.find("table",{"class":"h-table-show-first-4-columns"})
        active_courses = course.find_all("a",{"class":"ccl-iconlink"})
        courses = {}
        for link in active_courses:
            courses[link.get("href")]=link.contents[0].contents[0]
        self.course = courses
        return courses

    def get_itl_cookies(self):
        return self.cookies


    def find_folder_table(self,html):
        three = bs(html, "html.parser")
        folders = three.find('table',{"id":"ctl00_ContentPlaceHolder_ProcessFolderGrid_T"})
        return folders

    def download_link(self, link, title):
        print("Trying to download: {}".format(link))
        r = rq.get(link, cookies=self.cookies, stream=True)
        try:
            filename = re.search('FileName=(.+?)&',r.url).group(1)
        except:
            filename = title
            self.failure += 1
        print("File created with name:",filename)
        filename = os.path.join(os.path.abspath(os.path.curdir),filename)
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
        print("complete")

    def find_file(self, html):
        try:
            three = bs(html, "html.parser")
        except:
            print(html)
            print(type(html))
            print(html.find_all('a'))
            sys.exit(1)
        links = three.find_all('a')

        for link in links:
            if "download.aspx" in link.get("href"):
                Process(target=self.download_link, args=(base_url+link.get("href")[2:], self.failure)).start()
            elif "DownloadRedirect.ashx" in link.get("href"):
                title = link.contents[1].contents[0]
                Process(target=self.download_link, args=(link.get("href"), title)).start()

    def find_essay_files(self, html):
        three = bs(html, "html.parser")
        attached_files=three.find("div", {"id":"EssayDetailedInformation_FileListWrapper_FileList"})
        handin_files=three.find("div", {"id":"DF_FileList"})
        text=three.find("div", {"class":"h-userinput itsl-assignment-description"})

        if text:
            title = three.find("span", {"id":"ctl05_TT"}).contents[0]
            text = self.html2text.handle(str(text))
            fp = os.path.join(os.path.abspath(os.path.curdir), title)
            #convert to md?
            with open(fp+".md", "wb") as note:
                note.write(bytes(text.encode("utf-8")))
                note.close()

        if attached_files:
            self.find_file(str(attached_files))

        if handin_files:
            self.find_file(str(handin_files))

    def find_link(self,html):

        three = bs(html, "html.parser")
        section_link = three.find("a", {"id":"ctl00_ctl00_MainFormContent_ResourceContent_Link"})
        if section_link is None:
            link = three.find("a",{"id":"ctl00_ctl00_MainFormContent_ResourceContent_DownloadButton_DownloadLink"})
            try:
                print(link.get("download"))
                Process(target=self.download_link,args=(link.get("href"), link.get("download"))).start()
            except:
                print("Broken download link")
                pass
            return

        print(section_link)
        target = section_link.get("href")
        print(target)
        fp = os.path.join(os.path.abspath(os.path.curdir), "".join(target.split('/')))
        print("filepath:", fp)
        with  open(fp+".url", "wb") as shortcut:
            shortcut.write(b'[InternetShortcut]\n')
            shortcut.write(bytes(r'URL={}'.format(target).encode("utf-8")))
            shortcut.close()

    def save_note(self,html):
        three = bs(html, "html.parser")
        title = three.find("h1").contents[0].contents[1]
        print(title)
        text = three.find("div", {"class":"h-userinput"})
        print(text.contents[0])
        text = self.html2text.handle(str(text))
        fp = os.path.join(os.path.abspath(os.path.curdir), title)
        #convert to md?
        try:
            with open(fp+".md", "wb") as note:
                note.write(bytes(text.encode("utf-8")))
                note.close()
        except FileNotFoundError:
            if "/" in title:
                print("File contains slash '%s'. Skipping" % title)
            else:
                print("File not found '%s'" % title)

    def find_files(self,folders):
        for link in folders.find_all('a'):
            if "File" in link.get("href"):
                r = rq.get(base_url+link.get("href"), cookies=self.cookies)
                self.find_file(r.text)

            elif "LearningToolElement" in link.get("href"):
                r = rq.get(base_url+link.get("href"), cookies=self.cookies)
                three = bs(r.text, "html.parser")
                iframe = three.find('iframe')
                print(iframe.get("src"))
                if iframe is not None:
                    url = iframe.get("src")
                    r = rq.get(url, cookies=self.cookies)
                    link = self.find_link(r.text)

            elif "/note/View_Note" in link.get("href"):
                r = rq.get(base_url+link.get("href"), cookies=self.cookies)
                print(r.url)
                self.save_note(r.text)

            elif "folder" in link.get("href"):
                #print(link)
                itl_path = os.path.join(os.path.abspath(os.path.curdir))
                title = link.contents[0]
                if not title:
                    title = "Failed to name"+str(self.failure)
                    self.failure +=1
                make_folder(itl_path, str(title))
                r = rq.get(base_url+link.get("href"), cookies=self.cookies)
                table = self.find_folder_table(r.text)
                #print(table)
                self.find_files(table)
                os.chdir('..')
                #print(r.url)

            elif "read_essay" in link.get("href"):
                print("read_essay:",link.get("href"))
                itl_path = os.path.join(os.path.abspath(os.path.curdir))
                title = link.contents[0]
                make_folder(itl_path, str(title))
                r = rq.get(base_url+link.get("href"), cookies=self.cookies)
                self.find_essay_files(r.text)
                os.chdir('..')

    def download_all(self):
        p  = []
        for link in self.courses:
            r = rq.get(base_url+link, cookies=self.cookies)
            course_path = os.path.join(os.path.abspath(os.path.curdir))
            make_folder(course_path, self.courses[link])
            folder_id = re.search("FolderID=(.+?)'",r.text).group(1)
            print("folder id",folder_id)
            print("folder_url"+folder_id)
            r = rq.get(folder_url+folder_id, cookies=self.cookies)
            print(r.url)
            table = self.find_folder_table(r.text)
            Process(target=self.find_files, args=(table,)).start()
            os.chdir('..')

    def download_one(self, url):
        folder_title=input("folder title:")
        r = rq.get(url, cookies=self.cookies)
        course_path = os.path.join(os.path.abspath(os.path.curdir))
        make_folder(course_path, folder_title)
        folder_id = re.search("FolderID=(.+?)'",r.text).group(1)
        r = rq.get(folder_url+folder_id, cookies=self.cookies)
        r = rq.get(folder_url+folder_id, cookies=self.cookies)
        table = self.find_folder_table(r.text)
        self.find_files(table)

    def download_links(self, links):
        for link in links:
            r = rq.get(base_url+link, cookies=self.cookies)
            course_path = os.path.join(os.path.abspath(os.path.curdir))
            make_folder(course_path, links[link])
            folder_id = re.search("FolderID=(.+?)'",r.text).group(1)
            print("folder id",folder_id)
            print("folder_url"+folder_id)
            r = rq.get(folder_url+folder_id, cookies=self.cookies)
            print(r.url)
            table = self.find_folder_table(r.text)
            Process(target=self.find_files, args=(table,)).start()
            os.chdir('..')

    def get_courses(self):
        return self.courses

    def get_all_courses(self):
        self.browser.open("https://ntnu.itslearning.com/Course%2fAllCourses.aspx")
        p = self.browser.get_current_page()
        print(p)
        print(self.browser.session.cookies.get_dict())

#print(args.session_cookie)
#key = args.session_cookie
if __name__ == '__main__':
    scraper = itslearning_scraper()
    scraper.enter()
    url = input("Enter course url or press enter to download all active courses:")
    if url:
        scraper.download_one(url)
    else:
        scraper.download_all()
