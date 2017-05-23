class Movie:
    """
    Contains data about a movie 
    """
    def __init__(self, title, url):
        self.title = title
        self.url = url
        self.cast = set()


    @property
    def cast(self):
        return list(self.__cast)

    @cast.setter
    def cast(self, x):
        self.__cast = x

    def __repr__(self):
        return "Movie(%s,%s)"%(self.title, self.url)

    def __str__(self):
        return"Title: "+self.title+"\nURL: "+self.url

    def __hash__(self):
        return hash(self.__repr__())

    def __eq__(self, other):
        if isinstance(other, Movie):
            return self.url == other.url
        else:
            return False

    def add_to_cast(self, actor_url):
        self.__cast.add(actor_url)
