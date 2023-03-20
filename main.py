import requests
from bs4 import BeautifulSoup
from time import sleep
from random import randint
from config import cookies
import pandas as pd
import json
from pars import pars_links, pars_blocks, pars_apartments

url = 'https://www.avito.ru/voronezh/kvartiry/prodam/novostroyka-ASgBAgICAkSSA8YQ5geOUg'
# Для тренировки парсил только новостройки в Воронеже и однокомнатные.
# Сейчас поучусь так, позже сделаю через несколько IP и в многопроцессорности.

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/111.0',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
    'Connection': 'keep-alive',
    'Referer': 'https://www.avito.ru/voronezh/kvartiry/prodam/1-komnatnye/novostroyka-ASgBAQICAkSSA8YQ5geOUgFAyggUgFk?p=1',
    # Ссылка сверху показывает с какой страницы мы перешли на текущею.
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
}
# При переходах по ссылкам не будет хватать заголовка 'If-None-Match', не знаю как его автоматизировать, он меняется.
# Т.к. в печеньках идут изменения от сылки к сылке, то решил пока не запариваться и с заголовком тоже.

params = {
    'p': '100',
}
# Т.к. у меня стоит фильтр Воронеж, новостройки однокомнатные то страниц не 100.
# Переходим на 100 страницу, чтоб узнать сколько страниц. Авито не всегда сразу показывает сколько страниц.


response = requests.get(url=url,
                        params=params,
                        cookies=cookies,
                        headers=headers, )
soup = BeautifulSoup(response.text, features='lxml')
max_page = int(soup.find_all('span', class_='pagination-item-JJq_j')[-2].text)  # Узнаём максимальный номер страницы

links, links_error = pars_links(url=url,
                                params=params,
                                headers=headers,
                                cookies=cookies,
                                max_page=max_page, )

for refer in links_error.keys():
    try:
        headers['Referer'] = refer
        links[refer] = []
        for link in links_error[refer]:
            sleep(randint(1, 4))
            panels = pars_blocks(url=link, cookies=cookies, headers=headers, params={})
            # Находим все блоки объявлений
            for panel in panels:
                link = 'https://www.avito.ru' + panel.find('a', class_='link-link-MbQDP').get('href')
                links[refer].append(link)
    except Exception as ex:
        print(ex)
# Дособираем все ссылки, если и повторно ошибка то что уж поделать

for refer in links.keys():
    links[refer] = list(set(links[refer]))  # Убрали все дубли

apartments_error = {}  # Для ошибок
df_apartments = pd.DataFrame()  # Общий датафрейм
for refer in links.keys():
    apartments_error[refer] = []
    headers['Referer'] = refer
    for link in links[refer]:
        sleep(randint(1, 4))
        try:
            df_apartment = pd.DataFrame(pars_apartments(link=link, headers=headers, cookies=cookies))
            df_apartments = pd.concat([df_apartments, df_apartment], ignore_index=True)
        except Exception as ex:
            print(ex)
            apartments_error[refer].append(link)
            # Снова фиксирую ошибки

with open('links_error.json', 'w') as file:  # Сохраняем в json то чно не получилось
    json.dump(apartments_error, file, ensure_ascii=False, indent=4)

df_apartments.to_csv('df_apartments.csv')  # Итоговый датафрейм
