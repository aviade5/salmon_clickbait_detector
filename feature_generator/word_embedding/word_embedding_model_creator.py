from __future__ import print_function

import os

import numpy as np
import pandas as pd

from commons.abstract_controller import AbstractController
from commons.commons import *


class Word_Embedding_Model_Creator(AbstractController):
    def __init__(self, db):
        AbstractController.__init__(self, db)
        self._is_load_wikipedia_300d_glove_model = self._config_parser.eval(self.__class__.__name__,
                                                                            "is_load_wikipedia_300d_glove_model")
        self._wikipedia_model_file_path = self._config_parser.eval(self.__class__.__name__, "wikipedia_model_file_path")
        self._table_name = self._config_parser.eval(self.__class__.__name__, "table_name")
        self._targeted_fields_for_embedding = self._config_parser.eval(self.__class__.__name__,
                                                                       "targeted_fields_for_embedding")
        self._word_vector_dict = {}
        # key = author_id (could be author_guid, or other field) and array of the contents (maybe the author has many posts' content)
        self._author_id_texts_dict = {}
        self._author_id_words = {}
        self._word_vector_dict_full_path = "data/output/word_embedding/"
        self._aggregation_functions_names = self._config_parser.eval(self.__class__.__name__,
                                                                     "aggregation_functions_names")

    def setUp(self):
        if not os.path.exists(self._word_vector_dict_full_path):
            os.makedirs(self._word_vector_dict_full_path)

    def execute(self, window_start):
        if self._is_load_wikipedia_300d_glove_model:
            if not self._db.is_table_exist(self._table_name):
                self._load_wikipedia_300d_glove_model()
            self._fill_author_id_text_dictionary()
            self._calculate_word_embedding_to_authors()

    def _load_wikipedia_300d_glove_model(self):
        logging.info("_load_wikipedia_300d_glove_model")
        dataframe = pd.DataFrame()

        with open(self._wikipedia_model_file_path, 'r') as file:
            i = 1
            for line in file:
                msg = '\r Reading line #' + str(i)
                print(msg, end="")
                i += 1
                word_vector_array = line.split(' ')
                word = unicode(word_vector_array[0], 'utf-8')
                vector_str = word_vector_array[1:]
                vector_str = np.array(vector_str)
                vector = vector_str.astype(np.float)
                dataframe[word] = vector

        dataframe = dataframe.T
        info_msg = "\r transposed dataframe"
        print(info_msg, end="")
        # add the index as column before removing the index
        dataframe['word'] = dataframe.index
        # Change the order - the index column now first.
        cols = dataframe.columns.tolist()
        cols = cols[-1:] + cols[:-1]
        dataframe = dataframe[cols]

        info_msg = "\r  remove the index"
        print(info_msg, end="")

        engine = self._db.engine
        # index = false is important for removing index.
        dataframe.to_sql(name=self._table_name, con=engine, index=False)

        # save model
        if not os.path.exists(self._word_vector_dict_full_path):
            os.makedirs(self._word_vector_dict_full_path)

    def _fill_author_id_text_dictionary(self):
        for targeted_fields_dict in self._targeted_fields_for_embedding:
            table_name = targeted_fields_dict["table_name"]
            id_field = targeted_fields_dict["id_field"]
            targeted_field_name = targeted_fields_dict["targeted_field_name"]
            where_clauses = targeted_fields_dict["where_clauses"]

            key_tuple = self._create_key_for_dictionary(table_name, id_field, targeted_field_name, where_clauses)

            self._author_id_texts_dict[key_tuple] = {}
            tuples = self._db.get_targeted_records_by_id_targeted_field_and_table_name(id_field, targeted_field_name,
                                                                                       table_name, where_clauses)
            i = 1
            for tuple in tuples:
                msg = '\r Reading tuple #' + str(i) + "from table " + table_name
                print(msg, end="")
                i += 1
                author_id = tuple[0]
                # text could be content, description, etc
                text = tuple[1]
                if author_id is not None or text is not None:
                    if len(text) > 0:
                        if author_id not in self._author_id_texts_dict[key_tuple]:
                            self._author_id_texts_dict[key_tuple][author_id] = []
                            self._author_id_texts_dict[key_tuple][author_id].append(text)
                        else:
                            self._author_id_texts_dict[key_tuple][author_id].append(text)
                    else:  # added by Lior
                        if author_id not in self._author_id_texts_dict[key_tuple].keys():
                            self._author_id_texts_dict[key_tuple][author_id] = []

    def _calculate_word_embedding_to_authors(self):
        self._fill_author_id_words_dictionary()
        self._word_vector_dict = self._db.get_word_vector_dictionary(self._table_name)

        self._results_dataframe = pd.DataFrame()
        for targeted_fields_dict in self._targeted_fields_for_embedding:
            table_name = targeted_fields_dict["table_name"]
            id_field = targeted_fields_dict["id_field"]
            targeted_field_name = targeted_fields_dict["targeted_field_name"]
            where_clauses = targeted_fields_dict["where_clauses"]

            key_tuple = self._create_key_for_dictionary(table_name, id_field, targeted_field_name, where_clauses)
            print("Starting calculating word embeddings for: {}".format(key_tuple))

            for author_id, words in self._author_id_words[key_tuple].iteritems():
                word_vectors = self._collect_word_vector_per_author(author_id, words)

                # if len(word_vectors) == 0:
                #     continue
                transposed = zip(*word_vectors)

                self._fill_results_dataframe(author_id, table_name, id_field, targeted_field_name, transposed)
                print("Finishing calculating word embeddings for: {}".format(key_tuple))

        # if result is None: #added by Lior, need to check for if no author_id
        #     self._fill_zeros(results_dataframe, author_id, table_name, id_field, targeted_field_name)
        column_names = ["author_id", "table_name", "id_field", "targeted_field_name", "word_embedding_type"]
        dimensions = np.arange(300)
        column_names.extend(dimensions)
        self._results_dataframe.columns = column_names

        engine = self._db.engine
        self._results_dataframe.to_sql(name="author_word_embeddings", con=engine, index=False)

    def _clean_word(self, word):
        return re.sub('[^a-zA-Z]+', '', word)

    # added by Lior
    def _fill_zeros(self, results_dataframe, author_id, table_name, id_field, targeted_field_name):
        for aggregation_function_name in self._aggregation_functions_names:
            author_vector = [author_id, table_name, id_field, targeted_field_name,
                             aggregation_function_name]
            zero_vector = np.zeros((300,), dtype=np.int)
            author_vector.extend(zero_vector)
            series = pd.Series(data=author_vector)
            results_dataframe = results_dataframe.append(series, ignore_index=True)

    def _create_key_for_dictionary(self, table_name, id_field, targeted_field_name, where_clauses):
        key_tuple = table_name + "-" + id_field + "-" + targeted_field_name

        where_clause_dict = where_clauses[0]
        values = where_clause_dict.values()
        if values[0] != 1 and values[1] != 1:
            additional_str = u""
            for value in values:
                additional_str += "_" + value
            key_tuple += "_" + additional_str
        return key_tuple

    def _fill_author_id_words_dictionary(self):
        print("Starting fill_author_id_words_dictionary")
        for targeted_fields_dict in self._targeted_fields_for_embedding:
            table_name = targeted_fields_dict["table_name"]
            id_field = targeted_fields_dict["id_field"]
            targeted_field_name = targeted_fields_dict["targeted_field_name"]
            where_clauses = targeted_fields_dict["where_clauses"]

            key_tuple = self._create_key_for_dictionary(table_name, id_field, targeted_field_name, where_clauses)
            print("Starting filling author_id_words_dictionary for: {}".format(key_tuple))
            self._author_id_words[key_tuple] = {}

            for author_id, texts in self._author_id_texts_dict[key_tuple].iteritems():
                total_words = []
                for text in texts:
                    if text is not None:
                        # print("author_guid = " + author_id, "text =" + text)
                        words = get_words_by_content(text)
                        total_words += words
                self._author_id_words[key_tuple][author_id] = total_words
            print("Finishing filling author_id_words_dictionary for: {}".format(key_tuple))
        print("Finishing fill_author_id_words_dictionary")

    def _collect_word_vector_per_author(self, author_id, words):
        word_vectors = []
        for word in words:
            if word in self._word_vector_dict:
                word_vector = self._word_vector_dict[word]
                word_vectors.append(word_vector)
            else:  # added by Lior
                clean_word = self._clean_word(word)
                if clean_word in self._word_vector_dict:
                    word_vector = self._word_vector_dict[clean_word]
                    word_vectors.append(word_vector)
        return word_vectors

    def _fill_results_dataframe(self, author_id, table_name, id_field, targeted_field_name, transposed):
        for aggregation_function_name in self._aggregation_functions_names:
            author_vector = [author_id, table_name, id_field, targeted_field_name,
                             aggregation_function_name]

            result = map(eval(aggregation_function_name), transposed)
            if len(result) > 0:
                author_vector.extend(result)
                series = pd.Series(data=author_vector)
                self._results_dataframe = self._results_dataframe.append(series, ignore_index=True)
            else:
                zero_vector = np.zeros((300,), dtype=np.int)
                author_vector.extend(zero_vector)
                series = pd.Series(data=author_vector)
                self._results_dataframe = self._results_dataframe.append(series, ignore_index=True)
