class Connection:
    def __init__(self, from_actor, to_actor, degree, movie):
        self.__from = from_actor
        self.__to = to_actor
        self.__degree = degree
        self.__movie = movie

    def __str__(self):
        returnstring = "\nFROM: "+self.__from+"\nTO: "+self.__to+"\nDEGREE: "+str(self.__degree)+"\nMOVIE: "+self.__movie
        return returnstring
