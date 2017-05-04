from lxml import html
import requests

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