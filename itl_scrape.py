import os
import re
import argparse
import requests as rq
from bs4 import BeautifulSoup as bs

key = input("Enter sessionID:")
print(key)
cookie={"JSESSIONID": key}
print(cookie)
login = "https://innsida.ntnu.no/lms-ntnu"

r = rq.get(login, cookies=cookie)
print(r.url)

tc = r.request.headers["Cookie"].split(";")
sp_tc = [[elm.split("=",1)[0].strip(), elm.split("=",1)[1].strip()] for elm in tc]
itl_cookies=dict(sp_tc)
print(itl_cookies)

base_url = "https://ntnu.itslearning.com/"
url = "https://ntnu.itslearning.com/Folder/processfolder.aspx?FolderID=3204092"

path = os.path.abspath(os.path.curdir)
newpath = os.path.join(path,"scrape")
global failure
failure=0

if not os.path.exists(newpath):
    os.makedirs(newpath)
print(path)
print(newpath)
os.chdir(newpath)

def make_folder(curpath, title):
    folder_path = os.path.join(curpath,title)
    print("making dir:",folder_path)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    os.chdir(folder_path)

def find_folder_table(html):
    three = bs(html, "html.parser")
    folders = three.find('table',{"id":"ctl00_ContentPlaceHolder_ProcessFolderGrid_T"})
    return folders


def download_link(link, title):
            print("Trying to download: {}".format(link))
            r = rq.get(link, cookies=itl_cookies, stream=True)
            print(r.url)
            try:
                filename = re.search('FileName=(.+?)&',r.url).group(1)
            except:
                filename = title
                global failure
                failure += 1
            print(filename)
            filename = os.path.join(os.path.abspath(os.path.curdir),filename)
            with open(filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
            print("complete")
import sys

def find_file(html):
    try:
        three = bs(html, "html.parser")
    except:
        print(html)
        print(type(html))
        print(html.find_all('a'))
        sys.exit(1)
    links = three.find_all('a')
    #print(links)

    for link in links:
        if "download.aspx" in link.get("href"):
            download_link(base_url+link.get("href")[2:], failure)
        elif "DownloadRedirect.ashx" in link.get("href"):
            title = link.contents[1].contents[0]
            download_link(link.get("href"), title)
            #print(r.text)

def find_essay_files(html):
    three = bs(html, "html.parser")
    attached_files=three.find("div", {"id":"EssayDetailedInformation_FileListWrapper_FileList"})
    handin_files=three.find("div", {"id":"DF_FileList"})
    if attached_files:
        find_file(str(attached_files))
    if handin_files:
        find_file(str(handin_files))

def find_link(html):

    three = bs(html, "html.parser")
    section_link = three.find("a", {"id":"ctl00_ctl00_MainFormContent_ResourceContent_Link"})
    if section_link is None:
        link = three.find("a",{"id":"ctl00_ctl00_MainFormContent_ResourceContent_DownloadButton_DownloadLink"})
        print(link.get("download"))
        download_link(link.get("href"), link.get("download"))
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
import html2text
def save_note(html):
    three = bs(html, "html.parser")
    title = three.find("h1").contents[0].contents[1]
    print(title)
    text = three.find("div", {"class":"h-userinput"})
    print(text.contents[0])
    h = html2text.HTML2Text()
    text = h.handle(str(text))
    fp = os.path.join(os.path.abspath(os.path.curdir), title)
    #convert to md?
    with open(fp+".md", "wb") as note:
        note.write(bytes(text.encode("utf-8")))
        note.close()

def find_files(folders):
        for link in folders.find_all('a'):
            if "File" in link.get("href"):
                r = rq.get(base_url+link.get("href"), cookies=itl_cookies)
                find_file(r.text)

            elif "LearningToolElement" in link.get("href"):
                r = rq.get(base_url+link.get("href"), cookies=itl_cookies)
                three = bs(r.text, "html.parser")
                iframe = three.find('iframe')
                print(iframe.get("src"))
                if iframe is not None:
                    url = iframe.get("src")
                    r = rq.get(url, cookies=itl_cookies)
                    link = find_link(r.text)

            elif "/note/View_Note" in link.get("href"):
                r = rq.get(base_url+link.get("href"), cookies=itl_cookies)
                print(r.url)
                save_note(r.text)

            elif "folder" in link.get("href"):
                #print(link)
                itl_path = os.path.join(os.path.abspath(os.path.curdir))
                title = link.contents[0]
                make_folder(itl_path, title)
                r = rq.get(base_url+link.get("href"), cookies=itl_cookies)
                table = find_folder_table(r.text)
                #print(table)
                find_files(table)
                os.chdir('..')
                #print(r.url)

            elif "read_essay" in link.get("href"):
                print("read_essay:",link.get("href"))
                itl_path = os.path.join(os.path.abspath(os.path.curdir))
                title = link.contents[0]
                make_folder(itl_path, title)
                r = rq.get(base_url+link.get("href"), cookies=itl_cookies)
                find_essay_files(r.text)
                os.chdir('..')



#print(args.session_cookie)
#key = args.session_cookie

r = rq.get(url, cookies=itl_cookies)
print(r.url)
table = find_folder_table(r.text)
find_files(table)

