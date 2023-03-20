import requests
from bs4 import BeautifulSoup
from time import sleep
from random import randint


def pars_apartments(link, headers, cookies):
    """
    Собирает информацию внутри объявления.
    По нормальнаму, переделать бы её для парсинга по мобильной версии, там телефон видно.

    :param link:
    :param headers:
    :param cookies:
    :return:
    """
    all_info = {'link': [None], 'Адрес': [None], 'Застройщик': [None], 'Агентство': [None], 'Частное лицо': [None],
                'Цена': [None], 'Цена за квадрат': [None], 'Общая площадь': [None], 'Жилая площадь': [None],
                'Площадь кухни': [None], 'Балкон или лоджия': [None], 'Санузел': [None], 'Высота потолков': [None],
                'Количество комнат': [None], 'Этаж': [None], 'Этажей в доме': [None], 'Отделка': [None],
                'Пассажирский лифт': [None], 'Грузовой лифт': [None], 'Двор': [None], 'Парковка': [None],
                'Окна': [None], 'Название новостройки': [None], 'Официальный застройщик': [None], 'Тип участия': [None],
                'Срок сдачи': [None], 'Тип дома': [None], 'Корпус, строение': [None], 'Способ продажи': [None],
                'Вид сделки': [None]}
    # На предыдущем датафрейме вывел какие могут быть параметры, решил сразу создавать

    response = requests.get(url=link,
                            headers=headers,
                            cookies=cookies,
                            )
    soup = BeautifulSoup(response.text, features='lxml')

    all_info['link'] = [link]

    address = soup.find('span', {'class': 'style-item-address__string-wt61A'}).text.strip()
    all_info['Адрес'] = [address]

    block_developer = soup.find('div', class_='style-seller-info-col-PETb_')
    developer = block_developer.find('div', {'data-marker': 'seller-info/label'}).text
    name_developer = block_developer.find('span', class_='text-text-LurtD').text
    all_info[developer] = [name_developer]

    block_price = soup.find('div', class_='style-item-view-price-content-kAnuw')
    price = int(block_price.find('span', class_='js-item-price').get('content'))
    price_m2 = block_price.find('span', class_='style-item-line-mix-qV0Mt').text.replace('\xa0', '')
    price_m2 = int(price_m2.split('₽')[0])  # У него нет нормального вывода без непонятных байтов, а считать
    # как суму делить на метр тупо, данные то уже есть.
    all_info['Цена'] = [price]
    all_info['Цена за квадрат'] = [price_m2]

    block_about_apartaments = soup.find('div', {'data-marker': 'item-view/item-params'})
    about_apartaments = block_about_apartaments.find_all('li', class_='params-paramsList__item-appQw')
    for elem in about_apartaments:
        name = elem.text.split(':')[0]
        value = elem.text.split(':')[1].replace('\xa0', ' ').strip()
        if name in ['Общая площадь', 'Площадь кухни', 'Жилая площадь', 'Высота потолков']:
            # Убирем метры и переводим во float.
            value = float(value.split(' ')[0])
        elif name in ['Пассажирский лифт', 'Грузовой лифт']:
            try:
                value = float(value)
            except:
                value = None
            # Сделал так т.к. вертает строку в формате "1.0" или "нет".
        elif name == 'Этаж':
            value = int(value.split('из')[0])
        all_info[name] = [value]

    block_about_house = soup.find('div', class_='style-item-params-McqZq')
    about_house = block_about_house.find_all('li', class_='style-item-params-list-item-aXXql')
    for elem in about_house:
        all_info[elem.text.split(':')[0]] = [elem.text.split(':')[1].replace('\xa0', ' ').strip()]

    return all_info


def pars_blocks(url, headers, cookies, params):
    """
    Парсит ссылки непосредственно на объявления

    :param url:
    :param headers:
    :param cookies:
    :param params:
    :return:
    """
    response = requests.get(url=url,
                            params=params,
                            cookies=cookies,
                            headers=headers,
                            )
    soup = BeautifulSoup(response.text, features='lxml')
    tablo_all = soup.find_all('div', class_='iva-item-body-KLUuy')

    return tablo_all


def pars_links(url, params, cookies, headers, max_page):
    """
    Собирает все ссылки на объявления в словаре.
    Ключ - ссылка с которой перешли.
    Значения - список на которые перешли

    :param url:
    :param params:
    :param cookies:
    :param headers:
    :param max_page:
    :return:
    """
    links_error = {}
    # Буду сюда сохранять ключ - ссылка с какой перешли, значение - ссылка на какую перешли
    # для тех линков по которым ошибки будут, чтоб позже их повторно пройти.

    links = {}
    # Сюда будем писать все линки объявлений. Ключ это ссылка с какой, значение список на какие переходим.

    for i in range(1, max_page + 1):
        params['p'] = str(i)
        all_panels = pars_blocks(url=url, cookies=cookies, headers=headers, params=params)
        # Находим все блоки объявлений

        Referer = url + f'?p={i}'
        headers['Referer'] = Referer  # Сохраняем для следующих переходов, мол мы кликаем по кнопкам страниц.
        # Делаем это, чтоб показать что на следующую страницу перешли с этой ссылки.
        links[Referer] = []
        links_error[Referer] = []

        for panel in all_panels:
            key = panel.find('a', class_='iva-item-groupingsLink-gvbkF')
            if key:
                # Так делаем проверку на NaN, есть ли ссылка на похожие квартиры, или нет.
                href = key.get('href')
                Referer_pod = 'https://www.avito.ru' + href
                links[Referer_pod] = []
                # pod значит что подсылка/подданные, данные для "углубления".
                params_pod = {}
                href = href.split('?')[1]  # Вначале отделяем параметры, они начинаются после ?
                for param in href.split('&'):  # Параметры между собой разделены &
                    params_pod[param.split('=')[0]] = param.split('=')[1]  # Каждый параметр разделён знаком =
                    # Под 0 - название; под 1 - индексом значение.

                sleep(randint(1, 4))
                panels_all_pod = pars_blocks(url=url, cookies=cookies, headers=headers, params=params_pod)
                # Находим все блоки объявлений

                for panel_pod in panels_all_pod:
                    link = 'https://www.avito.ru' + panel_pod.find('a', class_='link-link-MbQDP').get('href')
                    links[Referer_pod].append(link)
            else:
                link = 'https://www.avito.ru' + panel.find('a', class_='link-link-MbQDP').get('href')
                links[Referer].append(link)

    return links, links_error
