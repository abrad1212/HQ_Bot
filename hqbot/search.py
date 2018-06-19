import time
#from multiprocessing import Pool

import urllib.request as urllib
import requests
#from bs4 import BeautifulSoup

from google import google

"""try:
    from question import split
except ImportError:
    from .question import split"""


def get_page(link):
    """Get a webpage

    Arguments:
        link {string} -- The website to read the HTML from.

    Returns:
        Bytes -- The HTML retrieved from the link
    """
    if link.find('mailto') != -1:
        return ''

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'}
    #req = urllib.Request(link, headers=headers)
    #return urllib.urlopen(req).read()

    r = requests.get(link, headers=headers, timeout=2)
    if r.status_code == 200:
        return r.text
    else:
        return None


def get_links(options):
    links = []

    for option in options:
        option = option.lower() + " wiki"

        search_wiki = google.search(option, pages=1)
        link = search_wiki[0].link
        links.append(link)


def get_link(option):
    s_time = time.time()

    option = option.lower()
    option += " wiki"
    search_wiki = google.search(option, pages=1)

    print("{} Elapsed Time: {}".format(option, time.time() - s_time))

    link = search_wiki[0].link
    return link
