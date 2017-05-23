from movie import Movie


class Actor:
    """
    Contains data of an actor
    """

    def __init__(self, name, url):
        self.name = name
        self.url = url
        self.connections = {}
        self.degree = -1

    def __repr__(self):
        return "Actor(%s,%s)"%(self.name, self.url)

    def __str__(self):
        return"Name: "+self.name+"\nURL: "+self.url+"\nDegree: "+str(self.degree)

    def __eq__(self, other):
        if isinstance(other, Actor):
            return self.url == other.url
        else:
            return False

    def add_connection(self, actor, movie):
        if isinstance(movie, Movie):
            movie = movie.url
        if isinstance(actor, Actor):
            actor = actor.url
        self.connections[actor] = movie
