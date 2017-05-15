from lxml import html
import requests

from actor import Actor
from movie import Movie
from connection import Connection

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

def IMDB_scrapper(actor_name, degree):
    scraped_actors = {}
    scraped_movies = set()
    root_actor = find_actor(actor_name)
    root_connect = Connection('root', root_actor.get_name(), 0, 'root')
    scraped_actors[root_actor.get_name()] = root_connect
    print("0\n")
    if degree == 0:
        return scraped_actors
    scraped_actors, scraped_movies, unscraped_actors = scrape_actor(root_actor, scraped_actors, scraped_movies, 1)
    print("1\n")
    if degree < 2:
        return scraped_actors
    for i in range(2, degree + 1):
        temp_list = []
        for actor in unscraped_actors:
            scraped_actors, scraped_movies, part_unscraped_actors = scrape_actor(actor, scraped_actors, scraped_movies, i)
            temp_list += part_unscraped_actors
        unscraped_actors = temp_list
        print(str(i)+"\n")
    return scraped_actors



def scrape_actor(actor, actor_dict, movie_set, degree):
    print(actor.get_name())
    frontier_cast = []
    movies = list_movies_of_actor(actor.get_url())
    movie_idx = 3
    if len(movies) < 3:
        movie_idx = len(movies)
    #for movie in movies:
    for i in range(movie_idx):
        movie = movies[i]
        if not movie.get_url() in movie_set:
            movie_set.add(movie.get_url())
            print(movie.get_title())
            cast = list_cast_of_movie(movie.get_url())
            #for co_actor in cast:
            idx = 5
            if len(cast) < 5:
                idx = len(cast)
            for i in range(idx):
                co_actor = cast[i]
                if not co_actor.get_name() in actor_dict:
                    connect = Connection(actor.get_name(), co_actor.get_name(), degree, movie.get_title())
                    actor_dict[co_actor.get_name()] = connect
                    frontier_cast.append(co_actor)
    return actor_dict, movie_set, frontier_cast



def find_actor(actor_name):
    search_url = "http://www.imdb.com/find?q=" + actor_name
    cast_page = requests.get(search_url)
    cast_tree = html.fromstring(cast_page.text)  # Build the DOM
    path_to_first_actor = cast_tree.xpath('(//table[@class="findList"])[1]/tr[1]/td[2]/a')
    actor_link = path_to_first_actor[0]
    actor_url = strip_url("http://www.imdb.com" + actor_link.attrib.get('href'))
    act = Actor(actor_name, actor_url)
    return act

#return everything except TV Series
def list_movies_of_actor(actor_url):
    cast_page = requests.get(actor_url)
    cast_tree = html.fromstring(cast_page.text)
    path_to_movies = cast_tree.xpath('//div[@class="filmo-category-section"]/div[not(text()[contains(., "TV Series")])]/b/a')
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



# kevin = find_actor("Kevin Bacon")
# kevins_movies = list_movies_of_actor(kevin.get_url())
# for mov in kevins_movies:
#     cast_of_movie = list_cast_of_movie(mov.get_url())
#     for co_actor in cast_of_movie:
#         if not co_actor.get_url() == kevin.get_url():
#             kevin.add_co_actor(co_actor.get_name(), mov.get_title())
#             print(co_actor.get_name()+" : "+mov.get_title())

dict = IMDB_scrapper("Sophie Cookson", 4)
print(dict["Taron Egerton"])
print(dict["Kate Beckinsale"])
print(dict["Tobias Menzies"])
print(dict["Riz Ahmed"])




