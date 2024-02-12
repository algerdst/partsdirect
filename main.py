import requests
from bs4 import BeautifulSoup

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 YaBrowser/24.1.0.0 Safari/537.36'
}

url = 'https://www.partsdirect.ru/parts_washing_machines'


def find_count_pages():
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    pages = soup.find('div', class_='pages').find_all('li')[-2].text
    category = soup.find('h1').text
    return (pages, category)



def find_elems():
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    blocks = soup.find_all('tr')
    for block in blocks:
        article = block.find('td').find('a').text.replace('\n', '').strip()
        name = block.findAll('td')[1].find('a').text
        item_link = 'https://www.partsdirect.ru'+block.findAll('td')[1].find('a')['href']
        price=block.find('div', class_='prices').find('span').text.replace('\n', '').strip()

find_elems()