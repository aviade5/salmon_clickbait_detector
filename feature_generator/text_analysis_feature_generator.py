from __future__ import print_function

import logging

import nltk
from nltk import word_tokenize, map_tag
from nltk.corpus import stopwords
from nltk.corpus import words

from base_feature_generator import BaseFeatureGenerator
from commons import commons


class Text_Anlalyser_Feature_Generator(BaseFeatureGenerator):
    def __init__(self, db, **kwargs):
        BaseFeatureGenerator.__init__(self, db, **kwargs)
        self._targeted_fields = self._config_parser.eval(self.__class__.__name__, "targeted_fields")
        self._load_stop_words()
        self._words = words.words()
        self._author_id_texts_dict = {}
        self._features = self._config_parser.eval(self.__class__.__name__, "feature_list")
        self._authors = []
        self._multi_field_features = []
        self._authors = self._db.get_author_guid_to_author_dict()

    def execute(self):
        self._execute_single_target_field_execute()
        self._execute_multi_target_fields_execute()

    def _execute_single_target_field_execute(self):

        self._author_id_texts_dict = self.load_target_field_for_id(self._targeted_fields)
        for targeted_fields_dict in self._targeted_fields:
            counter = 0
            key_tuple = self.get_key_tuple(targeted_fields_dict)
            authors_features = []
            if len(self._author_id_texts_dict[key_tuple]) == 0:
                pass
            else:
                for post_id, texts in self._author_id_texts_dict[key_tuple].iteritems():
                    author_guid = self._db.get_author_id_by_field_id(targeted_fields_dict['id_field'], post_id)
                    author = self._authors[author_guid]
                    if counter % 100 == 0:
                        print("\rprocessing author " + str(counter), end="")
                    counter += 1
                    for feature in self._features:
                        feature_name = feature + "_" + key_tuple
                        author_feature = self.run_and_create_author_feature(author, feature, texts,
                                                                            unicode(feature_name), author_guid)
                        authors_features.append(author_feature)
            logging.info("processing author " + str(counter))
            self.insert_author_features_to_db(authors_features)

    def _execute_multi_target_fields_execute(self):
        counter = 0
        self._multi_field_features = self._config_parser.eval(self.__class__.__name__, u'multi_feature_target_fields')
        self._features = self._config_parser.eval(self.__class__.__name__, u'multi_feature_feature_list')
        self._multi_field_feature_functions = self._config_parser.eval(self.__class__.__name__,
                                                                       u'multi_feature_function_names')
        for multi_feald_feature in self._multi_field_features:
            feature_field1 = multi_feald_feature[0]
            feature_field2 = multi_feald_feature[1]
            author_id_texts_dict1 = self.load_target_field_for_id([feature_field1])
            key_tuple1 = self.get_key_tuple(feature_field1)
            key_tuple2 = self.get_key_tuple(feature_field2)
            author_id_texts_dict2 = self.load_target_field_for_id([feature_field2])
            for post_id in author_id_texts_dict1[key_tuple1].keys():
                if counter % 100 == 0:
                    print("\r multi field, finished processing author " + str(counter), end="")
                counter += 1
                authors_features = []
                author_guid = self._db.get_author_id_by_field_id(multi_feald_feature[0]['id_field'], post_id)
                author = self._authors[author_guid]
                for feature in self._features:
                    for function in self._multi_field_feature_functions:
                        feature_name = function + "_" + feature + "_" + key_tuple1 + "_to_" + key_tuple2
                        first_field_text = author_id_texts_dict1[key_tuple1][post_id]
                        second_field_text = author_id_texts_dict2[key_tuple2][post_id]
                        values_tupple = getattr(self, feature)(first_text_set=first_field_text,
                                                               second_text_set=second_field_text)
                        result = getattr(self, function)(values_tupple)
                        author_feature = self.run_and_create_author_feature_with_given_value(author_guid, result,
                                                                                             feature_name)
                        authors_features.append(author_feature)
            logging.info("finished processing author " + str(counter))
            self.insert_author_features_to_db(authors_features)

    def setUp(self):
        pass

    def cleanUp(self):
        pass

    def _get_post_by_author(self, kwargs):
        author = kwargs['author']
        author_guid = author.author_guid
        posts = self.author_guid_posts_dict[author_guid]
        post = posts[0]
        return post

    def _get_posts_by_author(self, kwargs):
        return kwargs["posts"]

    def num_of_chars_on_avg(self, **kwargs):
        posts = self._get_posts_by_author(kwargs)
        return self._calculate_avg_num_of_chars(posts)

    def _calculate_avg_num_of_chars(self, posts):
        if posts is None or len(posts) == 0:
            return -1
        counter = 0
        sum = 0
        for post in posts:
            if post is not None:
                stripped_post = post.replace(" ", "")
                sum = sum + len(stripped_post)
                counter = counter + 1
        if counter == 0:
            return 0
        return float(sum) / counter

    def num_of_verbse_on_avarage(self, **kwargs):
        posts = self._get_posts_by_author(kwargs)
        return self._avg_num_of_verbs(posts)

    def _avg_num_of_verbs(self, posts):
        if posts is None or len(posts) == 0:
            return -1
        counter = 0
        sum = 0
        for post in posts:
            if post is not None:
                sum = sum + self._num_of_verbs_in_sentence(post)
                counter = counter + 1
        if counter == 0:
            return 0
        return float(sum) / counter

    def _num_of_verbs_in_sentence(self, sentence):
        meaning_dict = self._get_meaning_set(sentence)
        if meaning_dict is None:
            return 0
        counter = 0
        for word in meaning_dict:
            if word[1] == 'VERB':
                counter = counter + 1
        if counter == 0:
            return 0
        return counter

    def num_of_adjectives_on_avg(self, **kwargs):
        posts = self._get_posts_by_author(kwargs)
        return self._avg_num_of_adjectives(posts)

    def _avg_num_of_adjectives(self, posts):
        if posts is None or len(posts) == 0:
            return -1
        counter = 0
        sum = 0
        for post in posts:
            if post is not None:
                sum = sum + self._num_of_adjs_in_sentence(post)
                counter = counter + 1
        if counter == 0:
            return 0
        return float(sum) / counter

    def _num_of_adjs_in_sentence(self, sentence):
        meaning_dict = self._get_meaning_set(sentence)
        if meaning_dict is None:
            return 0
        counter = 0
        for word in meaning_dict:
            if word[1] == 'ADJ':
                counter = counter + 1
        if counter == 0:
            return 0
        return counter

    def num_of_nouns_on_avg(self, **kwargs):
        posts = self._get_posts_by_author(kwargs)
        return self._avg_num_of_nouns(posts)

    def _avg_num_of_nouns(self, posts):
        if posts is None or len(posts) == 0:
            return -1
        counter = 0
        sum = 0
        for post in posts:
            if post is not None:
                sum = sum + self._num_of_nouns_in_sentence(post)
                counter = counter + 1
        if counter == 0:
            return 0
        return float(sum) / counter

    def _num_of_nouns_in_sentence(self, sentence):
        meaning_dict = self._get_meaning_set(sentence)
        if meaning_dict is None:
            return 0
        counter = 0
        for word in meaning_dict:
            if word[1] == 'NOUN':
                counter = counter + 1
        return counter

    def _get_meaning_set(self, sentence):
        if sentence is None or sentence == u'':
            return None
        tags = word_tokenize(sentence)
        proccessed_tags = nltk.pos_tag(tags)
        simplified_tags = [(word, map_tag('en-ptb', 'universal', tag)) for word, tag in proccessed_tags]
        return simplified_tags

    def num_of_quotations_on_avg(self, **kwargs):
        posts = self._get_posts_by_author(kwargs)
        return self._avg_num_of_quotations(posts)

    def _avg_num_of_quotations(self, posts):
        if posts is None or len(posts) == 0:
            return -1
        counter = 0
        sum = 0
        for post in posts:
            sum = sum + self._contains_quotations(post)
            counter = counter + 1
        if counter == 0:
            return 0
        return float(sum) / counter

    def _contains_quotations(self, content):
        if content is None:
            return 0
        sum = 0
        for char in content:
            if char == "\"":
                sum += 1
        return sum / 2

    def _load_stop_words(self):
        self._stopwords_set = stopwords.words(u'english')

    def num_of_uppercase_words_in_post_on_avg(self, **kwargs):
        posts = self._get_posts_by_author(kwargs)
        return self._avg_num_of_uppercase_words(posts)

    def _avg_num_of_uppercase_words(self, posts):
        if posts is None or len(posts) == 0:
            return -1
        counter = 0
        sum = 0
        for post in posts:
            sum = sum + self._count_uppercase_words_in_sentence(post)
            counter = counter + 1
        if counter == 0:
            return 0
        return float(sum) / counter

    def number_of_precent_of_uppercased_posts(self, **kwargs):
        posts = self._get_posts_by_author(kwargs)
        if posts is None or len(posts) == 0:
            return -1
        counter = 0
        for post in posts:
            counter = counter + self._are_all_sentence_words_uppercase(post)
        return float(counter) / len(posts)

    def _are_all_sentence_words_uppercase(self, sentence):
        if sentence is None or sentence == u'':
            return 0
        num_of_uppercase_words = self._count_uppercase_words_in_sentence(sentence)
        total_num_of_words = len(sentence.split())
        if num_of_uppercase_words == total_num_of_words:
            return 1
        else:
            return 0

    def _count_uppercase_words_in_sentence(self, sentence):
        counter = 0
        if sentence is None:
            return 0
        for word in sentence.split():
            if word.isupper():
                counter = counter + 1
        return counter

    def num_of_formal_words_on_avg(self, **kwargs):
        posts = self._get_posts_by_author(kwargs)
        return self._avg_num_of_formal_words(posts)

    def _avg_num_of_formal_words(self, posts):
        sum = 0
        if posts is None or len(posts) == 0:
            return -1
        for post in posts:
            sum = sum + self._count_formal_words_in_sentence(post)
        return float(sum) / len(posts)

    def num_of_informal_words_on_avg(self, **kwargs):
        posts = self._get_posts_by_author(kwargs)
        return self._avg_num_of_informal_words(posts)

    def _avg_num_of_informal_words(self, posts):
        sum = 0
        if posts is None or len(posts) == 0:
            return -1
        for post in posts:
            sum = sum + self._count_informal_words_in_sentence(post)
        return float(sum) / len(posts)

    def precent_of_formal_words_on_avg(self, **kwargs):
        posts = self._get_posts_by_author(kwargs)
        if posts is None or len(posts) == 0:
            return -1
        sum = 0
        for post in posts:
            sum = sum + self._precent_of_formal_words_in_sentence(post)
        return float(sum) / len(posts)

    def _precent_of_formal_words_in_sentence(self, sentence):
        if sentence is None or sentence == u'':
            return 0
        num_of_formal_words = self._count_formal_words_in_sentence(sentence)
        return float(num_of_formal_words) / len(sentence.split())

    def _precent_of_informal_words_in_sentence(self, sentence):
        return 1 - self._precent_of_formal_words_in_sentence(sentence)

    def _count_formal_words_in_sentence(self, sentence):
        if sentence is None or sentence == u'':
            return 0
        counter = 0
        clean_words = self._clean_words(sentence.split())
        for word in clean_words:
            if word.lower() in self._words:
                counter = counter + 1
        return counter

    def _count_informal_words_in_sentence(self, sentence):
        if sentence is None or sentence == u'':
            return 0
        counter = 0
        clean_words = self._clean_words(sentence.split())
        for word in clean_words:
            if word.lower() not in self._words:
                counter = counter + 1
        return counter

    def _clean_words(self, words_list):
        clean_words = []
        for word in words_list:
            clean_words.append(commons.clean_word(word))
        return clean_words

    def num_of_question_marks_on_avg(self, **kwargs):
        posts = self._get_posts_by_author(kwargs)
        if posts is None or len(posts) == 0:
            return -1
        selected_sign = '?'
        sum = 0
        for post in posts:
            sum = sum + self._calculate_num_of_given_signs_by_content(selected_sign, post)
        return float(sum) / len(posts)

    def _calculate_num_of_given_signs_by_content(self, selected_sign, content):
        if content is None or content == u'':
            return 0
        num_of_signs = content.count(unicode(selected_sign))
        return num_of_signs

    def num_of_colons_on_avg(self, **kwargs):
        posts = self._get_posts_by_author(kwargs)
        if posts is None or len(posts) == 0:
            return -1
        selected_sign = ':'
        sum = 0
        for post in posts:
            sum = sum + self._calculate_num_of_given_signs_by_content(selected_sign, post)
        return float(sum) / len(posts)

    def num_of_comas_on_avg(self, **kwargs):
        posts = self._get_posts_by_author(kwargs)
        if posts is None or len(posts) == 0:
            return -1
        selected_sign = ','
        sum = 0
        for post in posts:
            sum = sum + self._calculate_num_of_given_signs_by_content(selected_sign, post)
        return float(sum) / len(posts)

    def num_of_retweets_on_avg(self, **kwargs):
        posts = self._get_posts_by_author(kwargs)
        if posts is None or len(posts) == 0:
            return -1
        selected_sign = 'RT'
        sum = 0
        for post in posts:
            sum = sum + self._calculate_num_of_given_signs_by_content(selected_sign, post)
        return float(sum) / len(posts)

    def num_of_ellipsis_on_avg(self, **kwargs):
        posts = self._get_posts_by_author(kwargs)
        if posts is None or len(posts) == 0:
            return -1
        selected_sign = '...'
        sum = 0
        for post in posts:
            sum = sum + self._calculate_num_of_given_signs_by_content(selected_sign, post)
        return float(sum) / len(posts)

    def _count_stop_words_in_sentence(self, sentence):
        if sentence is None or sentence == u'':
            return 0
        counter = 0
        clean_words = self._clean_words(sentence.split())
        for word in clean_words:
            if word in self._stopwords_set:
                counter = counter + 1
        return counter

    def _count_precent_of_stop_words_in_sentence(self, sentence):
        if sentence is None or sentence == u'':
            return 0
        num_of_stop_words = self._count_stop_words_in_sentence(sentence)
        num_of_words = len(sentence.split())
        if num_of_stop_words == 0:
            return 0
        return float(num_of_stop_words) / num_of_words

    def num_of_stop_words_on_avg(self, **kwargs):
        posts = self._get_posts_by_author(kwargs)
        return self._avg_num_of_stopwords(posts)

    def _avg_num_of_stopwords(self, posts):
        if posts is None or len(posts) == 0:
            return -1
        counter = 0
        sum = 0
        for post in posts:
            sum = sum + self._count_stop_words_in_sentence(post)
            counter = counter + 1
        if counter == 0:
            return 0
        return float(sum) / counter

    def precent_of_stop_words_on_avg(self, **kwargs):
        posts = self._get_posts_by_author(kwargs)
        if posts is None or len(posts) == 0:
            return -1
        counter = 0
        sum = 0
        for post in posts:
            sum = sum + self._count_precent_of_stop_words_in_sentence(post)
            counter = counter + 1
        if counter == 0:
            return 0
        return float(sum) / counter

    def diffarence(self, tupple):
        return tupple[0] - tupple[1]

    def ratio(self, tupple):
        if tupple[1] == 0:
            return 0.0
        return float(tupple[0]) / tupple[1]

    def num_of_characters(self, first_text_set, second_text_set):
        avg_num1 = self._calculate_avg_num_of_chars(first_text_set)
        avg_num2 = self._calculate_avg_num_of_chars(second_text_set)
        return (avg_num1, avg_num2)

    def num_of_verbse(self, first_text_set, second_text_set):
        avg_num1 = self._avg_num_of_verbs(first_text_set)
        avg_num2 = self._avg_num_of_verbs(second_text_set)
        return (avg_num1, avg_num2)

    def num_of_nouns(self, first_text_set, second_text_set):
        avg_num1 = self._avg_num_of_nouns(first_text_set)
        avg_num2 = self._avg_num_of_nouns(second_text_set)
        return (avg_num1, avg_num2)

    def num_of_adj(self, first_text_set, second_text_set):
        avg_num1 = self._avg_num_of_adjectives(first_text_set)
        avg_num2 = self._avg_num_of_adjectives(second_text_set)
        return (avg_num1, avg_num2)

    def num_of_quotations(self, first_text_set, second_text_set):
        avg_num1 = self._avg_num_of_quotations(first_text_set)
        avg_num2 = self._avg_num_of_quotations(second_text_set)
        return (avg_num1, avg_num2)

    def num_of_uppercase_words(self, first_text_set, second_text_set):
        avg_num1 = self._avg_num_of_uppercase_words(first_text_set)
        avg_num2 = self._avg_num_of_uppercase_words(second_text_set)
        return (avg_num1, avg_num2)

    def num_of_foraml_words(self, first_text_set, second_text_set):
        avg_num1 = self._avg_num_of_formal_words(first_text_set)
        avg_num2 = self._avg_num_of_formal_words(second_text_set)
        return (avg_num1, avg_num2)

    def num_of_informal_words(self, first_text_set, second_text_set):
        avg_num1 = self._avg_num_of_informal_words(first_text_set)
        avg_num2 = self._avg_num_of_informal_words(second_text_set)
        return (avg_num1, avg_num2)

    def num_of_stopwords(self, first_text_set, second_text_set):
        avg_num1 = self._avg_num_of_stopwords(first_text_set)
        avg_num2 = self._avg_num_of_stopwords(second_text_set)
        return (avg_num1, avg_num2)
