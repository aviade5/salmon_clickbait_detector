'''
Created on 26  JUN  2016

@author: Jorge Bendahan (jorgeaug@post.bgu.ac.il)


This script is responsible for performing the following tasks:
DB: set up database connection
Preprocessor: performing stemming, stop words removal (look for the Preprocessor section in config.ini
BoostAuthorModel: calculating boost author scores
AutoTopicExecutor: running LDA algorithm(topic extraction) on the crawled posts
KeyAuthorModel: calcularing key author scores
FeatureExtractor: computing features for authors and writing the final dataset of author's features into an output file.
'''
import logging.config
import time

from commons.config_class import getConfig
from commons.schema_definition import DB
from experimental_enviorment.experimental_environment import ExperimentalEnvironment
from feature_generator.feature_extractor import FeatureExtractor
from feature_generator.image_recognition.image_tags_extractor import Image_Tags_Extractor
from importer.clickbait_challenge_importer import Clickbait_Challenge_Importer

###############################################################
# MODULES
###############################################################

moduleNames = {}
moduleNames["DB"] = DB  ## DB is special, it cannot be created using db.
moduleNames["Clickbait_Challenge_Importer"] = Clickbait_Challenge_Importer
moduleNames["Image_Tags_Extractor"] = Image_Tags_Extractor

moduleNames["FeatureExtractor"] = FeatureExtractor
moduleNames["ExperimentalEnvironment"] = ExperimentalEnvironment
# moduleNames["Clickbait_Challenge_Evaluator"] = Clickbait_Challenge_Evaluator
# moduleNames["Clickbait_Challenge_Predictor"] = Clickbait_Challenge_Predictor

###############################################################
## SETUP
logging.config.fileConfig(getConfig().get("DEFAULT", "Logger_conf_file"))
config = getConfig()
domain = unicode(config.get("DEFAULT", "domain"))
logging.info("Start Execution ... ")
logging.info("SETUP global variables")

window_start = config.eval("DEFAULT", "start_date")

logging.info("CREATE pipeline")
db = DB()
moduleNames["DB"] = lambda x: x
pipeline = []
for module in getConfig().sections():
    parameters = {}
    if moduleNames.get(module):
        pipeline.append(moduleNames.get(module)(db))

logging.info("SETUP pipeline")
bmrk = {"config": getConfig().getfilename(), "window_start": "setup"}

for module in pipeline:
    logging.info("setup module: {0}".format(module))
    T = time.time()
    module.setUp()
    T = time.time() - T
    bmrk[module.__class__.__name__] = T

clean_authors_features = getConfig().eval("DatasetBuilderConfig", "clean_authors_features_table")
if clean_authors_features:
    db.delete_authors_features()

###############################################################
## EXECUTE
bmrk = {"config": getConfig().getfilename(), "window_start": "execute"}
for module in pipeline:
    logging.info("execute module: {0}".format(module))
    T = time.time()
    logging.info('*********Started executing ' + module.__class__.__name__)

    module.execute(window_start)

    logging.info('*********Finished executing ' + module.__class__.__name__)
    T = time.time() - T
    bmrk[module.__class__.__name__] = T

num_of_authors = db.get_number_of_targeted_osn_authors(domain)
bmrk["authors"] = num_of_authors

num_of_posts = db.get_number_of_targeted_osn_posts(domain)
bmrk["posts"] = num_of_posts

if __name__ == '__main__':
    pass
