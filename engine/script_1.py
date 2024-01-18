import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import datetime
import os
import xlsxwriter
import PySimpleGUI as sg
import time
from datetime import date
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
                       "Sub_category_1":[],
                       "Sub_category_2":[]}
df_vendors = pd.DataFrame(vendor_dict)

# данные запроса браузера
timeout = 10
headers = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

##### БЛОК ФУНКЦИЙ #####

def get_html(url):
    while True:
        try:
            req = requests.get(url= url, headers=headers, timeout=timeout)
            return req.text if req.status_code == 200 else False
        except Exception:
            #return False
            continue

#####

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

#####
##### БЛОК ФУНКЦИЙ ##### 

# исходный сайт, который будем парсить( продумать запуск inputom)

req = get_html('https://tula.elfgroup.ru/#/tab-catalog-overview')
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
                sub_section_ref = URL + item.find('a').get('href')#, class_='sub-sections__title '
                sub_category_dict[sub_category_name]=sub_section_ref
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
        vendor_count = 0
        req = get_html(sub_category_ref) #requests.get(sub_category_ref, headers=headers, timeout=timeout).text
        sub_cat_soup = BeautifulSoup(req, 'lxml')
        sub_section_div = None #sub_cat_soup.find('div', class_ = 'sub-sections__container')
        if sub_section_div is not None:
            name_sect = sub_cat_soup.find_all('div', class_ = 'sub-sections__item')
            #print(f'{sub_category_name} : {len(name_sect)} категорий')
            sub_section_dict = {}
            for item in name_sect:
                item_href =URL + item.find('a').get('href')
                item_name = item.text.strip()
                sub_section_dict[item_name] = item_href
            for sub_section_name, sub_section_ref in sub_section_dict.items():
                req = get_html(sub_section_ref)
                sub_cat_soup = BeautifulSoup(req, 'lxml')
                page_count = check_page_count(sub_cat_soup, 'maximaster-nav-string')
                if page_count == None:
                    vendor_table = sub_cat_soup.find('table', class_ = 'products-list')
                    vendor_list = vendor_table.find_all('tr', class_ = 'products-list-item')
                    loc_index_df(vendor_list)

                else:
                    current_page = 1
                                
                    while current_page <= int(page_count):
                                    
                        vendor_table = sub_cat_soup.find('table', class_ = 'products-list')
                        vendor_list = vendor_table.find_all('tr', class_ = 'products-list-item')
                        loc_index_df(vendor_list)
                        sub_section_ref = f'{sub_section_ref}?&PAGEN_1={current_page}'
                        req = get_html(sub_section_ref)
                        sub_cat_soup = BeautifulSoup(req, 'lxml')

            sub_section_dict.clear()
        else:
            sub_section_name = ''
            #print(f'{sub_category_name} не имеет подкатегорий')
            page_count = check_page_count(sub_cat_soup, 'maximaster-nav-string')
            if page_count == None:
                vendor_table = sub_cat_soup.find('table', class_ = 'products-list')
                vendor_list = vendor_table.find_all('tr', class_ = 'products-list-item')
                #loc_index_df(vendor_list)
                for item in vendor_list:
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
                print(f'В категории {category_name}: {sub_category_name} собрано {vendor_count} позиций(ии)')
            else:
                current_page = 1
                
                while current_page <= int(page_count):
                    
                    vendor_table = sub_cat_soup.find('table', class_ = 'products-list')
                    vendor_list = vendor_table.find_all('tr', class_ = 'products-list-item')
                    #loc_index_df(vendor_list)
                    for item in vendor_list:
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
                    current_page +=1
                    sub_category_ref = f'{sub_category_ref}?&PAGEN_1={current_page}'
                    req = get_html(sub_category_ref)
                    sub_cat_soup = BeautifulSoup(req, 'lxml')
                    print(f'В категории {category_name}: {sub_category_name} собрано {vendor_count} позиций(ии)')
                    #https://tula.elfgroup.ru/catalog/zapornaya-i-reguliruyushchaya-armutura/krany/
                    #https://tula.elfgroup.ru/catalog/zapornaya-i-reguliruyushchaya-armutura/krany/?&PAGEN_1=2

    category_number += 1
    
current_date = date.today()
json_vendor = df_vendors.to_json(orient="table")

with open("Data/ELF.json", "w", encoding = "utf-8") as file:
    file.write(json_vendor)
    
sheet_name = 'Sheet_1'

with pd.ExcelWriter(
        f"Data/Output/ELF_{current_date}.xlsx",
        engine="xlsxwriter",
        mode='w') as writer:

    df_vendors.to_excel(writer, sheet_name=sheet_name, index=False)
    workbook = writer.book
    link_format = workbook.add_format({  # type: ignore
                            'font_color': 'blue',
                            'underline': 1,
                            'valign': 'top',
                            'text_wrap': True,
                        })
    writer.sheets[sheet_name].set_column('D:D', None, link_format)


end_time = time.time()  # время окончания выполнения
execution_time = end_time - start_time  # вычисляем время выполнения
print("Сбор данных завершен")
print(f"Время выполнения программы: {execution_time} секунд")
time.sleep(3)
