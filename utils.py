import re
import sys
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup, ResultSet, Tag
from pprint import pprint
from typing import List
from selectolax.parser import HTMLParser
import urllib3
from loguru import logger

logger.remove(0)
logger.add(sys.stderr,colorize=True)

BASE_URL = "https://books.toscrape.com/index.html"

def get_DOM(base_url = BASE_URL):
    try:    
        response = requests.get(BASE_URL)
        response.raise_for_status()
        DOM = BeautifulSoup(response.text, "html.parser")
        return DOM
    except requests.exceptions.RequestException as e:
        logger.error(f"An error has occured: {e}")
        raise requests.exceptions.RequestException from e
DOM = get_DOM()



def _get_book_id(book_url:str):
    book_id = re.findall(r'_(\d+)/', book_url)[0]
    return book_id

def _get_categories(dom_object:BeautifulSoup):
    try:
        logger.info("Getting all existing categories ...")
        links = dom_object.find('ul', class_='nav nav-list').find('ul').find_all('li')  # type: ignore
    except AttributeError as e:
        logger.error(f"La balise `ul` ou `li` n'existe pas dans sur la page. {e}")
        raise AttributeError from e
    return links

def build_categories_dictionnary(dom_object:BeautifulSoup =DOM):# -> dict[Any, Any]:
    logger.info("Building dictionnary of Categories ...")
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
    logger.info("Getting amount of books and articles ...")
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
    logger.info("Getting worst rated Books ... ")
    worst_rated_articles:List[Tag] = [article for article in articles if article.select('p.'+threshold_str)]
    
    books = {
            _get_book_id(article.find('a')['href']):article.find("img")['alt'] for article in worst_rated_articles # type: ignore
        }
    return books

# function to get the value of the entire web library 
# def get_book_to_scrape_value():
#     total_value = 0
#     ...


# function to get all details page link of each books and turn it to list
# next_page = True
def get_books_details_page_link(url:str=BASE_URL):
    # pages = details_links
    response = requests.get(url)
    tree = HTMLParser(response.content)
    logger.info(f"Scrapping page at: {url}")
    targeted_articles = tree.css("article.product_pod")
    # logger.info("Getting details page links of each books in current page ...")
    for article in targeted_articles:
        link = article.css_first("a").attributes['href'] 
        yield link
    # logger.info("Get next page")
    next_page = get_next_page_url(tree=tree)
    # print(pages)
    if next_page !=None:
        next_page = urljoin("https://books.toscrape.com/catalogue/",next_page)
        for link in get_books_details_page_link(next_page):
            yield link
    else:
        logger.success("All page has bee scraped")
        return None

# function to get the next page link
def get_next_page_url(tree: HTMLParser):
    try:
        next_page:str|None= tree.css_first('li.next').css_first('a').attributes['href']
    except AttributeError as exc:
        # logger.error("There are no other page to scrape or Something went wrong with your css querry, next_page has returned None as value ")
        # raise AttributeError from exc
        return None
    if next_page != None and "/" in next_page:
        next_page = next_page.split('/')[1] 
    if next_page is None:
        raise Exception("Something went wrong with your css querry, next_page has returned None as value ")
    # logger.info("Go to the next page ...")
    return next_page

# function to get book's price 
def get_book_price(tree: HTMLParser):
    article = tree.css_first("article") 
    return article.css_first('p.price_color').text()[1:]

def get_book_title(tree: HTMLParser):
    title = tree.css_first('h1').text()
    return title
    pass
# function to get amount of book in stock
def get_in_stock(tree: HTMLParser):
    in_stock = tree.css_first('p.instock.availability').text()
    in_stock:str = in_stock.split('available')[0].split('(')[1]
    return in_stock

# function to get the value of this books based on the amount in stock
def in_stock_book_value():
    pass




if __name__ == '__main__':
    pass
