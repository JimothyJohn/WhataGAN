#!/usr/bin/python
from io import BytesIO
import requests     # HTTP requests
import shutil
import os
from time import sleep
from bs4 import BeautifulSoup

HOMEPAGE = "https://artvee.com/?per_page=100"
ABSTRACTPAGE = "https://artvee.com/c/abstract/?per_page=100"

key = os.environ.get("STREETVIEW_API_KEY")


def SaveStreetView(filename, params):
    rootURL = "https://maps.googleapis.com/maps/api/streetview"
    params["key"] = key,

    res = requests.get(rootURL, params=params, stream=True)
    sleep(0.2)

    if res.status_code == 200:
        with open(f"{filename}", 'wb') as f:
            shutil.copyfileobj(res.raw, f)
            f.close()
    else:
        print('Image Couldn\'t be retrieved')


def getPage(url):
    ''' returns a soup object that contains all the information
    of a certain webpage'''
    result = requests.get(url)
    sleep(0.2)
    content = result.content
    return BeautifulSoup(content, "html.parser")
