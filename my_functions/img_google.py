from bs4 import BeautifulSoup
import json
from io import BytesIO
import requests
import urllib
from urllib.request import urlopen
import urllib.parse
from PIL import Image
import pdb


def get_soup(url):
    page = requests.get(url).text
    return BeautifulSoup(page, 'html.parser')


def get_tk_img(query):
    query = urllib.parse.quote(query, safe='')
    url = "https://www.google.co.in/search?q=" + query + "&source=lnms&tbm=isch"
    soup = get_soup(url)
    for a in soup.find_all("img"):
        my_url = a.get('src')
        if my_url:
            if "http" in my_url and my_url:
                u = urlopen(my_url)
                a = u.read()
                u.close()
                im = Image.open(BytesIO(a))
                return im


if __name__ == "__main__":
    print('hi')
