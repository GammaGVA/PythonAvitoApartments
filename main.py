import requests
from bs4 import BeautifulSoup
from config import cookies
from pars import requests_url, pars
import pandas as pd
import json

headers = {
    'authority': 'm.avito.ru',
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
    'content-type': 'application/json;charset=utf-8',
    'referer': 'https://m.avito.ru/voronezh/kvartiry/prodam-ASgBAgICAUSSA8YQ?context=H4sIAAAAAAAA_0q0MrSqLraysFJKK8rPDUhMT1WyLrYyNLNSKk5NLErOcMsvyg3PTElPLVGyrgUEAAD__xf8iH4tAAAA',
    'sec-ch-ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Mobile Safari/537.36',
    'x-laas-timezone': 'Europe/Moscow',
}
linkslist = {}
for numberpage in range(1, 101):
    response = requests.get(
        f'https://m.avito.ru/api/11/items?key=af0deccbgcgidddjgnvljitntccdduijhdinfgjgfjir&params[201]=1059&categoryId=24&locationId=625810&localPriority=0&context=H4sIAAAAAAAAA0u0MrSqLraysFJKK8rPDUhMT1WyLrYyNLNSKk5NLErOcMsvyg3PTElPLVGyrgUAF_yIfi0AAAA&page={numberpage}&lastStamp=1684077060&display=list&limit=37&presentationType=serp',
        cookies=cookies,
        headers=headers,
    )
    soup = BeautifulSoup(response.text, features='lxml')
    info_list = json.loads(soup.text)['result']['items']
    for point in info_list:
        info = point['value']
        if link := info.get('uri_mweb'):
            coords = info.get('coords')
            linkslist['https://m.avito.ru' + link] = {'Широта': float(coords.get('lat')),
                                                      'Долгота': float(coords.get('lng'))}

for link in linkslist.keys():
    url = link.split('?')[0]
    params = {'context': link.split('=')[1]}
    headers['referer'] = link
    soup = requests_url(url=url, params=params, headers=headers, cookies=cookies)
    pars(soup=soup, linkslist=linkslist, link=link)

    # id = link.split('._')[2].split('?')[0]
    # params = {
    #     'key': 'af0deccbgcgidddjgnvljitntccdduijhdinfgjgfjir',
    # }
    # response = requests.get(f'https://m.avito.ru/api/1/items/{id}/phone', params=params, cookies=cookies,
    #                         headers=headers)
    # phone = BeautifulSoup(response.text, features='lxml')
    # phone = json.loads(phone.text)['result']['action']['uri'].split('%2B')[1]
    # Телефон можно вот так выцеплять, но он у них вертуальный и спустя время меняется.
    # Так что решил не делать лишний запрос и оставить так, хоть и переделывал код под возможность парсить ещё и номер.

with open('data2.json', 'w') as f:
    json.dump(linkslist, f, ensure_ascii=False, indent=4)
