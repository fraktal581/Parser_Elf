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

start_time = time.time()
cur_dir = r'C:/Users/vorotintsev/Desktop/Parser_ELF'
URL = "https://tula.elfgroup.ru"

# данные запроса браузера
timeout = 5
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
    if os.path.isdir(f'C:/Users/vorotintsev/Desktop/PYTHON_parser/Data/Sub_categories/{name_dir}') == False:
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
        for item in sub_category_div:
            sub_category_name = item.text.strip()#, class_='sub-sections__title '
            sub_category_ref = URL + item.find('a').get('href')#, class_='sub-sections__title '
            sub_category_dict[sub_category_name]=sub_category_ref
            with open(f'Data/Sub_categories/{category_count}_{category_name}/{category_name}_sub_categories.json', 'w', encoding= 'utf-8') as file:
                json.dump(sub_category_dict, file, indent = 4, ensure_ascii=False)
            with open(f'Data/Sub_categories/{category_count}_{category_name}/{category_name}_sub_categories.json', encoding= 'utf-8') as file:
                sub_category_dict = json.load(file)
            print(f'{sub_category_name}: {sub_category_ref}')    
    category_count += 1      
"""         category_req = requests.get(url= category_href, headers=headers, timeout=timeout)
        src = req.text """
        
""" all_categories_dict = {}
for item in all_categories_div:
    item_href = URL + item.find('div', class_ = 'catalog-overview-list-item-title').find('a').get('href')
    item_name = item.find('div', class_ = 'catalog-overview-list-item-title').text.strip()
    if item_name != 'Последние поступления':
        all_categories_dict[item_name] = item_href
        
with open('Data/all_categories_dict.json', 'w', encoding= 'utf-8') as file:
    json.dump(all_categories_dict, file, indent=4, ensure_ascii= False) """

#print(soup)






#time.sleep(5)
end_time = time.time()
execution_time = start_time - end_time
print(execution_time)