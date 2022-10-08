import threading
import webview
import eel
import twint
from textblob import TextBlob
import datetime
import csv

print('TwScraper started.')


def Analyzer(num):
    eel.init('web')

    @eel.expose
    def start_calculating(tw_hashtags, tw_username, tw_startdate, tw_enddate, tw_sentimental):
        printer(tw_hashtags, tw_username, tw_startdate,
                tw_enddate, tw_sentimental)

    def printer(tw_hashtags, tw_username, tw_startdate, tw_enddate, tw_sentimental):
        tw_hashtags = tw_hashtags.replace(", ", ",")
        tw_hashtags = tw_hashtags.replace(" ,", ",")
        tw_hashtags_splitted = tw_hashtags.split(",")
        print(tw_hashtags)
        # array of keywords
        print(tw_hashtags_splitted)
        # username
        print(tw_username)
        # start date
        print(tw_startdate)
        # end date
        print(tw_enddate)
        # sentimental analysis
        print(tw_sentimental)

        # variable q contains twint configs
        q = twint.Config()
        if tw_username != 'None':
            q.Username = tw_username

        tw_hashtags = tw_hashtags.replace(",", " OR ")
        if tw_startdate != 'None':
            q.Since = str(tw_startdate)
            q.Until = str(tw_enddate)

        q.Search = tw_hashtags
        q.Store_csv = True
        q.Lang = 'en'

        # date and time as file name
        now = datetime.datetime.now()
        file_loc = str('outputs/'+now.strftime("%Y-%m-%d_%H-%M-%S")+'.csv')
        q.Output = file_loc

        # start twint search/scraping
        twint.run.Search(q)

        with open(file_loc, newline='', encoding='utf8') as f:
            reader = csv.reader(f)
            data = list(reader)

            data[0].append('Sentimental_Analysis_Subjectivity')
            data[0].append('Sentimental_Analysis_Polarity_Value')
            data[0].append('Sentimental_Analysis_Polarity_Output')
            if str(tw_sentimental) != 'False':
                print('Scraping finished, now starting to do sentimental analysis.')
            else:
                print('Scraping finished.')
            if str(tw_sentimental) != 'False':
                i = 1
                while i < len(data):
                    tweet = data[i][10]
                    tweet = tweet.replace('@', '')
                    tweet = tweet.replace('#', '')
                    stweet = TextBlob(tweet)

                    data[i].append(stweet.sentiment.subjectivity)
                    data[i].append(stweet.sentiment.polarity)
                    if stweet.sentiment.polarity > 0:
                        data[i].append('Positive')
                    if stweet.sentiment.polarity == 0:
                        data[i].append('Neutral')
                    if stweet.sentiment.polarity < 0:
                        data[i].append('Negative')
                    i = i+1

                file = open(file_loc, 'w+', newline='', encoding='utf8')
                file.truncate(0)
                with file:
                    write = csv.writer(file)
                    write.writerows(data)
                print('Scraping and analysis finished.')

    eel.start('index.html', size=(300, 700), mode=None, port=8078)  # Start


if __name__ == "__main__":

    t1 = threading.Thread(target=Analyzer, args=(10,))

    # starting thread 1
    t1.start()
    # starting thread 2

    webview.create_window('TwScrapper', 'http://localhost:8078/index.html',
                          height=900, background_color='#1a1a1a')
    webview.start()

    # wait until thread 1 is completely executed
    t1.join()
    # wait until thread 2 is completely executed

    # both threads completely executed
    print("Done!")
