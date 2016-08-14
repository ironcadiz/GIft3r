from monkeylearn import MonkeyLearn
import re
from random import shuffle
from collections import Counter
import twython_utils
from twython import Twython
import matplotlib.pyplot as plt
#import scipy.stats
from unidecode import unidecode
from nltk.stem import SnowballStemmer
from difflib import SequenceMatcher


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

stemmer = SnowballStemmer('spanish', ignore_stopwords=False)
stemmer_e = SnowballStemmer('english', ignore_stopwords=False)

def apply_stemming(document, stemmer):
    return [stemmer.stem(x) for x in document]

def get_friends_descriptions(api, twitter_account, max_users=100):
    """
    Return the bios of the people that a user follows

    api -- the tweetpy API object
    twitter_account -- the Twitter handle of the user
    max_users -- the maximum amount of users to return
    """

    user_ids = api.friends_ids(twitter_account)
    shuffle(user_ids)

    following = []
    for start in range(0, min(max_users, len(user_ids)), 100):
        end = start + 100
        following.extend(api.lookup_users(user_ids[start:end]))

    descriptions = []
    for user in following:
        description = re.sub(r'(https?://\S+)', '', user.description)

        # Only descriptions with at least ten words.
        if len(re.split(r'[^0-9A-Za-z]+', description)) > 10:
            descriptions.append(description.strip('#').strip('@'))

    return descriptions


def get_tweets(api, twitter_user, tweet_type='timeline', max_tweets=200, min_words=5):
    tweets = []

    full_tweets = []
    step = 200  # Maximum value is 200.
    for start in range(0, max_tweets, step):
        end = start + step

        # Maximum of `step` tweets, or the remaining to reach max_tweets.
        count = min(step, max_tweets - start)

        kwargs = {'count': count}
        if full_tweets:
            last_id = full_tweets[-1].id
            kwargs['max_id'] = last_id - 1

        if tweet_type == 'timeline':
            current = api.user_timeline(twitter_user, **kwargs)
        else:
            current = api.favorites(twitter_user, **kwargs)

        full_tweets.extend(current)

    for tweet in full_tweets:
        text = re.sub(r'(https?://\S+)', '', tweet.text)

        score = tweet.favorite_count + tweet.retweet_count
        if tweet.in_reply_to_status_id_str:
            score -= 15

        # Only tweets with at least five words.
        if len(re.split(r'[^0-9A-Za-z]+', text)) > min_words:
            tweets.append((text, score))

    return tweets


def classify_batch(text_list, classifier_id, ml):
    module_id = 'cl_hDDngsX8'
    res = ml.classifiers.classify(classifier_id, text_list, sandbox=True)

    return res


def filter_language(texts, ml,MONKEYLEARN_LANG_CLASSIFIER_ID ,language='Spanish',):
    lang_classification = classify_batch(texts, MONKEYLEARN_LANG_CLASSIFIER_ID, ml)
    lang_texts = [
        text
        for text in texts for prediction in lang_classification.result
        if prediction[0]['label'] == language
        ]

    return lang_texts


def extract_keywords(text_list, max_keywords,MONKEYLEARN_EXTRACTOR_ID,ml):
    response = ml.extractors.extract(MONKEYLEARN_EXTRACTOR_ID, text_list)

    return response.result


"""
import multiprocessing.dummy as multiprocessing

BING_KEY = ''
EXPAND_TWEETS = False

def _bing_search(query):

    MAX_EXPANSIONS = 5

    params = {
        'Query': u"'{}'".format(query),
        '$format': 'json',
    }

    response = requests.get(
        'https://api.datamarket.azure.com/Bing/Search/v1/Web',
        params=params,
        auth=(BING_KEY, BING_KEY)
    )

    try:
        response = response.json()
    except ValueError as e:
        print( e)
        print( response.status_code)
        print( response.text)
        texts = []
        return
    else:
        texts = []
        for result in response['d']['results'][:MAX_EXPANSIONS]:
            texts.append(result['Title'])
            texts.append(result['Description'])

    return u" ".join(texts)


def _expand_text(text):
    result = text + u"\n" + _bing_search(text)
    print( result)
    return result


def expand_texts(texts):

    # First extract hashtags and keywords from the text to form the queries
    queries = []
    keyword_list = extract_keywords(texts, 10)
    for text, keywords in zip(texts, keyword_list):
        query = ' '.join([item['keyword'] for item in keywords])
        query = query.lower()
        tags = re.findall(r"#(\w+)", text)
        for tag in tags:
            tag = tag.lower()
            if tag not in query:
                query = tag + ' ' + query
        queries.append(query)

    pool = multiprocessing.Pool(2)
    return pool.map(_expand_text, queries)


# Use Bing search to expand the context of descriptions
expanded_descriptions = descriptions_english
#expanded_descriptions = expand_texts(descriptions_english)


# Use Bing search to expand the context of tweets
if EXPAND_TWEETS:
    expanded_tweets = expand_texts(tweets_english)
else:
    expanded_tweets = tweets_english

"""

def category_histogram(texts, short_texts, ml, MONKEYLEARN_TOPIC_CLASSIFIER_ID):
    # Classify the bios and tweets with MonkeyLearn's news classifier.
    topics = classify_batch(texts, MONKEYLEARN_TOPIC_CLASSIFIER_ID, ml)

    # The histogram will keep the counters of how many texts fall in
    # a given category.
    histogram = Counter()
    samples = {}

    for classification, text, short_text in zip(topics.result, texts, short_texts):

        # Join the parent and child category names in one string.
        category = classification[0]['label']
        probability = classification[0]['probability']

        if len(classification) > 1:
            category += '/' + classification[1]['label']
            probability *= classification[1]['probability']

        MIN_PROB = 0.0
        # Discard texts with a predicted topic with probability lower than a treshold
        if probability < MIN_PROB:
            continue

        # Increment the category counter.
        histogram[category] += 1

        # Store the texts by category
        samples.setdefault(category, []).append((short_text, text))

    return histogram, samples

def user_histogram(data,MONKEYLEARN_TOPIC_CLASSIFIER_ID,ml):

    total_histogram, data_categorized = category_histogram(data,data, ml,MONKEYLEARN_TOPIC_CLASSIFIER_ID)

    """
    # Print(the catogories sorted by most frequent)
    for topic, count in tweets_histogram.most_common():
        print(count, topic)
    """
    return total_histogram,data_categorized

def plot_histogram(top_categories,values):


    plt.figure(1, figsize=(5, 5))
    ax = plt.axes([0.1, 0.1, 0.8, 0.8])

    plt.pie(
        values,
        labels=top_categories,
        shadow=True,
        colors=[
            (0.86, 0.37, 0.34), (0.86, 0.76, 0.34), (0.57, 0.86, 0.34), (0.34, 0.86, 0.50),
            (0.34, 0.83, 0.86), (0.34, 0.44, 0.86), (0.63, 0.34, 0.86), (0.86, 0.34, 0.70),
        ],
        radius=20,
        autopct='%1.f%%',
    )

    plt.axis('equal')
    plt.show()

def keywords_user(tweets_categorized,top_categories,MONKEYLEARN_EXTRACTOR_ID,ml):
    joined_texts = {}

    for category in tweets_categorized:
        if category not in top_categories:
            continue

        expanded = 0
        joined_texts[category] = u' '.join(map(lambda t: t[expanded], tweets_categorized[category]))

    keywords = dict(zip(joined_texts.keys(), extract_keywords(joined_texts.values(), 20,MONKEYLEARN_EXTRACTOR_ID,ml)))
    return keywords

def analyze_user(twitter,ml,TWITTER_USER,language):
    MONKEYLEARN_LANG_CLASSIFIER_ID = 'cl_hDDngsX8'
    MONKEYLEARN_TOPIC_CLASSIFIER_ID = 'cl_5icAVzKR'
    MONKEYLEARN_AFILLIATE_ID = 'cl_zD7UNmJE'
    if language == "Spanish":
        MONKEYLEARN_EXTRACTOR_ID = 'ex_eV2dppYE'
        MONKEYLEARN_SENTIMENT_ID = 'cl_u9PRHNzf'
        MONKEYLEARN_ENTITY_ID = 'ex_Kc8uzhSi'
        MONKEYLEARN_NEWS_ID = 'cl_6hvxGfLu'
    else:
        MONKEYLEARN_EXTRACTOR_ID = 'ex_y7BPYzNG'
        MONKEYLEARN_SENTIMENT_ID = 'cl_qkjxv9Ly'
        MONKEYLEARN_ENTITY_ID = 'ex_isnnZRbS'
        MONKEYLEARN_NEWS_ID = 'cl_hS9wMk9y'

    tuple = twython_utils.get_tweets_by_entity(twitter,TWITTER_USER,max_tweets=2000,min_words=5)
    tweets = [x[0] for x in tuple[0]]
    mentions = [x[0] for x in tuple[1]]
    hashtags = tuple[2]
    #tweets += [x[0] for x in twython_utils.get_likes(twitter,TWITTER_USER,150)]
    descriptions = twython_utils.get_friends_descriptions(twitter,TWITTER_USER,max_users=500)
    #for i in tweets: print(i)
    #for i in descriptions: print(i)

    ##OJO LIST SET
    print(len(tweets))
    print(len(descriptions))
    print(len(mentions))
    descriptions_english = list(set((filter_language(descriptions, ml,MONKEYLEARN_LANG_CLASSIFIER_ID,language))))
    print("Descriptions found: {}".format(len(descriptions_english)))

    tweets_english = list(set(filter_language(tweets, ml,MONKEYLEARN_LANG_CLASSIFIER_ID,language)))
    print("Tweets found: {}".format(len(tweets_english)))
    mentions_filtered = set(filter_language(mentions, ml,MONKEYLEARN_LANG_CLASSIFIER_ID,language))
    print(len(mentions_filtered))
    mentions_to_filter = set(filter_language(list(mentions_filtered), ml,MONKEYLEARN_SENTIMENT_ID,"Negative"))
    mentions_filtered.difference(mentions_to_filter)
    mentions_filtered = list(mentions_filtered)
    print(len(mentions_filtered))

    max_categories = 6
    tweets_histogram,tweets_categorized = user_histogram(tweets_english,MONKEYLEARN_AFILLIATE_ID,ml)
    descriptions_histogram,descriptions_categorized = user_histogram(descriptions_english,MONKEYLEARN_AFILLIATE_ID,ml)
    mentions_histogram,mentions_categorized = user_histogram(mentions_filtered,MONKEYLEARN_AFILLIATE_ID,ml)


    top_tweets, values = zip(*tweets_histogram.most_common(max_categories))
    #plot_histogram(top_tweets,values)
    top_descriptions, values = zip(*descriptions_histogram.most_common(max_categories))
    #plot_histogram(top_descriptions,values)
    top_mentions, values = zip(*mentions_histogram.most_common(max_categories))
    #plot_histogram(top_mentions,values)

    #print(descriptions_categorized)
    keywords_tweets = keywords_user(tweets_categorized,top_tweets,MONKEYLEARN_EXTRACTOR_ID,ml)
    keywords_descriptions = keywords_user(descriptions_categorized,top_descriptions,MONKEYLEARN_EXTRACTOR_ID,ml)
    keywords_mentions = keywords_user(mentions_categorized,top_mentions,MONKEYLEARN_EXTRACTOR_ID,ml)

    for category in keywords_tweets:
        for word in keywords_tweets[category]:
            print("{}: {}, relevance:{}, count:{}".format(category,word['keyword'],word['relevance'],word['count']))
    for category in keywords_descriptions:
        for word in keywords_descriptions[category]:
            print("{}: {}, relevance:{}, count:{}".format(category,word['keyword'],word['relevance'],word['count']))
    for category in keywords_mentions:
        for word in keywords_mentions[category]:
            print("{}: {}, relevance:{}, count:{}".format(category,word['keyword'],word['relevance'],word['count']))
    #print(hashtags)
    results = []

    """
    for category in keywords_tweets:
        palabras = set([x['keyword'] for x in keywords_tweets[category]])
        for categorys in keywords_tweets:
            if category != categorys:
                palabrass = set([x['keyword'] for x in keywords_tweets[categorys]])
                results.extend(list(palabras.intersection(palabrass)))

    """
    resta = []
    for category in keywords_descriptions:
        palabras = set([x['keyword'] for x in keywords_descriptions[category]])
        for categorys in keywords_descriptions:
            if category != categorys:
                palabrass = set([x['keyword'] for x in keywords_descriptions[categorys]])
                resta.extend(list(palabras.intersection(palabrass)))

    for category in keywords_mentions:
        palabras = set([x['keyword'] for x in keywords_mentions[category]])
        for categorys in keywords_mentions:
            if category != categorys:
                palabrass = set([x['keyword'] for x in keywords_mentions[categorys]])
                results.extend(list(palabras.intersection(palabrass)))
    twits = []
    for category in keywords_tweets:
        for word in keywords_tweets[category]:
            twits.append(word['keyword'])

    descs = []
    for category in keywords_descriptions:
        for word in keywords_descriptions[category]:
            descs.append(word['keyword'])
    final_descs = set(descs).difference(set(resta))
    print(final_descs)
    menciones = []
    for category in keywords_mentions:
        for word in keywords_mentions[category]:
            menciones.append(word['keyword'])
    #inter = list(set(twits).intersection(set(descs)).intersection(set(menciones)))
    #print(inter)

    if results == []:
        words = []
        for category in top_mentions[0:2]:
            for word in keywords_mentions[category]:
                words.append(word)
        words = sorted(words, key = lambda x : x['relevance'])
        mid = len(words)//2
        results = [words[i]['keyword'] for i in range(mid-2,mid + 3)]



    return results

def recomender(twitter,ml,TWITTER_USER,language):
    results = list(set(analyze_user(twitter,ml,TWITTER_USER,language)))
    return results
    """
    palabras = {}

    for category in keywords:
        for i in range(len(keywords[category])):
            if i >= len(keywords[category]): break
            if keywords[category][i]['count'] == 0: del keywords[category][i]

    for category in top_categories[0:2]:
        keywords[category].sort(key=lambda x : x['count'])
        numeros = [float(keywords[category][i]['count']) for i in range(len(keywords[category]))]
        numeros_2 = list(scipy.stats.boxcox(numeros)[0])
        media = sum(numeros_2) / len(numeros_2)
        minimo = min(numeros_2, key = lambda x: abs(x - media))
        i = numeros_2.index(minimo)
        palabras[category] = [keywords[category][j]['keyword'] for j in range(i - 1, i + 2)]
    print(palabras)
    """
    nueva = []

    with open('stopwords.txt', 'r', errors='ignore') as archivo:
        words = set(apply_stemming([unidecode(p.strip()) for p in archivo.readlines()], stemmer_e))
        for keyword in results:
            elemento_steam = apply_stemming([keyword], stemmer)[0]
            if elemento_steam not in words:
                nueva.append(keyword)

    nueva_2 = []
    if language == 'Spanish':
        with open('listado-general.txt', 'r',errors='ignore') as archivo:
            words = set(apply_stemming([unidecode(p.strip()) for p in archivo.readlines()], stemmer))
            for keyword in nueva:
                elemento_steam = apply_stemming([keyword], stemmer)[0]
                if elemento_steam not in words:
                    nueva_2.append(keyword)

            nueva_2 = list(set(nueva_2))
            print(nueva_2)
            return nueva_2

    nueva = list(set(nueva))
    print(nueva)
    return nueva
if __name__ == '__main__':
    """
    TWITTER_CONSUMER_KEY = 'SJ3glU25jK3swUhRAraJ8GQXc'
    TWITTER_CONSUMER_SECRET = 'bfXDwwJIa2emh61MFNLSduMSGQx60VIHTcZmDuvoMg5zaVoDzm'
    TWITTER_ACCESS_TOKEN_KEY = '744463552992403456-51Ek3Oh2fFe52XxF1rvw29CG5uA1pFL'
    TWITTER_ACCESS_TOKEN_SECRET = 'j4laK9F7abRvcc0ZgkunMTWpdYEy4eZmQgBsSpbftOs7v'
    ml = MonkeyLearn('49f8003168af75e8a3eea233657dcb43da732f71')
    MONKEYLEARN_LANG_CLASSIFIER_ID = 'cl_hDDngsX8'
    MONKEYLEARN_TOPIC_CLASSIFIER_ID = 'cl_5icAVzKR'
    MONKEYLEARN_EXTRACTOR_ID = 'ex_eV2dppYE'
    TWITTER_USER = 'caro_achondo'
    # TWITTER_USER = 'agustin'
    """
    """
    auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
    auth.set_access_token(TWITTER_ACCESS_TOKEN_KEY, TWITTER_ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth)




    # Get the descriptions of the people that twitter_user is following.
    descriptions = get_friends_descriptions(api, TWITTER_USER, max_users=300)
    # print(descriptions)
    tweets = []
    tweets.extend(get_tweets(api, TWITTER_USER, 'timeline', 1000))  # 400 = 2 requests (out of 15 in the window).
    tweets.extend(get_tweets(api, TWITTER_USER, 'favorites', 400))  # 1000 = 5 requests (out of 180 in the window).
    tweets = list(map(lambda t: t[0], sorted(tweets, key=lambda t: t[1], reverse=True)))
    """
    """
    #twitter = Twython(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET , oauth_version=2)
    #ACCESS_TOKEN = twitter.obtain_access_token()
    #twitter = Twython(TWITTER_CONSUMER_KEY, access_token=ACCESS_TOKEN)
    twitter = Twython(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET ,TWITTER_ACCESS_TOKEN_KEY, TWITTER_ACCESS_TOKEN_SECRET)
    palabras = recomender(twitter,ml,TWITTER_USER,"Spanish")
    print(palabras)
    """