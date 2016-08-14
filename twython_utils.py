from twython import Twython
import re

APP_KEY = 'XhqKZd5lLIQot8V1LULIDx6ze'
APP_SECRET = 'Oe7qmeT7u3tz82AZDw1QCkqWkwtOOLYYe3CQaXMtl7Cf1bHqkQ'

twitter = Twython(APP_KEY, APP_SECRET, oauth_version=2)
ACCESS_TOKEN = twitter.obtain_access_token()
twitter = Twython(APP_KEY, access_token=ACCESS_TOKEN)


# returns a list of tuples, in the form (tweet_string, date) from a username (screen_name)
def get_all_tweets_username(twitter_instance, username, max_tweets, min_words, include_rt, like_mode):
    tweets = []

    full_tweets = []
    step = 200  # Maximum value is 200.
    for start in range(0, max_tweets, step):

        # Maximum of `step` tweets, or the remaining to reach max_tweets.
        count = min(step, max_tweets - start)

        kwargs = {'count': count}
        if full_tweets:
            last_id = full_tweets[-1]['id']
            kwargs['max_id'] = last_id - 1
        if like_mode:
            current = twitter_instance.get_favorites(screen_name=username, include_rts=include_rt, **kwargs)
        else:
            current = twitter_instance.get_user_timeline(screen_name=username, include_rts=include_rt, **kwargs)
        full_tweets.extend(current)

    for tweet in full_tweets:
        text = re.sub(r'(https?://\S+)', '', tweet['text'])
        text = re.sub(r'(^|[^@\w])@(\w{1,15})\b', '', text)
        text = re.sub(r'#(\w+)', '', text)
        date = tweet['created_at']

        # Only tweets with at least five words.
        if len(re.split(r'[^0-9A-Za-z]+', text)) > min_words:
            tweets.append((text, date))
    return tweets


# returns text of all the tweets in which a user mentioned someone more influential user. Explicitly excludes RT's
def get_tweets_by_entity(twitter_instance, username, max_tweets, min_words):

    followers = twitter_instance.get_followers_ids(screen_name=username)['ids']
    notable_tweets = []
    normal_tweets = []
    hashtags = []
    full_tweets = []
    step = 200  # Maximum value is 200.
    for start in range(0, max_tweets, step):

        # Maximum of `step` tweets, or the remaining to reach max_tweets.
        count = min(step, max_tweets - start)

        kwargs = {'count': count}
        if full_tweets:
            last_id = full_tweets[-1]['id']
            kwargs['max_id'] = last_id - 1
        current = twitter_instance.get_user_timeline(screen_name=username, include_rts=False, **kwargs)
        full_tweets.extend(current)

    for tweet in full_tweets:

        men = False
        mentions = tweet['entities']['user_mentions']
        hashtags.extend(tweet['entities']['hashtags'])

        for user in mentions:
            if user['id'] not in followers:
                men = True
                break

        text = re.sub(r'(https?://\S+)', '', tweet['text'])
        text = re.sub(r'(^|[^@\w])@(\w{1,15})\b', '', text)
        text = re.sub(r'#(\w+)', '', text)
        date = tweet['created_at']

        # Only tweets with at least five words.
        if len(re.split(r'[^0-9A-Za-z]+', text)) > min_words:
            if men:
                notable_tweets.append((text, date))
            else:
                normal_tweets.append((text, date))

    hashtags = [x['text'] for x in hashtags]
    return normal_tweets, notable_tweets, hashtags


# returns a list of descriptions of friends from username. Strings are stripped from links and handles(not hashtags)
def get_friends_descriptions(twitter_instance, username, max_users=100):
    user_ids = twitter_instance.get_friends_ids(screen_name=username)['ids']
    following = []

    for start in range(0, min(max_users, len(user_ids)), 100):
        end = start + 100
        following.extend(lookup_ids(twitter_instance, user_ids[start:end]))

    descriptions = []
    for user in following:
        try:
            if user['verified']:
                description = re.sub(r'(https?://\S+)', '', user['description'])
                description = re.sub(r'(^|[^@\w])@(\w{1,15})\b', '', description)
                if len(re.split(r'[^0-9A-Za-z]+', description)) > 10:
                    descriptions.append(description.strip('#').strip('@'))
        except Exception as e:
            break
    return descriptions


def get_followers_count(twitter_instance, username):
    return twitter_instance.show_user(screen_name=username)['friends_count']


def get_friends_count(twitter_instance, username):
    return twitter_instance.show_user(screen_name=username)['followers_count']


def get_description_from_id(twitter_instance, user_id):
    return twitter_instance.show_user(id=user_id)['description']


def get_username_from_id(twitter_instance, user_id):
    return twitter_instance.show_user(id=user_id)['screen_name']


def get_id_from_username(twitter_instance, username):
    return twitter_instance.show_user(screen_name=username)['id']


def lookup_ids(twitter_instance, ids):
    st = ''
    for id in ids:
        st = st + str(id) + ', '
    st = st[:-1]
    return twitter_instance.lookup_user(user_id=st)


# methods for getting tweets fom timeline and likes, striped from urls and hashtags.
def get_likes(twitter_instance, username, max_tweets=50, min_words=5, include_rt=True):
    return get_all_tweets_username(twitter_instance, username, max_tweets, min_words, include_rt, True)


def get_tweets(twitter_instance, username, max_tweets=200, min_words=5, include_rt=True):
    return get_all_tweets_username(twitter_instance, username, max_tweets, min_words, include_rt, False)

