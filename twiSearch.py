from TwitterSearch import *



class twiSearch:
    def __init__(self, credentials):
        self.credentials = credentials

    def search(self, tags, lan='ru'):
        try:
            tso = TwitterSearchOrder()  # create a TwitterSearchOrder object
            tso.set_keywords(tags)  # let's define all words we would like to have a look for
            tso.set_language(lan)  # we want to see German tweets only
            tso.set_include_entities(False)  # and don't give us all those entity information

            return self.credentials.search_tweets_iterable(tso)
        except TwitterSearchException as e:  # take care of all those ugly errors if there are some
            print(e)
