import re
from urllib import request
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup, ResultSet, Tag
from pprint import pprint
from typing import List, Dict
import time


BASE_URL = "https://books.toscrape.com/index.html"

def get_DOM(base_url = BASE_URL):
    try:    
        response = requests.get(BASE_URL)
        response.raise_for_status()
        DOM = BeautifulSoup(response.text, "html.parser")
        return DOM
    except requests.exceptions.RequestException as e:
        print(f"errreur {e}")
        raise requests.exceptions.RequestException from e
DOM = get_DOM()


def _get_categories(dom_object:BeautifulSoup):
    try:
        links = dom_object.find('ul', class_='nav nav-list').find('ul').find_all('li')  # type: ignore
    except AttributeError as e:
        print(f"La balise `ul` ou `li` n'existe pas dans sur la page. {e}")
        raise AttributeError from e
    return links

def build_categories_dictionnary(dom_object:BeautifulSoup =DOM):# -> dict[Any, Any]:
    links = _get_categories(dom_object)
    categories_dict = {tag.text.strip():tag.find('a')['href'] for tag in links} 
    return categories_dict

def get_amount_of_books(from_url:str,from_base_url: bool, **kwargs) -> tuple[int, ResultSet[Tag]]:
    """get all article tags with `product_pod` as class 

    :param from_url: url to get article from
    :type from_url: str
    :param from_base_url: if you getting article from home page set it to True
    :type from_base_url: bool
    :return: tuple made with the number of article on this page and the list of them
    :rtype: tuple[int, ResultSet[Tag]]:
    """
    session: requests.Session = kwargs.get('session') # type: ignore
    absolute_url = BASE_URL if from_base_url else urljoin(BASE_URL,from_url)
    if session:
        response = session.get(absolute_url)
        response.raise_for_status()
    else:
        response = requests.get(absolute_url)
        response.raise_for_status()
    articles: ResultSet[Tag] = BeautifulSoup(response.text,'html.parser').find_all('article',class_='product_pod')
    return len(articles),articles


def get_worst_rated_books(from_url_page:str = BASE_URL, threshold:int = 1,**kwargs:dict[str,requests.Session]):# -> dict[Any, str | list[str] | Any]:
    int_to_string = {
        1:"One",
        2:"Two",
        3:"Three",
        4:"Four",
        5:"Five"
    }
    rq_session:requests.Session = kwargs.get('session')  # type: ignore
    if rq_session:
        if from_url_page == BASE_URL:
            articles = get_amount_of_books(from_url=BASE_URL,from_base_url=True,sess=rq_session)[1]
        else:
            absolute_url = urljoin(BASE_URL,from_url_page)
            articles = get_amount_of_books(from_url=absolute_url,from_base_url=False,sess=rq_session)[1]
    else:
        if from_url_page == BASE_URL:
            articles = get_amount_of_books(from_url=BASE_URL,from_base_url=True,sess=rq_session)[1]
        else:
            absolute_url = urljoin(BASE_URL,from_url_page)
            articles = get_amount_of_books(from_url=absolute_url,from_base_url=False,sess=rq_session)[1]

    threshold_str = int_to_string.get(threshold,"One")
    worst_rated_articles:List[Tag] = [article for article in articles if article.select('p.'+threshold_str)]
    
    books = {
            _get_book_id(article.find('a')['href']):article.find("img")['alt'] for article in worst_rated_articles # type: ignore
        }
    return books


def _get_book_id(book_url:str):
    book_id = re.findall(r'_(\d+)/', book_url)[0]
    return book_id



if __name__ == '__main__':
    pass
