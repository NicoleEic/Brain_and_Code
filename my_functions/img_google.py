from bs4 import BeautifulSoup
import json
import urllib2
from io import BytesIO
import urllib
from PIL import Image


def get_soup(url, header):
    return BeautifulSoup(urllib2.urlopen(urllib2.Request(url, headers=header)), 'html.parser')


def get_tk_img(query):
    query = query.split()
    query = '+'.join(query)

    url = "https://www.google.co.in/search?q=" + query + "&source=lnms&tbm=isch"
    header = {'User-Agent':"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"
    }
    soup = get_soup(url, header)

    for a in soup.find_all("div",{"class":"rg_meta"}):
        link , Type =json.loads(a.text)["ou"]  ,json.loads(a.text)["ity"]
        if Type == 'jpg' or  Type == 'png':
            my_url = str(link)
            break
    u = urllib.urlopen(my_url)
    raw_data = u.read()
    u.close()
    im = Image.open(BytesIO(raw_data))
    return im


if __name__ == "__main__":
    print 'hi'
