class Connection:
    def __init__(self, from_actor, to_actor, movie):
        self.__from = from_actor
        self.__to = to_actor
        self.__movie = movie

    def __str__(self):
        return_string = "\nFROM: "+self.__from+"\nTO: "+self.__to+"\nMOVIE: "+self.__movie
        return return_string

    def get_degree(self):
        return self.__degree

    def get_from(self):
        return self.__from

    def get_to(self):
        return self.__to

    def get_movie(self):
        return self.__movie
