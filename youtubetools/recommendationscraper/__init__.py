"""
provides functions to collect and process YouTube video recommendations
"""
from youtubetools.recommendationscraper.spider import get_recommendation_tree
from youtubetools.recommendationscraper.treetools import flatten_dict
from youtubetools.recommendationscraper.loggedin import create_personalized_rec_collection
