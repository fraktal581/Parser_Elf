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

start_time = time.time()
cur_dir = r'C:/Users/vorotintsev/Desktop/Parser_ELF'
URL = "https://tula.elfgroup.ru"

vendor_dict = {"Vendor":[],
                       "Nomination":[],
                       "Price":[],
                       "Reference":[],
                       "Category_Name":[],
                       "Sub_category_1":[]}
df_vendors = pd.DataFrame(vendor_dict)
# данные запроса браузера
timeout = 10
headers = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

##### БЛОК ФУНКЦИЙ #####

def create_and_write_all_categories_dict(name_dict, cat_list, url, div_class):
    for item in cat_list:
        item_href = url + item.find('div', class_ = div_class).find('a').get('href')
        item_name = item.find('div', class_ = div_class).text.strip()
        if item_name != 'Последние поступления':
            name_dict[item_name] = item_href

#####

def check_and_create_folder(name_dir, cur_dir):
    if os.path.isdir(f'C:/Users/vorotintsev/Desktop/Parser_ELF/Data/Sub_categories/{name_dir}') == False:
        dir_and_file_name = 'Data/Sub_categories/' + name_dir
        path = os.path.join(cur_dir, dir_and_file_name)
        os.mkdir(path)

#####

def create_soup_tag_list(url_ref, tag, class_tag):
    req = requests.get(url=url_ref, headers=headers, timeout=timeout)
    src = req.text
    soup = BeautifulSoup(src, 'lxml')
    return soup.find_all(tag, class_ = class_tag)

#####

def create_tag_list(soup, tag, class_tag):
    return soup.find_all (tag, class_ = class_tag)

#####

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

#####
##### БЛОК ФУНКЦИЙ ##### 

# исходный сайт, который будем парсить( продумать запуск inputom)
req = requests.get('https://tula.elfgroup.ru/#/tab-catalog-overview', timeout= timeout).text
src = req

with open('Data/index.html', 'w', encoding= 'utf-8') as file:
    file.write(src)
with open('Data/index.html', encoding='utf-8') as file:
    src = file.read()

soup = BeautifulSoup(src, 'lxml')
catalog_block = soup.find('div', class_ = 'catalog-overview-list')

all_categories_div = create_tag_list(catalog_block, 'div', 'catalog-overview-list-item')
#all_categories_div = catalog_block.find_all('div', class_ = 'catalog-overview-list-item')

all_categories_div_class = 'catalog-overview-list-item-title'
all_categories_dict = {}
create_and_write_all_categories_dict(all_categories_dict, all_categories_div, URL, all_categories_div_class)

with open('Data/all_categories_dict.json', 'w', encoding= 'utf-8') as file:
    json.dump(all_categories_dict, file, indent=4, ensure_ascii= False)
with open('Data/all_categories_dict.json', encoding='utf-8') as file:
    all_categories_dict = json.load(file)

category_count = 0
for category_name, category_href in all_categories_dict.items():
    if category_count <= len(all_categories_dict):
        sub_category_div = create_soup_tag_list(category_href, 'div', 'sub-sections__item')
        check_and_create_folder(f'{category_count}_{category_name}', cur_dir)
        #sub_category_div = soup.find_all('div', class_ = 'sub-sections__container')
        sub_category_dict = {}
        if len(sub_category_div) == 0:
                sub_category_dict[category_name] = category_href
        else:
            for item in sub_category_div:
                sub_category_name = item.text.strip()#, class_='sub-sections__title '
                sub_category_ref = URL + item.find('a').get('href')#, class_='sub-sections__title '
                sub_category_dict[sub_category_name]=sub_category_ref
        with open(f'Data/Sub_categories/{category_count}_{category_name}/{category_name}_sub_categories.json', 'w', encoding= 'utf-8') as file:
            json.dump(sub_category_dict, file, indent = 4, ensure_ascii=False)
        #with open(f'Data/Sub_categories/{category_count}_{category_name}/{category_name}_sub_categories.json', encoding= 'utf-8') as file:
            #sub_category_dict = json.load(file)
            #print(f'{sub_category_name}: {sub_category_ref}')    
    category_count += 1 
category_number = 0
for category_name in all_categories_dict.keys():
    with open(f'Data/Sub_categories/{category_number}_{category_name}/{category_name}_sub_categories.json', encoding= 'utf-8') as file:
        sub_category_dict = json.load(file)
    for sub_category_name, sub_category_ref in sub_category_dict.items():
        req = requests.get(sub_category_ref, headers=headers, timeout=timeout).text
        sub_cat_soup = BeautifulSoup(req, 'lxml')
        sub_section_div = sub_cat_soup.find('div', class_ = 'sub-sections__container')
        if sub_section_div is not None:
            name_sect = sub_cat_soup.find_all('div', class_ = 'sub-sections__item')
            #print(f'{sub_category_name} : {len(name_sect)} категорий')
            
        else:
            #print(f'{sub_category_name} не имеет подкатегорий')
            page_count = check_page_count(sub_cat_soup, 'maximaster-nav-string')
            if page_count == None:
                vendor_table = sub_cat_soup.find('table', class_ = 'products-list')
                vendor_list = vendor_table.find_all('tr', class_ = 'products-list-item')
                vendor_count = 0
                for item in vendor_list:
                    vendor_href =URL + item.find('td', class_ = 'products-list-item-info').find('div', class_ = 'products-list-item-title').find('div', class_ = 'products-list-item-name').find('a').get('href')
                    vendor_name = item.find('div', class_ = 'products-list-item-name').find('a').text.strip()
                    vendor = item.find('div', class_ = 'code-container').text.strip()
                    vendor_req = requests.get(vendor_href, headers=headers, timeout=timeout).text
                    vendor_soup = BeautifulSoup(vendor_req, 'lxml')
                    vendor_price = float(vendor_soup.find('div', class_ = 'd-none').find('meta', {'itemprop':'price'}).get('content'))
                    df_vendors.loc[len(df_vendors.index)]=[vendor, vendor_name, vendor_price, vendor_href, category_name, sub_category_name]
                    vendor_count += 1
                    print(df_vendors)
                print(f'В категории {category_name}: {sub_category_name} собрано {vendor_count} позиций(ии)')
            else:
                current_page = 1
                
                while current_page <= int(page_count):
                    
                    vendor_count = 0
                    vendor_table = sub_cat_soup.find('table', class_ = 'products-list')
                    vendor_list = vendor_table.find_all('tr', class_ = 'products-list-item')
                    for item in vendor_list:
                        vendor_href =URL + item.find('td', class_ = 'products-list-item-info').find('div', class_ = 'products-list-item-title').find('div', class_ = 'products-list-item-name').find('a').get('href')
                        vendor_name = item.find('div', class_ = 'products-list-item-name').find('a').text.strip()
                        vendor = item.find('div', class_ = 'code-container').text.strip()
                        vendor_req = requests.get(vendor_href, headers=headers, timeout=timeout).text
                        vendor_soup = BeautifulSoup(vendor_req, 'lxml')
                        vendor_price = float(vendor_soup.find('div', class_ = 'd-none').find('meta', {'itemprop':'price'}).get('content'))
                        df_vendors.loc[len(df_vendors.index)]=[vendor, vendor_name, vendor_price, vendor_href, category_name, sub_category_name]
                        vendor_count += 1
                        print(df_vendors)
                    current_page +=1
                    sub_category_ref = f'{sub_category_ref}?&PAGEN_1={current_page}'
                    req = requests.get(sub_category_ref, headers=headers, timeout=timeout).text
                    sub_cat_soup = BeautifulSoup(req, 'lxml')
                print(f'В категории {category_name}: {sub_category_name} собрано {vendor_count} позиций(ии)')
                    #https://tula.elfgroup.ru/catalog/zapornaya-i-reguliruyushchaya-armutura/krany/
                    #https://tula.elfgroup.ru/catalog/zapornaya-i-reguliruyushchaya-armutura/krany/?&PAGEN_1=2

    category_number += 1







#time.sleep(5)
end_time = time.time()
execution_time = start_time - end_time
print(execution_time)