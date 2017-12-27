# Created by aviade      
# Time: 03/05/2016 09:00
from __future__ import print_function

import datetime
import re
import uuid
from datetime import timedelta

import unicodedata
from nltk.tokenize.simple import SpaceTokenizer


def str_to_date(datestring, formate="%Y-%m-%d %H:%M:%S"):
    return datetime.datetime.strptime(datestring, formate)


date = str_to_date


def date_to_str(datetimeObj, formate="%Y-%m-%d %H:%M:%S"):
    return datetimeObj.strftime(formate)


def cleaner(dirtyStr):
    # @review: cleaner of what?
    # @todo: refactor rename

    # from old clean data:
    afterOldCleandData = ""

    afterOldCleandData = dirtyStr.replace("<![CDATA[", "").replace("]]>", ""). \
        replace("\n", "").replace("\r\n", "").replace("\r", "").replace("\t", "")
    dashes = afterOldCleandData.find('#')
    if (dashes != -1):
        afterOldCleandData = afterOldCleandData[:dashes]
    if afterOldCleandData.endswith('/'):
        afterOldCleandData = afterOldCleandData[:-1]
    # from old clean url code:
    afterOldCleanUrl = afterOldCleandData.strip('\r\n\t')
    stripedStr = afterOldCleanUrl.strip("\r\n ")
    if stripedStr.startswith('"') or stripedStr.endswith('"'):
        stripedStr = stripedStr[1:-1]
    stripedStr = stripedStr.strip("(")
    stripedStr = stripedStr.strip(")")

    cleanStr = stripedStr.lstrip().rstrip()
    # cleanStr=cleanStr[:cleanStr.find('#')]
    return cleanStr


def cleanForAuthor(dirtyAuthorStr):
    sentToCleaner = dirtyAuthorStr.replace("-", "").replace(".", "")  # .lower()
    return cleaner(sentToCleaner)


def str_to_date(datestring, formate="%Y-%m-%d %H:%M:%S"):
    return datetime.datetime.strptime(datestring, formate)


def convert_str_to_unicode_datetime(str_date):
    str_date = unicode(str_date)
    unicode_str_date = unicodedata.normalize('NFKD', str_date).encode('ascii', 'ignore')
    date = str_to_date(unicode_str_date)
    return date


def get_current_time_as_string():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def compute_author_guid_by_author_name(author_name):
    from config_class import getConfig
    configInst = getConfig()
    prefix_osn_url = configInst.eval("DEFAULT", "social_network_url")
    author_url = prefix_osn_url + author_name

    # bytes = get_bytes(author_url)

    class NULL_NAMESPACE:
        bytes = b''

    author_guid = uuid.uuid3(NULL_NAMESPACE, author_url.encode('utf-8'))
    str_author_guid = unicode(str(author_guid))

    return str_author_guid

def compute_post_guid(post_url, author_name, str_publication_date):
    author_guid = compute_author_guid_by_author_name(author_name)
    publication_date = datetime.datetime.strptime(str_publication_date, '%Y-%m-%d %H:%M:%S')

    # adding two hours according to Henrik
    german_publication_date = publication_date + timedelta(hours=2)

    epoch = datetime.datetime.utcfromtimestamp(0)
    german_publication_date_in_milliseconds = int((german_publication_date - epoch).total_seconds() * 1000)

    str_german_publication_date_in_milliseconds = str(german_publication_date_in_milliseconds)

    url = post_url + "#" + author_guid + "#" + str_german_publication_date_in_milliseconds

    class NULL_NAMESPACE:
        bytes = b''

    post_guid = uuid.uuid3(NULL_NAMESPACE, url.encode('utf-8'))
    str_author_guid = unicode(str(post_guid))
    return str_author_guid
    '''

    long_publication_date = convert_date_to_long(publicationDate);
    String strLongPublicationDate = longPublicationDate.toString();

    System.out.println("Post url = " + postUrl);
    System.out.println("AuthorGuid = " + authorGuid);
    System.out.println("strLongPublicationDate = " + strLongPublicationDate);
    String url = postUrl + "#" + authorGuid + "#" + strLongPublicationDate;


    byte[] urlBytes = url.getBytes();
    UUID postGuid = UUID.nameUUIDFromBytes(urlBytes);
    String strPostGuid = postGuid.toString();

    System.out.println("Post: java.util.UUID .nameUUIDFromBytes((<URL> + \"#\" + <AUTHOR_GUID> + \"#\" + <PubDateAsLong>).getBytes())");
    System.out.println("POST GUID: "+ strPostGuid);
    '''


def retreive_valid_k(k, author_type_class_series):
    series_length = len(author_type_class_series)
    if series_length < k:
        return series_length
    else:
        return k


def retreive_labeled_authors_dataframe(targeted_class_name, dataframe):
    labeled_dataframe = dataframe.loc[dataframe[targeted_class_name].notnull()]
    return labeled_dataframe


def replace_nominal_class_to_numeric(dataframe, optional_classes):
    num_of_class = len(optional_classes)
    for i in range(num_of_class):
        class_name = optional_classes[i]
        dataframe = dataframe.replace(to_replace=class_name, value=i)
    return dataframe


def generate_tweet_url(tweet_id, tweet_author_name):
    '''
    :return: the URL of the retweeted tweet
    '''
    url = "https://twitter.com/{0}/status/{1}".format(tweet_author_name, tweet_id)
    return url


def extract_tweet_publiction_date(tweet_creation_time):
    '''
    :param tweet_creation_time: the time in which the tweet was published
    :return: the publication date of the tweet as a string.
    The time is CEST time.
    the structure of the time signature: YYYY-MM-DD HH:MM:SS
    '''
    utc_repr = datetime.datetime.strptime(tweet_creation_time, '%a %b %d %H:%M:%S +0000 %Y')
    cest_repr = utc_repr + timedelta(hours=2)
    return str(cest_repr)


def get_words_by_content(content):
        words = []
        tokenizer = SpaceTokenizer()
        words += tokenizer.tokenize(content)

        return words


def clean_word(word):
    return re.sub('[^a-zA-Z]+', '', word)
