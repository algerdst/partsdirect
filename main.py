import json
import time

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import csv

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 YaBrowser/24.1.0.0 Safari/537.36'
}

url = input('Введите ссылку')
#


def find_count_pages():
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    try:
        pages = soup.find('div', class_='pages').find_all('li')[-2].text
    except:
        pages = 1
    category = soup.find('h1').text
    return (pages, category)


def find_elems(pages, url, category):
    items = {}
    count = 0
    print('[+][+][+]ПОИСК ТОВАРОВ ПО ССЫЛКЕ[+][+][+]')
    for page in range(1, pages+1):
        if page == 1:
            link = url
        else:
            link = f"{url}?p={page}"
        response = requests.get(link, headers=headers)
        soup = BeautifulSoup(response.text, 'lxml')
        blocks = soup.find_all('tr')
        for block in blocks:
            article = block.find('td').find('a').text.replace('\n', '').strip()
            item_link = 'https://www.partsdirect.ru' + block.findAll('td')[1].find('a')['href']
            price = block.find('div', class_='prices').find('span').text.replace('\n', '').strip().replace(' ', '')
            items[article] = (item_link, price, category)
            count += 1
            print(f'НАЙДЕНО ТОВАРОВ {count}')
    print('[+][+][+]СБОР ИНФОРМАЦИИ О ТОВАРАХ[+][+][+]')

    with webdriver.Chrome() as browser:
        added_count = 0
        for item in list(items):
            chars = {
                'размер, мм': '-',
                'комплект, шт.': '-',
                'тип': '-',
                'особенности': '-',
            }
            compatibility = ''
            browser.get(items[item][0])
            # browser.execute_script(
            #     "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
            # browser.execute_script("window.scrollTo(0, 10);")

            characteristics_table_rows = browser.find_element(By.ID, 'characteristics').find_element(By.TAG_NAME,
                                                                                                     'table').find_elements(
                By.TAG_NAME, 'tr')
            for row in characteristics_table_rows:
                td = row.find_elements(By.TAG_NAME, 'td')
                try:
                    for char in list(chars):
                        if td[0].text == char:
                            chars[char] = td[1].text
                            break
                except:
                    continue
            try:
                compatibility_button = browser.find_element(By.CSS_SELECTOR, 'div.show-more').find_element(By.TAG_NAME,
                                                                                                           'a')
                ActionChains(browser).move_to_element(compatibility_button).click(compatibility_button).perform()

                time.sleep(1.5)
            except:
                pass
            try:
                compatible_block_lis = browser.find_element(By.ID, 'compatibles').find_elements(
                    By.TAG_NAME, 'li')
                for li in compatible_block_lis:
                    compatibility += li.text + ', '
            except:
                pass
            category = items[item][2]
            item_name = browser.find_element(By.TAG_NAME, 'h1').text
            price = items[item][1]
            size = chars['размер, мм']
            kit = chars['комплект, шт.']
            item_type = chars['тип']
            features = chars['особенности']
            compatibility = compatibility.replace(';', ':')
            with open('Результат.json', 'r', encoding='utf-8') as file:
                json_dict = json.load(file)
            json_dict['data'].append(
                {
                    'Категория': category,
                    'Товар': item_name,
                    'Цена': price,
                    'Размер': size,
                    'Комплект шт.': kit,
                    'Особенности': features,
                    'Тип': item_type,
                    'Подходит к моделям': compatibility,
                }
            )
            added_count += 1
            print(f'ОСТАЛОСЬ СОБРАТЬ {count - added_count} ТОВАРОВ')
            with open('Результат.json', 'w', encoding='utf-8') as file:
                json.dump(json_dict, file, indent=4, ensure_ascii=False)


pages_category = find_count_pages()
pages = int(pages_category[0])
category = pages_category[1]

with open('Результат.json', 'w', encoding='utf-8') as file:
    json.dump({'data': []}, file, indent=4, ensure_ascii=False)

find_elems(pages, url, category)
