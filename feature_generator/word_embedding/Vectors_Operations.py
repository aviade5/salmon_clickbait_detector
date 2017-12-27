from operator import sub

import commons
from feature_generator.base_feature_generator import BaseFeatureGenerator


class Vector_Operations():
    @staticmethod
    def create_authors_feature_from_two_vectors(func, first_author_vector_dict, second_author_vector_dict,
                                                first_table_name,
                                                first_targeted_field_name, first_word_embedding_type, second_table_name,
                                                second_targeted_field_name, second_word_embedding_type, window_start,
                                                window_end):
        authors_features = []
        for author_id in first_author_vector_dict.keys():
            feature_name = u"word_embeddings_sim_" + first_table_name + "_" + first_targeted_field_name + "_" + first_word_embedding_type + "_" \
                           + second_table_name + "_" + second_targeted_field_name + "_" + second_word_embedding_type + "_" + func
            first_vector = first_author_vector_dict[author_id]
            second_vector = second_author_vector_dict[author_id]
            # attribute_value = getattr(commons.commons, func)(first_vector, second_vector
            attribute_value = Vector_Operations.oparate_on_two_vectors(commons.commons, func,
                                                                       first_vector,
                                                                       second_vector)
            feature = BaseFeatureGenerator.create_author_feature(feature_name, author_id, attribute_value,
                                                                 window_start,
                                                                 window_end)
            authors_features.append(feature)
        return authors_features

    @staticmethod
    def oparate_on_two_vectors(func_location, func, vector_1, vector_2):
        value = getattr(func_location, func)(vector_1, vector_2)
        return value

    @staticmethod
    def create_features_from_word_embedding_dict(author_guid_word_embedding_dict, targeted_table, targeted_field_name,
                                                 targeted_word_embedding_type, window_start, window_end):
        authors_features = []
        for author_id in author_guid_word_embedding_dict.keys():
            author_vector = author_guid_word_embedding_dict[author_id]
            feature_name = targeted_table + "_" + targeted_field_name + "_" + targeted_word_embedding_type
            dimentions_feature_for_author = Vector_Operations.create_author_feature_for_each_dimention(author_vector,
                                                                                                       feature_name,
                                                                                                       author_id,
                                                                                                       window_start,
                                                                                                       window_end)
            authors_features = authors_features + dimentions_feature_for_author
        return authors_features

    @staticmethod
    def create_author_feature_for_each_dimention(vector, feature_name, author_id, window_start, window_end):
        authors_features = []
        prefix_name = u'word_embeddings_dimension_'
        dimension_counter = 0
        for dimension in vector:
            final_feature_name = prefix_name + str(
                dimension_counter) + "_" + feature_name
            dimension_counter = dimension_counter + 1
            feature = BaseFeatureGenerator.create_author_feature(final_feature_name, author_id, dimension, window_start,
                                                                 window_end)
            authors_features.append(feature)
        return authors_features

    @staticmethod
    def create_subtruction_dimension_features_from_authors_dict(first_author_guid_word_embedding_vector_dict,
                                                                second_author_guid_word_embedding_vector_dict,
                                                                first_table_name, first_targeted_field_name,
                                                                first_word_embedding_type, second_table_name,
                                                                second_targeted_field_name, second_word_embedding_type,
                                                                window_start, window_end):
        author_features = []
        for author_id in first_author_guid_word_embedding_vector_dict.keys():
            first_vector = first_author_guid_word_embedding_vector_dict[author_id]
            second_vector = second_author_guid_word_embedding_vector_dict[author_id]
            current_authors_feature = Vector_Operations.create_subtruction_dimention_features(first_vector,
                                                                                              second_vector,
                                                                                              first_table_name,
                                                                                              first_targeted_field_name,
                                                                                              first_word_embedding_type,
                                                                                              second_table_name,
                                                                                              second_targeted_field_name,
                                                                                              second_word_embedding_type,
                                                                                              window_start, window_end,
                                                                                              author_id)
            author_features = author_features + current_authors_feature
        return author_features

    @staticmethod
    def create_subtruction_dimention_features(vector_1, vector_2, first_table_name, first_targeted_field_name,
                                              first_word_embedding_type, second_table_name,
                                              second_targeted_field_name, second_word_embedding_type,
                                              window_start, window_end, author_id):
        result_vector = tuple(map(sub, vector_1, vector_2))
        feature_name = "subtruct_" + first_table_name + "_" + first_targeted_field_name + "_" + first_word_embedding_type + "_" + "to_" + \
                       second_table_name + "_" + second_targeted_field_name + "_" + second_word_embedding_type
        feature_id = author_id
        author_features = Vector_Operations.create_author_feature_for_each_dimention(result_vector, feature_name,
                                                                                     feature_id,
                                                                                     window_start, window_end)
        return author_features
