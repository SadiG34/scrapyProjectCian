import json
import re
import time
import requests
from scrapy.selector import Selector
from selenium import webdriver
from selenium.webdriver.common.by import By

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

filtered_data = []


def parse_cian(page_num):
    url = f'https://kazan.cian.ru/cat.php?deal_type=sale&engine_version=2&offer_type=flat&p={page_num}&region=4777&room1=1'

    driver = webdriver.Chrome()  # Инициализация драйвера
    driver.get(url)

    while True:
        time.sleep(10)
        html_text = driver.page_source
        selector = Selector(text=html_text)

        apt_info = selector.css('span[data-mark="OfferTitle"] span::text').extract()
        price_info = selector.css('span[data-mark="MainPrice"] span::text').extract()
        offer_links = selector.css('a._93444fe79c--link--VtWj6::attr(href)').extract()

        all_ids = []
        all_addresses = []
        for id_, address in zip(offer_links, selector.css('div._93444fe79c--labels--L8WyJ').extract()):
            numeric_id = re.search(r'\d+', id_).group()
            all_ids.append(numeric_id)
            address_selector = Selector(text=address)
            full_address = address_selector.css('a::text').extract()
            all_addresses.append(full_address)

        all_titles = []
        for id_ in all_ids:
            link = f'https://kazan.cian.ru/sale/flat/{id_}/'
            response = requests.get(link, headers=headers)
            if response.status_code == 200:
                detail_text = response.text
                detail_selector = Selector(text=detail_text)
                title = detail_selector.css('h1.a10a3f92e9--title--vlZwT::text').extract_first()
                all_titles.append(title)

        for apt, price, title, id_, address in zip(apt_info, price_info, all_titles, all_ids, all_addresses):
            filtered_data.append(
                {"title": title, "apartment_info": apt, "price": price, 'ID': id_, "address": address,
                 "page": f'Page {page_num}'})

        try:
            time.sleep(5)
            show_more_button = driver.find_element(By.XPATH, '//*[@id="frontend-serp"]/div/div[5]/div[12]/a')
            time.sleep(5)

            show_more_button.click()
        except:
            break

    driver.quit()

    with open('cian_spider.json', 'w', encoding='utf-8') as f:
        json.dump(filtered_data, f, ensure_ascii=False)


parse_cian(54)  # Введите номер страницы
