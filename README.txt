Scraper.py scrapes pages from IMDB and creates a graph with actors as nodes and movies being the edges.
To run the project use Python3.
In linux terminal use following command: python3 scraper.py
When Scraper.py is run, there will be some questions in the terminal.
1) Enter an actor URL:
    Give an URL of an actor's page on IMDB and the page of this actor will be searched on IMDB for his name.
    It will then used as the root node.
2) Degree from actor:
    Give a number till which degree from the root you want to scrape actors.
    A degree of 0 is the root and 1 are all actors that have acted besides the root actor.
3) Do you want to limit searches? [y/n]
    If no is answered, the scraper will scrape all the movies and actors till a certain degree from IMDB.
    If yes is answered:
    3.1) Amount of co-actors:
        Give the maximum amount of co-actors it takes from the cast.
        If 3 is given, the first 3 actors from the cast will only be looked to.
    3.2) Amount of movies:
        Give the maximum amount of movies taken from the movie list of an actor.
        If 3 is given, the first 3 movies of the actor will only be taken.
    These limit the amount of pages the scraper needs to handle.
    However this makes that the graph can miss edges between actors because the movies they both played in
    are not in the top K.

After scraping is done, the user will get 3 options:
(the user needs to type the option and enter)
1) find
    Returns information about the actor
    The user will need to give the actors name. If not in the graph it will tell the user.
2) path
    Returns the shortest path between 2 actors in the graph
    The user will need to give a name as starting point and a name as end point.
    If one of these names is not in the graph, the program will return an error
3) exit
    The program keeps running till this option is given.

