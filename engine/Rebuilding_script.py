from bs4 import BeautifulSoup
import requests
import json
import pandas as pd
import datetime as dt 
import os
import xlsxwriter
import time

start_time = time.time()
cur_dir = os.getcwd()
data_dir = '\\'.join([os.getcwd(), 'Data'])
URL = 'https://tula.elfgroup.ru'
URL_catalog = "https://tula.elfgroup.ru/catalog"
#cur_dir = r'C:/Users/vorotintsev/Desktop/Parser_ELF'

# инициализиер DF для записи итогового списка артикулов
vendor_dict = {
    "Vendor":[],
    "Nomination":[],
    "Price":[],
    "Reference":[],
    "Category_Name":[],
    "Sub_category_1":[],
    "Sub_category_2":[]
    }
df_vendors = pd.DataFrame(vendor_dict)

# данные запроса браузера
timeout = 10
headers = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

#   ************* FUNCTIONS BLOCK ****************

# функция для извлечения кода запрашиваемого страницы
def get_html(url):
    while True:
        try:
            req = requests.get(url= url, headers=headers, timeout=timeout)
            return req.text if req.status_code == 200 else False
        except Exception:
            #return False
            continue

# функция создающая словарь категорий
def create_and_write_categories_dict(class_tag, name_dict, cat_list, url):
    for item in cat_list:
        if class_tag:
            item_href = url + item.find('a', class_ = class_tag).get('href')
            item_name = item.find('a', class_ = class_tag).get_text().strip()
            if item_name != 'Последние поступления':
                name_dict[item_name] = item_href
        else:
            item_href = url + item.find('a').get('href')
            item_name = item.find('a').get_text().strip()
            if item_name != 'Последние поступления':
                name_dict[item_name] = item_href

# функция сбора списка тэгов
def create_tag_list(soup, tag, class_tag):
    result = soup.find_all (tag, class_ = class_tag)
    if result:
        return result
    else:
        return False

# Функция проверяет существует ли папка с указанным именем, если нет, создает новую
def check_and_create_folder(name_dir, cur_dir):
    if os.path.isdir(f'C:\\Users\\vorotintsev\\Desktop\\Parser_ELF\\Data\\Sub_categories\\{name_dir}') == False:
        dir_and_file_name = 'Sub_categories\\' + name_dir
        path = os.path.join(cur_dir, dir_and_file_name)
        os.mkdir(path)


# Функция проверки количества елементо Pager'a
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

# Функция 
def loc_index_df(list, category_name, sub_category_name, sub_section_name):
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


#   ************* FUNCTIONS BLOCK ****************

#   ************* MAIN BLOCK *************

# получаем исходный код запрашиваемой страницы
# записываем данные в файл .json
# собираем список div-контейнеров, содержащих ссылки на категории
# создаем словарь "категория: ссылка", записываем в файл .json
# Получение списка/словаря ссылок на подкатегорий, записываем в файл .json
    # Проверка существования подкатегории_1
# Перебор циклом ссылок словаря подкатегорий или подкатегории_1
# Получение ссылок Pager'a
# Перебор страниц с записью в файл .json
# Получение списка [Артикул, Номенклатура, Цена, Ссылка, Категория, Подкатегория_1, Подкатегория_2]

# получаем исходный код запрашиваемой страницы
req = get_html(URL_catalog)
src = req
index_file_path = '\\'.join([data_dir, 'index_1.html'])

# записываем данные в файл .json
with open(index_file_path, 'w', encoding= 'utf-8') as file:
    file.write(src)
with open(index_file_path, encoding='utf-8') as file:
    src = file.read()

# собираем список div-контейнеров, содержащих ссылки на категории
soup = BeautifulSoup(src, 'lxml')
category_list = create_tag_list(soup, 'div', 'main-sections__wrapper')

# создаем словарь "категория: ссылка", записываем в файл .json
category_dict={}
create_and_write_categories_dict(0, name_dict=category_dict, cat_list=category_list, url=URL)
category_dict_path = '\\'.join([data_dir, 'all_categories_dict_1.json'])
with open(category_dict_path, 'w', encoding='utf-8') as file:
    json.dump(category_dict, file, indent=4, ensure_ascii= False)
# инициализируем словарь категорий из файла .json
with open(category_dict_path, encoding='utf-8') as file:
    category_dict = json.load(file)

# Получение списка/словаря ссылок на подкатегории из category_dict
count_sub_categories = 1
for item in category_list:
    item_name = item.find('a').text.strip()
    
    # Инициируем объект BS из item, путем преобразования в текст 
    soup_cat = BeautifulSoup(str(item), 'lxml')
    sub_category_list = create_tag_list(soup_cat, 'div', 'sub-sections__item')
    
    # создаем словарь подкатегорий
    sub_category_dict = {}
    create_and_write_categories_dict( 'sub-sections__title', sub_category_dict, sub_category_list, URL)
    
    # проверка существования папки
    check_and_create_folder(f'{count_sub_categories}_{item_name}', data_dir)
    sub_category_path = '\\'.join([data_dir, 'Sub_categories', f'{count_sub_categories}_{item_name}', f'{item_name}_категории.json'])
    
    # запись в файл .json в подпаку SUB_CATEGORIES
    with open(sub_category_path, 'w', encoding='utf-8') as file:
        json.dump(sub_category_dict, file, indent=4, ensure_ascii=False)
    count_sub_categories += 1

count_vendor = 1
count_sub_categories = 1
for key in category_dict:
    sub_category_path = '\\'.join([data_dir, 'Sub_categories', f'{count_sub_categories}_{key}', f'{key}_категории.json'])
    with open(sub_category_path, encoding='utf-8') as file:
        sub_category_dict = json.load(file)
    for item_name, item_ref in sub_category_dict.items():
        req = get_html(item_ref)
        soup = BeautifulSoup(req, 'lxml')
        page_count = check_page_count(soup, 'maximaster-nav-string')
        if page_count:
            print('-')
        else:
            vendor_list = create_tag_list(soup, 'tr', 'products-list-item')
            loc_index_df(vendor_list, key, item_name, None)
            print(df_vendors)
        print(f'в категории {key}, подкатегории {item_name} отобрано {page_count} страниц(ы)')
    count_sub_categories += 1


""" 
# Перебор циклом словаря категорий
for item_name, item_ref in category_dict.items():
    req = get_html(item_ref)
    soup = BeautifulSoup(req, 'lxml')
    sub_category_list = create_tag_list(soup, 'div', 'sub-sections__item')
    sub_category_dict = {}
    create_and_write_categories_dict(sub_category_dict, sub_category_list, URL)
    sub_category_dict_path = '\\'.join([data_dir, 'Sub_categories', 'all_categories_dict.json'])
    with open(sub_category_dict_path, 'w', encoding='utf-8') as file:
        file.write(sub_category_dict)
"""

#   ************* MAIN BLOCK *************

#   ************* TEST ****************

#print(category_dict)

#   ************* TEST ****************
