import sys
import os
import re
import csv
import time
import datetime

import feedparser
import requests
from requests.exceptions import HTTPError

import nltk
import pandas


#TODO: OOP

class ScholarArticle(object):
    """
    A class representing articles listed on arxiv (basic dictionary-like behavior)
    """
    def __init__(self):
        self.attrs():