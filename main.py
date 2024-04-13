from pprint import pprint
from actions import get_home_page_unfamous_books, get_library_unfamous_books
import time
BASE_URL = "https://books.toscrape.com/index.html"  



# you can uncoment this code if you want to get all unfamous books existing on home page wich are lower than 4 stars
start=time.time()
get_home_page_unfamous_books(stars_threshold=4)
print('first function tooks: {}'.format(time.time()-start))


# you can uncoment this code if you want to get all unfamous books existing on the entire web library wich are lower than  the `stars_treshold` 
start=time.time()
get_library_unfamous_books(stars_threshold=2)
print('second function tooks: {}'.format(time.time()-start))









