import os
import json
import hashlib
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()
FILE_PATH = os.getenv('file_path')


def create_an_id(url):
    id = hashlib.sha256()
    id.update(url.encode('utf-8'))
    id = str(int(id.hexdigest(), 16))[:6]
    return id


def get_mining_news():
    """ Получить все последние новости. """

    url = 'https://www.kitco.com/mining/'
    r = requests.get(url=url)
    soup = BeautifulSoup(r.text, 'lxml')
    news = dict()
    mining_news = soup.find_all('div', class_='mining-news--with-image')
    for new in mining_news:
        article_url = (f"{url}"
                       f"{new.find('div', class_='mining-news--content').find('a').get('href')}")

        article_title = new.find('div', class_='mining-news--content').find('a').text.strip()
        article_description = new.find('div', class_='mining-news--content---text').find('p').text.strip()
        article_date = (new.find('div', 'mining-news--content')
                        .find('div', class_='mining-news--content---source-date')
                        .find('span', class_='mining-news--content---date').text.strip()
                        )
        article_category = 'Mining news'
        article_id = create_an_id(article_url)

        news[article_id] = {
            'article_title': article_title,
            'article_url': article_url,
            'article_category': article_category,
            'article_date': article_date,
            'article_description': article_description
        }

    with open(FILE_PATH, mode='w', encoding='utf-8') as file:
        json.dump(news, file, indent=4, ensure_ascii=False)


def get_mining_fresh_news():
    """ Получить только последние новости. """

    with open(FILE_PATH, mode='r', encoding='utf-8') as file:
        news = json.load(file)

    fresh_news = dict()
    url = 'https://www.kitco.com/mining/'
    r = requests.get(url=url)
    soup = BeautifulSoup(r.text, 'lxml')
    mining_news = soup.find_all('div', class_='mining-news--with-image')
    article_category = 'Mining news'

    for new in mining_news:
        article_url = (f"{url}"
                       f"{new.find('div', class_='mining-news--content').find('a').get('href')}")
        article_id = create_an_id(article_url)
        if article_id in news:
            continue
        else:
            article_title = new.find('div', class_='mining-news--content').find('a').text.strip()
            article_description = new.find('div', class_='mining-news--content---text').find('p').text.strip()
            article_date = (new.find('div', 'mining-news--content')
                            .find('div', class_='mining-news--content---source-date')
                            .find('span', class_='mining-news--content---date').text.strip()
                            )

            news[article_id] = {
                'article_title': article_title,
                'article_url': article_url,
                'article_category': article_category,
                'article_date': article_date,
                'article_description': article_description
            }

            fresh_news[article_id] = {
                'article_title': article_title,
                'article_url': article_url,
                'article_category': article_category,
                'article_date': article_date,
                'article_description': article_description
            }

    with open(FILE_PATH, mode='w', encoding='utf-8') as file:
        json.dump(news, file, indent=4, ensure_ascii=False)
    return fresh_news


def main():
    if os.path.isfile(FILE_PATH) and os.path.getsize(FILE_PATH) > 0:
        return get_mining_fresh_news()
    else:
        get_mining_news()


if __name__ == '__main__':
    main()
