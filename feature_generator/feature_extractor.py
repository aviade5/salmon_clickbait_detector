# Created by Jorge Bendahan (jorgeaug@post.bgu.ac.il) at 10/04/2016
# Ben Gurion University of the Neguev - Department of Information Systems Engineering

import logging
import time

from commons.abstract_controller import AbstractController
from commons.config_class import getConfig
from feature_generator.account_properties_feature_generator import AccountPropertiesFeatureGenerator
from feature_generator.clickbait_feature_generator import Clickbait_Feature_Generator
from feature_generator.sentiment_feature_generator import Sentiment_Feature_Generator
from feature_generator.text_analysis_feature_generator import Text_Anlalyser_Feature_Generator
from image_tags_feature_generator import Image_Tags_Feature_Generator
from ocr_feature_generator import OCR_Feature_Generator

'''
This class is responsible for executing all the FeatureGenerator classes and finally calling ArffWriter class which
writes all the generated features to an output file
'''


class FeatureExtractor(AbstractController):
    def __init__(self, db, **kwargs):
        AbstractController.__init__(self, db)
        self.config_parser = getConfig()
        # self._table_name = self._config_parser.get(self.__class__.__name__, "table_name")

    def setUp(self):
        pass

    def execute(self, window_start=None, window_end=None):
        start_time = time.time()
        info_msg = "execute started for " + self.__class__.__name__ + " started at " + str(start_time)
        print info_msg
        logging.info(info_msg)

        ###############################################################
        # MODULES
        ###############################################################
        module_names = {}

        module_names["OCR_Feature_Generator"] = OCR_Feature_Generator
        module_names["Image_Tags_Feature_Generator"] = Image_Tags_Feature_Generator
        module_names["Clickbait_Feature_Generator"] = Clickbait_Feature_Generator
        module_names["Sentiment_Feature_Generator"] = Sentiment_Feature_Generator
        module_names["Text_Anlalyser_Feature_Generator"] = Text_Anlalyser_Feature_Generator
        module_names["AccountPropertiesFeatureGenerator"] = AccountPropertiesFeatureGenerator
        # module_names["Word_Embeddings_Comparison_Feature_Generator"] = Word_Embeddings_Comparison_Feature_Generator
        # module_names["Word_Embeddings_Feature_Generator"] = Word_Embeddings_Feature_Generator

        ###############################################################
        ## SETUP
        logging.config.fileConfig(getConfig().get("DEFAULT", "Logger_conf_file"))
        logging.info("Start Execution ... ")
        logging.info("SETUP global variables")
        window_start = getConfig().eval("DEFAULT", "start_date")
        logging.info("CREATE pipeline")

        pipeline = []
        authors = self._db.get_authors_by_domain(self._domain)
        posts = self._db.get_posts_by_domain(self._domain)
        graphs = {}

        parameters = {"authors": authors, "posts": posts, "graphs": graphs}

        for module in self._config_parser.sections():
            if module_names.get(module):
                if module.startswith("GraphFeatureGenerator") or module.startswith(
                        "DistancesFromTargetedClassFeatureGenerator"):
                    self._add_graph_features_to_params(module, parameters)

                pipeline.append(module_names.get(module)(self._db, **parameters))

        for module in pipeline:
            logging.info("execute module: {0}".format(module))
            T = time.time()
            logging.info('*********Started executing ' + module.__class__.__name__)

            module.execute()

            logging.info('*********Finished executing ' + module.__class__.__name__)
            T = time.time() - T

        end_time = time.time()
        diff_time = end_time - start_time
        info_msg = "execute finished for " + self.__class__.__name__ + "  in " + str(diff_time) + " seconds"
        print info_msg
        logging.info(info_msg)

    def _add_graph_features_to_params(self, module, parameters):

        graph_types = self._config_parser.eval(module, "graph_types")
        graph_directed = self._config_parser.eval(module, "graph_directed")
        graph_weights = self._config_parser.eval(module, "graph_weights")
        parameters.update({"graph_types": graph_types,
                           "graph_directed": graph_directed, "graph_weights": graph_weights})

        if self._config_parser.has_option(module, "algorithms"):
            algorithms = self._config_parser.eval(module, "algorithms")
            parameters.update({"algorithms": algorithms})

        if self._config_parser.has_option(module, "aggregation_functions"):
            aggregations = self._config_parser.eval(module, "aggregation_functions")
            parameters.update({"aggregation_functions": aggregations})

        if self._config_parser.has_option(module, "neighborhood_sizes"):
            neighborhood_sizes = self._config_parser.eval(module, "neighborhood_sizes")
            parameters.update({"neighborhood_sizes": neighborhood_sizes})
