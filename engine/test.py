import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
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


list = ['1', '2', '3, 2', '4']
elt =str(list[len(list)-2:-1])
print(elt)
print(elt.find('2'))

# ['3, 2']


URL = "https://tula.elfgroup.ru"
timeout = 10
headers = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

vendor_dict = {"Vendor":[],
                       "Nomination":[],
                       "Price":[],
                       "Reference":[],
                       "Category_Name":[],
                       "Sub_category_1":[],
                       "Sub_category_2":[]}
df_vendors = pd.DataFrame(vendor_dict)

def get_html(url):
    while True:
        try:
            req = requests.get(url= url, headers=headers, timeout=timeout)
            return req.text if req.status_code == 200 else False
        except Exception:
            #return False
            continue

def check_page_count(soup, tag_class):
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

def create_tag_list(soup, tag, class_tag):
    return soup.find_all (tag, class_ = class_tag)

def loc_index_df(list):
    vendor_count = 0
    for item in list:
        vendor_href =URL + item.find('td', class_ = 'products-list-item-info').find('div', class_ = 'products-list-item-title').find('div', class_ = 'products-list-item-name').find('a').get('href')
        vendor_name = item.find('div', class_ = 'products-list-item-name').find('a').text.strip()
        vendor = item.find('div', class_ = 'code-container').text.strip()
        if vendor.find('\n') != -1:
            vendor = vendor[:vendor.find('\n')]
        vendor_req = get_html(vendor_href) #requests.get(vendor_href, headers=headers, timeout=timeout).text
        vendor_soup = BeautifulSoup(vendor_req, 'lxml')
        vendor_price = vendor_soup.find('div', class_ = 'd-none').find('meta', {'itemprop':'price'}).get('content')
        if vendor_price != '':
            vendor_price = float(vendor_price)
        df_vendors.loc[len(df_vendors.index)]=[vendor, vendor_name, vendor_price, vendor_href, category_name, sub_category_name, sub_section_name]
        vendor_count += 1
    print(df_vendors)
    print(f'В категории {category_name}: {sub_category_name}, {sub_section_name} собрано {vendor_count} позиций(ии)')



category_name = 'Трубопроводная арматура'
sub_category_name = "Шаровые краны"
sub_section_href = 'https://tula.elfgroup.ru/catalog/zapornaya-i-reguliruyushchaya-armutura/krany/'
req = get_html(sub_section_href) #requests.get(sub_category_ref, headers=headers, timeout=timeout).text
sub_cat_soup = BeautifulSoup(req, 'lxml')
sub_section_div = sub_cat_soup.find('div', class_ = 'sub-sections__container')
if sub_section_div is not None:
    name_sect = sub_cat_soup.find_all('div', class_ = 'sub-sections__item')
            #print(f'{sub_category_name} : {len(name_sect)} категорий')
    sub_section_dict = {}
    for item in name_sect:
        item_href =URL + item.find('a').get('href')
        item_name = item.text.strip()
        sub_section_dict[item_name] = item_href

print(sub_section_dict)

for sub_section_name, sub_section_href in sub_section_dict.items():
    req = get_html(sub_section_href)
    sub_cat_soup = BeautifulSoup(req, 'lxml')
    page_count = check_page_count(sub_cat_soup, 'maximaster-nav-string')
    if page_count == None:
        vendor_table = sub_cat_soup.find('table', class_ = 'products-list')
        vendor_list = vendor_table.find_all('tr', class_ = 'products-list-item')
        loc_index_df(vendor_list)
        #### 
        """for item in vendor_list:
            vendor_href =URL + item.find('td', class_ = 'products-list-item-info').find('div', class_ = 'products-list-item-title').find('div', class_ = 'products-list-item-name').find('a').get('href')
            vendor_name = item.find('div', class_ = 'products-list-item-name').find('a').text.strip()
            vendor = item.find('div', class_ = 'code-container').text.strip()
            if vendor.find('\n') != -1:
                vendor = vendor[:vendor.find('\n')]
            vendor_req = get_html(vendor_href) #requests.get(vendor_href, headers=headers, timeout=timeout).text
            vendor_soup = BeautifulSoup(vendor_req, 'lxml')
            vendor_price = float(vendor_soup.find('div', class_ = 'd-none').find('meta', {'itemprop':'price'}).get('content'))
            df_vendors.loc[len(df_vendors.index)]=[vendor, vendor_name, vendor_price, vendor_href, category_name, sub_category_name]
            vendor_count += 1
            print(df_vendors)
            print(f'В категории {category_name}: {sub_category_name} собрано {vendor_count} позиций(ии)')"""
    else:
        current_page = 1
                    
        while current_page <= int(page_count):
                        
            vendor_table = sub_cat_soup.find('table', class_ = 'products-list')
            vendor_list = vendor_table.find_all('tr', class_ = 'products-list-item')
            loc_index_df(vendor_list)
            ###

            current_page +=1
            sub_section_href = f'{sub_section_href}?&PAGEN_1={current_page}'
            req = get_html(sub_section_href)
            sub_cat_soup = BeautifulSoup(req, 'lxml')
sub_section_dict.clear()
print(df_vendors)
            # https://tula.elfgroup.ru/catalog/zapornaya-i-reguliruyushchaya-armutura/krany/krany-sharovye-latunnye/
            # https://tula.elfgroup.ru/catalog/zapornaya-i-reguliruyushchaya-armutura/krany/krany-sharovye-latunnye/?&PAGEN_1=2    

""" a = 'ТТ000018531'
index = a.find(" ")
print(a[:a.find(" ")])
 """
""" timeout = 10
headers = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

URL = 'https://tula.elfgroup.ru/'
sub_category_href = 'https://tula.elfgroup.ru/catalog/zapornaya-i-reguliruyushchaya-armutura/krany/krany-sharovye-latunnye/'

vendor_href = 'https://tula.elfgroup.ru/catalog/vodonagrevateli/bojlery-kosvennogo-nagreva/vodonagrevatel-kosvennyj-hajdu-aq-ind-fc-75-l-nastennyj/'
vendor_req = requests.get(vendor_href, headers=headers, timeout=timeout).text
with open('Data/index_1.html', 'w', encoding= 'utf-8') as file:
    file.write(vendor_req) 
vendor_soup = BeautifulSoup(vendor_req, 'lxml')
vendor_price = float(vendor_soup.find('div', class_ = 'd-none').find('meta', {'itemprop':'price'}).get('content'))
print(vendor_price)

def check_and_create_page_count(soup, tag_class):
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


