from lxml import html
import requests
from actor import Actor
from movie import Movie
from collections import deque

actor_dict = {}

movie_dict = {}

translate_actor_to_url = {}

actors_scraped = set()

processed_actors = set()

processing_queue = deque()

def IMDB_scraper(actor_name, degree, thr_mov, thr_act):
    root_actor = find_actor(actor_name)
    add_to_queue(root_actor.url)
    for i in range(degree):
        ctr = len(processing_queue)
        for j in range(ctr):
            act = processing_queue.popleft()
            create_edges(act,i, thr_mov, thr_act)
    for act in processing_queue:
        create_border(act, degree, thr_mov, thr_act)



def find_actor(actor_name):
    search_url = "http://www.imdb.com/find?q=" + actor_name
    cast_page = requests.get(search_url)
    cast_tree = html.fromstring(cast_page.text)
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


def find_shortest_path(start, end, path=[]):
    path = path + [start]
    if start == end:
        return path
    shortest = None
    for node in actor_dict[start].connections:
        if node not in path:
            newpath = find_shortest_path(node, end, path)
            if newpath:
                if not shortest or len(newpath) < len(shortest):
                    shortest = newpath


    return shortest

def shortest_path(start, end):
    shortest = find_shortest_path(start, end)
    return_string = ''
    act = actor_dict[shortest[0]]
    for i in range(1,len(shortest)):
        m = act.connections[shortest[i]]
        mov = movie_dict[m]
        act_to = actor_dict[shortest[i]]
        return_string += act.name + '--('+mov.title+')-->' + act_to.name + '\n'
        act = act_to
    return return_string

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

    else:
        thr_actor = float('Inf')
        thr_movie = float('Inf')

    print("Scraping started")
    IMDB_scraper(actor,int(degree),thr_actor,thr_movie)
    print("Scraping done, graph created with "+actor+" as root nodes")
    print("Choose from following functionalities")
    exit = False
    while(not exit):
        get_input = input("[find/path/exit]:")
        if get_input == "find":
            act = input("Name of actor:")
            try:
                act_url = translate_actor_to_url[act]
                print(actor_dict[act_url])
            except KeyError:
                print("Actor not found in graph")
        elif get_input == "exit":
            break
        elif get_input == "path":
            from_act = input("Actor to start from: ")
            to_act = input("Actor to end with: ")
            try:
                from_act = translate_actor_to_url[from_act]
                to_act = translate_actor_to_url[to_act]
                print(shortest_path(from_act, to_act))
            except KeyError:
                print("One of the actors is not in the graph")

    print("exiting")
