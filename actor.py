class Actor:
    #TODO make the data structure XML
    def __init__(self, name, url):
        self.__name = name
        self.__url = url
        self.__co_actors = {}

    def get_url(self):
        return self.__url

    def get_name(self):
        return self.__name

    def add_co_actor(self, co_author, movie):
        if co_author in self.__co_actors:
            self.__co_actors[co_author].append(movie)
        else:
            self.__co_actors[co_author] = [movie]

    def get_co_actors(self):
        co_actors = []
        for actor in self.__co_actors.keys():
            co_actors.append(actor)
        return co_actors

    def get_movies_with_co_actor(self, co_actor):
        movies = []
        for movie in self.__co_actors[co_actor]:
            movies.append(movie)
        return movies


