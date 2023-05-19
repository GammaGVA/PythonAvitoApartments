import requests
from bs4 import BeautifulSoup


def requests_url(url, params, headers, cookies, ) -> BeautifulSoup:
    response = requests.get(
        url=url,
        params=params,
        cookies=cookies,
        headers=headers,
    )
    soup = BeautifulSoup(response.text, features='lxml')
    return soup


def pars(soup: BeautifulSoup, linkslist, link):
    price = soup.find('span', {"data-marker": "item-description/price"})
    if price == None:
        linkslist[link]['Параша'] = True
        return
    price = float(''.join(price.text.split()[:-1]))
    linkslist[link]['Цена'] = price

    price_per_meter = soup.find('span', {"data-marker": "item-description/normalized-price"})
    price_per_meter = price_per_meter.text.split('₽')[0]
    linkslist[link]['Цена за метр'] = float(price_per_meter.replace('\xa0', ''))

    seller = soup.find('span', {"data-marker": "seller-info/postfix"}).text
    name = soup.find('span', {"data-marker": "seller-info/name"}).text
    linkslist[link][seller] = name

    for i in range(19):
        info = soup.find_all('div', {"data-marker": f"item-properties-item({i})"})
        if info == []:
            break
        for point in info:
            key = point.find('span', {"data-marker": f"item-properties-item({i})/title"})
            item = point.find('span', {"data-marker": f"item-properties-item({i})/description"})
            linkslist[link][key.text.split(':')[0]] = item.text.replace('\xa0',' ')

    info_house = soup.find_all('div', {'class': 'Lehf0'})
    for n, point in enumerate(info_house):
        key = point.find_all('span', {"data-marker": f"additional-seller-item({n})/title"})
        item = point.find_all('span', {"data-marker": f"additional-seller-item({n})/description"})
        for k, i in zip(key, item):
            linkslist[link][k.text.split(':')[0]] = i.text.replace('\xa0', ' ')
