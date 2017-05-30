# ITLscraper
Scrapes files from It's learning and stores them in categorised folders

## Requirements
* Python>= 3.x
* [Git](https://git-scm.com/)
* [Pip](https://pip.pypa.io/en/stable/installing/)

## Install python3 OSX
Install [homebrew](https://brew.sh/index_no.html)
```
brew install python3
```
It's important to remember that when it's installed through homebrew you replace the `python` command with `python3` and `pip` with `pip3`

## How to use
```bash
git clone https://github.com/sigvartmh/ITLscraper
cd ITLscraper
pip install -r requirements.txt
python itl_scrape.py
```
## If you want GUI
```
git clone https://github.com/sigvartmh/ITLscraper
cd ITLscraper
pip install -r requirements.txt
python app.py
```

## If pip install fails try
```
sudo pip install -r requirements.txt
```
Scrapes every course you have taken that is not deleted except community courses.
