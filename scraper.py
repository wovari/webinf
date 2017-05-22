from lxml import html
import requests
from actor import Actor
from movie import Movie
from connection import Connection
from collections import deque

#actor_dict[key = URL, value = Actor class]
actor_dict = {}

#movie_dict[key = URL, value = Movie class]
movie_dict = {}

translate_actor_to_url = {}

actors_scraped = set()

processed_actors = set()

processing_queue = deque()


def IMDB_scraper(actor_name, degree, thr_mov = float('Inf'), thr_act = float('Inf')):
    root_actor = find_actor(actor_name)
    add_to_queue(root_actor.url)
    for i in range(degree):
        ctr = len(processing_queue)
        for j in range(ctr):
            act = processing_queue.popleft()
            create_edges(act,i, thr_mov, thr_act)
    for act in processing_queue:
        create_border(act, degree, thr_mov, thr_act)




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
    actor_dict[actor_url] = act
    translate_actor_to_url[actor_name] = actor_url
    return act


# return everything except TV Series
def list_movies_of_actor(actor_url, threshold=float('inf')):
    movie_lst = []
    cast_page = requests.get(actor_url)
    cast_tree = html.fromstring(cast_page.text)
    path_to_movies = cast_tree.xpath('//div[@class="filmo-category-section"]'
                                     '/div[not(text()[contains(., "TV Series")])]/b/a')
    for mov in path_to_movies:
        if threshold <= 0:
            break
        movie_name = mov.text
        movie_url = strip_url("http://www.imdb.com" + mov.attrib.get('href'))
        if not movie_url in movie_dict:
            movie_dict[movie_url] = Movie(movie_name, movie_url)
        movie_lst.append(movie_url)
        threshold -= 1
    return movie_lst


def list_cast_of_movie(movie_url, threshold=float('Inf'), cast_lookup=True, add_new_actors=True):
    mov = movie_dict[movie_url]
    if len(mov.cast) > 0 and (threshold <= len(mov.cast) or threshold ==float('Inf')) and cast_lookup:
        if threshold == float('Inf'):
            return mov.cast
        else:
            return mov.cast[:threshold]
    else:
        actor_lst = []
        cast_url = movie_url + "/fullcredits?ref_=tt_ov_st_sm"
        cast_page = requests.get(cast_url)
        cast_tree = html.fromstring(cast_page.text)
        path_to_actors = cast_tree.xpath('//table[@class="cast_list"]'
                                         '/tr[@class="odd" or @class="even"]'
                                         '/td[@class="itemprop"]/a')
        for act in path_to_actors:
            if threshold <= 0:
                break
            actor_name = act[0].text
            actor_url = strip_url("http://www.imdb.com" + act.attrib.get('href'))
            mov.add_to_cast(actor_url)
            if not actor_url in actor_dict and add_new_actors:
                actor_dict[actor_url] = Actor(actor_name,actor_url)
                translate_actor_to_url[actor_name] = actor_url
                add_to_queue(actor_url)
            actor_lst.append(actor_url)
            threshold-=1
        return actor_lst


def strip_url(url):
    url = url.split("?")[0]
    url = url[:-1]
    return url


def get_path(dict, actor):
    if actor in dict:
        connect = dict[actor]
        print("START PATH")
        while connect.get_degree() > 0:
            print(connect.get_to()+" --["+connect.get_movie()+"]--> "+connect.get_from())
            connect=dict[connect.get_from()]
        print("END PATH\n")
    else:
        print("ACTOR: "+actor+" NOT FOUND")


def add_to_queue(actor_url):
    if not actor_url in actors_scraped:
        processing_queue.append(actor_url)
        actors_scraped.add(actor_url)


def create_edges(actor_url,degree, thr_mov, thr_act):
    mov_lst = list_movies_of_actor(actor_url,threshold=thr_mov)
    unique_actors = set()
    actor = actor_dict[actor_url]
    print("Getting edges for: "+actor.name)
    actor.degree = degree
    for m in mov_lst:
        act_lst = list_cast_of_movie(m, threshold=thr_act)
        for a in act_lst:
            if not a in unique_actors and a != actor_url:
                actor.add_connection(a, m)
                if a in actor_dict:
                    tmp_act = actor_dict[a]
                    if not actor_url in tmp_act.connections:
                        tmp_act.add_connection(actor_url, m)
                        actor_dict[a] = tmp_act
                unique_actors.add(a)
    actor_dict[actor_url] = actor
    processed_actors.add(actor_url)

def create_border(actor_url, degree, thr_mov, thr_act):
    mov_lst = list_movies_of_actor(actor_url, threshold=thr_mov)
    unique_actors = set()
    actor = actor_dict[actor_url]
    print("Getting edges for: "+actor.name)
    actor.degree = degree
    for m in mov_lst:
        act_lst = list_cast_of_movie(m, threshold=thr_act, add_new_actors=False)
        for a in act_lst:
            if not a in unique_actors and a in actors_scraped and a != actor_url:
                actor.add_connection(a, m)
                unique_actors.add(a)
    actor_dict[actor_url] = actor
    processed_actors.add(actor_url)



# kevin = find_actor("Kevin Bacon")
# kevins_movies = list_movies_of_actor(kevin.get_url())
# for mov in kevins_movies:
#     cast_of_movie = list_cast_of_movie(mov.get_url())
#     for co_actor in cast_of_movie:
#         if not co_actor.get_url() == kevin.get_url():
#             kevin.add_co_actor(co_actor.get_name(), mov.get_title())
#             print(co_actor.get_name()+" : "+mov.get_title())

#
# root_actor = find_actor("Kevin Bacon")
# mov_url = list_movies_of_actor(root_actor.url, 1)[0]
#
# print(list_cast_of_movie(mov_url, threshold=5))
# print(list_cast_of_movie(mov_url, threshold=7))
# print(list_cast_of_movie(mov_url))
# print(list_cast_of_movie(mov_url, cast_lookup=False))
# print(list_cast_of_movie(mov_url))




#
#
#
#
# dict = IMDB_scraper("Kevin Bacon", 3 )
# print(dict["Mark Wahlberg"])
# print(dict["Christian Bale"])
# print(dict["Cate Blanchett"])
# print(dict["Jake Gyllenhaal"])
# get_path(dict, "Cate Blanchett")
# get_path(dict, "Jake Gyllenhaal")

def print_connections(actor_url):
    actor = actor_dict[actor_url]
    for act in actor.connections:
        act_name = actor_dict[act].name
        mov_name = movie_dict[actor.connections[act]].title
        print(act_name+" : "+mov_name)


if __name__ == "__main__":
    actor = input("Enter an actor:")
    degree = int(input("Degree from actor:"))
    thr = input("Do you want to limit searches? [y/n]")
    if thr == "y":
        thr_actor = int(input("Amount of co-actors:"))
        thr_movie = int(input("Amount of movies:"))

    print("Scraping started")
    IMDB_scraper(actor,int(degree),thr_act=thr_actor,thr_mov=thr_movie)
    for act in actor_dict:
        actor = actor_dict[act]
        print(actor)
        print_connections(act)

