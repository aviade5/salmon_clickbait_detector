# Lior Bass 26.10.17

from Vectors_Operations import Vector_Operations
from feature_generator.base_feature_generator import BaseFeatureGenerator


class Word_Embeddings_Feature_Generator(BaseFeatureGenerator):
    def __init__(self, db, **kwargs):
        BaseFeatureGenerator.__init__(self, db, **kwargs)
        self._targeted_author_word_embeddings = self._config_parser.eval(self.__class__.__name__,
                                                                         "targeted_author_word_embeddings")

    def execute(self):
        for target_author_word_embeddings_dict in self._targeted_author_word_embeddings:
            targeted_table = target_author_word_embeddings_dict["table_name"]
            targeted_field_name = target_author_word_embeddings_dict["targeted_field_name"]
            targeted_word_embedding_type = target_author_word_embeddings_dict["word_embedding_type"]

            author_guid_word_embeding_dict = self._db.get_author_guid_word_embedding_vector_dict(targeted_table,
                                                                                                 targeted_field_name,
                                                                                                 targeted_word_embedding_type)
            authors_features = Vector_Operations.create_features_from_word_embedding_dict(
                author_guid_word_embeding_dict, targeted_table, targeted_field_name, targeted_word_embedding_type,
                self._window_start, self._window_end)
            self.insert_author_features_to_db(authors_features)
