class Movie:
    def __init__(self, title, url):
        self.__title = title
        self.__url = url

    def get_title(self):
        return self.__title

    def get_url(self):
        return self.__url