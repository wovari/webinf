class Movie:
    def __init__(self, title, url):
        self.__title = title
        self.__url = url

    def __repr__(self):
        return "Movie(%s,%s)"%(self.__title, self.__url)

    def __str__(self):
        return"Title: "+self.__title+"\nURL: "+self.__url

    def __hash__(self):
        return hash(self.__repr__())

    def __eq__(self, other):
        if isinstance(other, Movie):
            return (self.url == other.get_url())
        else:
            return False

    def get_title(self):
        return self.__title

    def get_url(self):
        return self.__url
