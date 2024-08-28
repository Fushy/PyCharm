from time import sleep

import requests


def get_html_page(url):
    page_html = requests.get(url)
    while page_html.status_code != 200:
        print("page_html.status_code != 200 :", page_html.status_code)
        sleep(30)
        page_html = requests.get(url)
    return page_html
