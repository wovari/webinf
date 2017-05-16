class Actor:
    def __init__(self, name, url):
        self.__name = name
        self.__url = url

    def __repr__(self):
        return "Actor(%s,%s)"%(self.__name, self.__url)

    def __str__(self):
        return"Name: "+self.__name+"\nURL: "+self.__url

    def __hash__(self):
        return hash(self.__repr__())

    def __eq__(self, other):
        if isinstance(other, Actor):
            return (self.url == other.get_url())
        else:
            return False

    def get_url(self):
        return self.__url

    def get_name(self):
        return self.__name
