import requests
from bs4 import BeautifulSoup
import json
import pandas
import datetime
import os
import xlsxwriter
import PySimpleGUI as sg
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

timeout = 10
headers = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

URL = 'https://tula.elfgroup.ru/'
sub_category_href = 'https://tula.elfgroup.ru/catalog/zapornaya-i-reguliruyushchaya-armutura/krany/krany-sharovye-latunnye/'

vendor_href = 'https://tula.elfgroup.ru/catalog/vodonagrevateli/bojlery-kosvennogo-nagreva/vodonagrevatel-kosvennyj-hajdu-aq-ind-fc-75-l-nastennyj/'
vendor_req = requests.get(vendor_href, headers=headers, timeout=timeout).text
""" with open('Data/index_1.html', 'w', encoding= 'utf-8') as file:
    file.write(vendor_req) """
vendor_soup = BeautifulSoup(vendor_req, 'lxml')
vendor_price = float(vendor_soup.find('div', class_ = 'd-none').find('meta', {'itemprop':'price'}).get('content'))
print(vendor_price)

""" def check_and_create_page_count(soup, tag_class):
    if soup.find("div", class_ = tag_class) != None:
        count_pages = soup.find("div", class_ = tag_class).find_all('a', class_ = '')
        page_list = []
        for item in count_pages:
            page_text = item.text.strip()
            if page_text != '': 
                page_list.append(page_text)
        return page_list[-1]
    else:
        return None

req = requests.get("https://tula.elfgroup.ru/catalog/izmeritelnye-pribory/termometry/", timeout=3).text
sub_cat_soup = BeautifulSoup(req, 'lxml')
page_count = check_and_create_page_count(sub_cat_soup, 'maximaster-nav-string') """
#print(page_count)


