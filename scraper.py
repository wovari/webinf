from lxml import html
import requests
from actor import Actor
from movie import Movie
from collections import deque
from contextlib import contextmanager
from time import perf_counter

@contextmanager
def timing(label: str):
    t0 = perf_counter()
    yield lambda: (label, t1 - t0)
    t1 = perf_counter()


"""
Actor and Movie entities are saved in a dictionary with key the URL of their page on IMDB.
The translate dictionary is used to quickly translate an actors name to a valid URL.
    actor_dict -- dictionary contains Actor classes and has as key the URL of the actors page on IMDB
    movie_dict -- dictionary contains Movie classes and has as key the URL of the movie page on IMDB
    translate_actor_to_url -- dictionary contains the name of the actor as key and the URL of their page as value
"""
actor_dict = {}
movie_dict = {}
translate_actor_to_url = {}

"""
The sets are used to keep track of all the actors already encountered.
When an actors URL is added to the queue, it is also added to actors_encountered.
This makes it easy during scraping to detect actors that are already scraped or waiting in the queue.
    actors_encountered -- set containing urls of actors
    processing_queu -- deque where all actors that are encountered but not yet processed are added to
"""
actors_encountered = set()
processing_queue = deque()

"""
IMDB_scraper is the function that creates a graph from a given actor as root with a degree K.
The nodes (actors) are stored in actor_dict and the edges are stored in the Actor class as connections.
    actor-name -- Name of the actor that will be used as root
    degree -- Find all actors till that degree of the actor
    thr_mov -- Limit on how many movies are selected
    thr_act -- Limit on how many actors are selected 
"""
def IMDB_scraper(actor_url, degree, thr_mov, thr_act):
    with timing('Total scraping time') as total_scrape:
        with timing('Find initial actor ') as initial_find:
            actor_name = get_actor_name(actor_url)
        print('%s[%.6f s]: ' % initial_find() + str(actor_name))
        act = Actor(actor_name, actor_url)
        act.degree = 0
        actor_dict[actor_url] = act
        translate_actor_to_url[actor_name] = actor_url
        add_to_queue(actor_url)
        for i in range(degree):
            ctr = len(processing_queue)
            for j in range(ctr):
                act = processing_queue.popleft()
                create_edges(act,i, thr_mov, thr_act)
        if degree > 0:
            for act in processing_queue:
                create_border(act, degree, thr_mov, thr_act)
    print('%s: %.6f s'% total_scrape())

"""
list_movies_of_actor is a function that returns the list with movies where the actor played a role in.
The limit parameter, if not infinite, will make sure that the length of the returned list is not longer than given limit.
    actor_url -- URL of the actor
    limit -- default value is infinite, limits the size of returned list
"""
def list_movies_of_actor(actor_url, limit=float('inf')):
    movie_lst = []
    cast_page = requests.get(actor_url)
    cast_tree = html.fromstring(cast_page.text)
    path_to_movies = cast_tree.xpath('//div[@id="filmography"]'
                                     '//div[(contains(@id, "actor") or contains(@id, "actress")) '
                                     'and not(text()[contains(., "TV Series")])]/b/a')
    print(len(path_to_movies))
    for mov in path_to_movies:
        if limit <= 0:
            break
        movie_name = mov.text
        print(movie_name)
        movie_url = strip_url("http://www.imdb.com" + mov.attrib.get('href'))
        if not movie_url in movie_dict:
            movie_dict[movie_url] = Movie(movie_name, movie_url)
        movie_lst.append(movie_url)
        limit -= 1
    return movie_lst

"""
list_cast_of_movie returns the list of the cast that acted in the movie. 
The limit parameter, if not infinite, will make sure that the length of the returned list is not longer than given limit.
    movie_url -- URL of the movie
    limit -- default value is infinite, limits the size of returned list
    cast_lookup -- default value is True, if False the function will not look in the dictionary to see if the movie
                   is already scraped.
    add_new_actors -- default value is True, if False the function will not add actors to the list that not yet encountered
"""
def list_cast_of_movie(movie_url, limit=float('Inf'), cast_lookup=True, add_new_actors=True):
    mov = movie_dict[movie_url]
    if len(mov.cast) > 0 and (limit <= len(mov.cast) or limit ==float('Inf')) and cast_lookup:
        if limit == float('Inf'):
            return mov.cast
        else:
            return mov.cast[:limit]
    else:
        actor_lst = []
        cast_url = movie_url + "/fullcredits?ref_=tt_ov_st_sm"
        cast_page = requests.get(cast_url)
        cast_tree = html.fromstring(cast_page.text)
        path_to_actors = cast_tree.xpath('//table[@class="cast_list"]'
                                         '/tr[@class="odd" or @class="even"]'
                                         '/td[@class="itemprop"]/a')
        for act in path_to_actors:
            if limit <= 0:
                break
            actor_name = act[0].text
            actor_url = strip_url("http://www.imdb.com" + act.attrib.get('href'))
            mov.add_to_cast(actor_url)
            if not actor_url in actor_dict and add_new_actors:
                actor_dict[actor_url] = Actor(actor_name,actor_url)
                translate_actor_to_url[actor_name] = actor_url
                add_to_queue(actor_url)
            actor_lst.append(actor_url)
            limit-=1
        return actor_lst


"""
strip_url is a function that strips a URL string of unnecessary data and returns the result
    url -- url that needs to be stripped
"""
def strip_url(url):
    if "?" in url:
        url = url.split("?")[0]
        url = url[:-1]
    return url

"""
add_to_queue is a function that handles which actors are added to the queue. 
It adds them only if they are not yet encountered.
    actor_url -- URL of actor that is to be added to the queue
"""
def add_to_queue(actor_url):
    if not actor_url in actors_encountered:
        processing_queue.append(actor_url)
        actors_encountered.add(actor_url)

"""
create_edges searches all actors where the given actor has worked with. 
Every connection (the movie and the co-actor) are added to the actors Actor object connection dictionary.
Only the first connection with a certain co-actor is saved. If later a movie is encountered in which the actor
also played with the co-actor, the connection is skipped.
The co-actor also adds the actor to its connections.
    actor_url -- URL of actor
    degree -- degree of root actor (to be saved in the actors object)
    thr_mov -- limit for the movie selection
    thr_act -- limit for the actor selection
"""
def create_edges(actor_url, degree, thr_mov, thr_act):
    mov_lst = list_movies_of_actor(actor_url, limit=thr_mov)
    actor = actor_dict[actor_url]
    unique_actors = set(list(actor.connections.keys()))
    print("Getting edges for: "+actor.name)
    actor.degree = degree
    for m in mov_lst:
        act_lst = list_cast_of_movie(m, limit=thr_act)
        for a in act_lst:
            if not a in unique_actors and a != actor_url:
                actor.add_connection(a, m)
                if a in actor_dict:
                    tmp_act = actor_dict[a]
                    if -1 < tmp_act.degree < (degree - 1):
                        actor.degree = tmp_act.degree + 1
                    if not actor_url in tmp_act.connections:
                        tmp_act.add_connection(actor_url, m)
                        actor_dict[a] = tmp_act
                unique_actors.add(a)
    actor_dict[actor_url] = actor

"""
create_border searches all actors where the given actor has worked with and that are already encountered.
This function is used to connect the actor with actors that are already present in the graph. 
For example if we want to end the graph at the 3rd degree, the actors on this degree can still connect 
with eachother without adding new actors to the queue.
    actor_url -- URL of actor
    degree -- degree of root actor (to be saved in the actors object)
    thr_mov -- limit for the movie selection
    thr_act -- limit for the actor selection    
"""
def create_border(actor_url, degree, thr_mov, thr_act):
    mov_lst = list_movies_of_actor(actor_url, limit=thr_mov)
    unique_actors = set()
    actor = actor_dict[actor_url]
    print("Getting edges for: "+actor.name)
    actor.degree = degree
    for m in mov_lst:
        act_lst = list_cast_of_movie(m, limit=thr_act, add_new_actors=False)
        for a in act_lst:
            if not a in unique_actors and a in actors_encountered and a != actor_url:
                actor.add_connection(a, m)
                if a in actor_dict:
                    tmp_act = actor_dict[a]
                    if not actor_url in tmp_act.connections:
                        tmp_act.add_connection(actor_url, m)
                        actor_dict[a] = tmp_act
                unique_actors.add(a)
    actor_dict[actor_url] = actor

"""
get_actor_name requests the actor page which URL is given, and with the aid of XPath returns the name of 
the actor.
    actor_url -- URL string of the actor's page
"""
def get_actor_name(actor_url):
    if actor_url[-1] == ' ':
        actor_url = actor_url.replace(' ', '')
    cast_page = requests.get(actor_url)
    if cast_page.status_code == 404:
        print("Page not found: %s" % actor_url)
        exit(0)
    cast_tree = html.fromstring(cast_page.text)
    actor_name = cast_tree.xpath('//span[@itemprop = "name"]/text()')
    return actor_name[0]


"""
find_shortest_path is a recursive BFS function that tries to find the shortest path between two vertices.
    q -- deque containing lists of actor URLs that still need to be handled
    seen_set -- set that contains the URLs of all actors that are already handled
    end -- URL of actor that needs to be found
"""
def find_shortest_path(q, seen_set, end):
    lst = q.popleft()
    el = lst[-1]
    seen_set.add(el)
    connections = list(actor_dict[el].connections.keys())
    for i in range(len(connections)):
        c = connections[i]
        if c not in seen_set:
            if c == end:
                lst.append(c)
                return lst, True, q, seen_set
            else:
                cpy_lst = lst[:]
                cpy_lst.append(c)
                q.append(cpy_lst)
    return lst, False, q, seen_set
"""
shortest_path is a function that calls find_shortest_path and translates the returned list of URLs to readable connections.
    start -- URL of actor from where to start
    end -- URL of actor that needs to be found
"""
def shortest_path(start, end):
    q = deque()
    q.append([start])
    path_set = set()
    found = False
    while(not found):
        shortest, found, new_q, path_set = find_shortest_path(q, path_set, end)
        q = new_q
    return_string = ''
    act = actor_dict[shortest[0]]
    for i in range(1,len(shortest)):
        m = act.connections[shortest[i]]
        mov = movie_dict[m]
        act_to = actor_dict[shortest[i]]
        return_string += act.name + '--('+mov.title+')-->' + act_to.name + '\n'
        act = act_to
    return return_string


if __name__ == "__main__":
    actor = strip_url(input("Enter an actor url:"))
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
