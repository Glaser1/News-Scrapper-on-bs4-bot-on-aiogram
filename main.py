import os
import json
import hashlib
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()
FILE_PATH: str | None = os.getenv('FILE_PATH')
KITCO_NEWS_URL = 'https://www.kitco.com/mining/'


def create_an_id_for_article(article_url: str) -> str:
    """
    Создает уникальный идентификатор для статьи на основе URL
    (для использования в качестве ключа для словаря новостей и json-файла).

    Args:
        article_url (str): URL статьи.

    Returns:
        str: Уникальный идентификатор статьи.
    """
    article_url_bytes: bytes = article_url.encode('UTF-8')
    article_id: str = hashlib.sha256(article_url_bytes).hexdigest()
    return article_id[:8]


def extract_article_data(new: BeautifulSoup, url: str) -> dict[str, str]:
    """
    Извлекает данные статьи из HTML и возвращает их в виде словаря.

    Args:
        new: BeautifulSoup объект для новости.
        url (str): URL страницы новостей.

    Returns:
        dict[str, str]: Словарь с данными статьи.
    """
    article_url: str = f"{url}{new.find('div', class_='mining-news--content').find('a').get('href')}"
    article_title: str = new.find('div', class_='mining-news--content').find('a').text.strip()
    article_description: str = new.find('div', class_='mining-news--content---text').find('p').text.strip()
    article_date: str = (new.find('div', 'mining-news--content')
                         .find('div', class_='mining-news--content---source-date')
                         .find('span', class_='mining-news--content---date').text.strip()
                         )

    return {
        'article_title': article_title,
        'article_url': article_url,
        'article_category': 'Mining news',
        'article_date': article_date,
        'article_description': article_description
    }


def get_mining_news() -> None:
    """
    Получает и записывает в json-файл все новости горнодобывающей промышленности.
    """
    try:
        response: requests.Response = requests.get(url=KITCO_NEWS_URL)
        response.raise_for_status()
        soup: BeautifulSoup = BeautifulSoup(response.text, 'lxml')
        news: dict[str, dict] = {}
        mining_news: list = soup.find_all('div', class_='mining-news--with-image')

        for new in mining_news:
            article_id: str = create_an_id_for_article(
                f"{KITCO_NEWS_URL}{new.find('div', class_='mining-news--content').find('a').get('href')}")
            news[article_id] = extract_article_data(new, KITCO_NEWS_URL)

        with open(FILE_PATH, mode='w', encoding='utf-8') as file:
            json.dump(news, file, indent=4, ensure_ascii=False)

    except Exception as e:
        print(f'An error occured: {e}')


def get_fresh_mining_news() -> dict[str, dict[str, str]]:
    """
    Получить только последние новости горнодобывающей промышленности.

    Returns:
        dict[str, dict[str, str]]: Словарь с данными только о новых статьях.
    """
    fresh_news: dict[str, dict[str, str]] = {}

    try:
        with open(FILE_PATH, mode='r', encoding='utf-8') as file:
            news: dict[str, dict[str, str]] = json.load(file)

        response: requests.Response = requests.get(url=KITCO_NEWS_URL)
        response.raise_for_status()
        soup: BeautifulSoup = BeautifulSoup(response.text, 'lxml')
        mining_news: list = soup.find_all('div', class_='mining-news--with-image')

        for new in mining_news:
            article_id: str = create_an_id_for_article(
                f"{KITCO_NEWS_URL}{new.find('div', class_='mining-news--content').find('a').get('href')}")
            if article_id not in news:
                article_data: dict[str, str] = extract_article_data(new, KITCO_NEWS_URL)
                news[article_id] = article_data
                fresh_news[article_id] = article_data

        with open(FILE_PATH, mode='w', encoding='utf-8') as file:
            json.dump(news, file, indent=4, ensure_ascii=False)

    except Exception as e:
        print(f'Произошла непредвиденная ошибка: {e}')

    return fresh_news


def main() -> dict[str, dict[str, str]] | None:
    """Основная функция, вызывает функцию для получения новостей."""
    if os.path.isfile(FILE_PATH) and os.path.getsize(FILE_PATH) > 0:
        return get_fresh_mining_news()
    else:
        get_mining_news()


if __name__ == '__main__':
    main()
