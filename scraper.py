from lxml import html
import requests
from actor import Actor
from movie import Movie

'''
movie_url = "http://www.imdb.com/title/tt1179933" #MOVIE URL
cast_url = movie_url + "fullcredits?ref_=tt_ov_st_sm" #CAST URL

cast_page = requests.get(cast_url) #Request page for the cast URL
cast_tree = html.fromstring(cast_page.text) #Build the DOM

path_to_odd_class = cast_tree.xpath('//tr[@class="odd"]/td[2]/a')
path_to_even_class = cast_tree.xpath('//tr[@class="even"]/td[2]/a')

for actor in path_to_even_class:
    actor_name = actor[0].text
    actor_url = "http://www.imdb.com" + actor.attrib.get('href')
    print(actor_name + " : " + actor_url)

for actor in path_to_odd_class:
    actor_name = actor[0].text
    actor_url = "http://www.imdb.com" + actor.attrib.get('href')
    print(actor_name + " : " + actor_url)
'''

def find_actor(actor_name):
    search_url = "http://www.imdb.com/find?q=" + actor_name
    cast_page = requests.get(search_url)
    cast_tree = html.fromstring(cast_page.text)  # Build the DOM
    path_to_first_actor = cast_tree.xpath('(//table[@class="findList"])[1]/tr[1]/td[2]/a')
    actor_link = path_to_first_actor[0]
    actor_url = strip_url("http://www.imdb.com" + actor_link.attrib.get('href'))
    act = Actor(actor_name, actor_url)
    return act


def list_movies_of_actor(actor_url):
    cast_page = requests.get(actor_url)
    cast_tree = html.fromstring(cast_page.text)
    path_to_movies = cast_tree.xpath('//div[@class="filmo-category-section"]/div/b/a')
    movie_list = []
    for mov in path_to_movies:
        movie_name = mov.text
        movie_url = strip_url("http://www.imdb.com" + mov.attrib.get('href'))
        movie_list.append(Movie(movie_name, movie_url))
    return movie_list

def list_cast_of_movie(movie_url):
    cast_url = movie_url + "/fullcredits?ref_=tt_ov_st_sm"
    cast_page = requests.get(cast_url)
    cast_tree = html.fromstring(cast_page.text)
    path_to_actors = cast_tree.xpath('//table[@class="cast_list"]/tr[@class="odd" or @class="even"]/td[@class="itemprop"]/a')
    actor_list = []
    for act in path_to_actors:
        actor_name = act[0].text
        actor_url = strip_url("http://www.imdb.com" + act.attrib.get('href'))
        actor_list.append(Actor(actor_name, actor_url))
    return actor_list

def strip_url(url):
    url = url.split("?")[0]
    url = url[:-1]
    return url

kevin = find_actor("Amy Anderson")
kevins_movies = list_movies_of_actor(kevin.get_url())
for mov in kevins_movies:
    cast_of_movie = list_cast_of_movie(mov.get_url())
    for co_actor in cast_of_movie:
        if not co_actor.get_url() == kevin.get_url():
            kevin.add_co_actor(co_actor.get_name(), mov.get_title())
            print(co_actor.get_name()+" : "+mov.get_title())



