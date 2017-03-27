import sys
import os
import re
import csv
import time
import datetime

import feedparser
import requests
from requests.exceptions import HTTPError

# TODO: condition for when data is not available
try:
    import nltk
except:
    

import pandas