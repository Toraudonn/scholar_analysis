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


class Arxiv(object):

    def __init__(self):
        self.date_format = '%Y-%m-%dT%H:%M:%SZ'  #Formatting directives
        self.root_url = 'http://export.arxiv.org/api/'
        self.qsearch = "query?search_query="


    def count_total_papers(self, category):
        # category = stat.ML
        url = self.root_url + self.qsearch + "cat:" + category + "&start=0&sortBy=submittedDate&sortOrder=descending&max_results=1"
        d = feedparser.parse(url)
        print('status: ' + str(d['status']))
        if d['status'] != 200:
            print("cannot GET url...")
            return None
        else:
            return int(d['feed']['opensearch_totalresults'])

    def retrieve_results(self, url):
        return feedparser.parse(url)['entries']

    def open_data(self, output_type, cat, dir_):
        if output_type == 1:
            return open('./'+dir_+'_csv/'+cat+'.csv', 'a')
        elif output_type == 2:
            return open('./'+dir_+'_txt/'+cat+'.txt', 'a')
        else:
            return None

    def refactor_data(self, result, output_type):
        fd = FormatData()
        link = result['link']
        try:
            pdf = result['links'][1]['href']
        except:
            pdf = ''
        title = result['title']
        summary = result['summary']
        authors = result['authors']
        tags = result['tags']
        if output_type == 1:
            title = title.replace(',', '')
            summary = summary.replace(',', '')
            # make authors into one string
            author_names = fd.arr2csv(authors, 'name')
            # get category keyword
            tag_names = fd.arr2csv(tags, 'term')
        else:
            author_names = fd.arr2psv(authors, 'name')
            tag_names = fd.arr2psv(tags, 'term')
        return [link, pdf, title, summary, author_names, tag_names]

class DailyDataRetriever(Arxiv):
    '''
    object for getting daily data
    '''
    def __init__(self, output_type=0, delay=2):
        Arxiv.__init__(self)
        self.delay = delay # number of day to delay
        self.output_type = output_type
        pass

    def daily_data(self, cat, delay):
        f = self.open_data(self.output_type, cat.replace('.',''), 'daily')
        if not (f is None):
            for n in range(0, 10):
                results = self.retrieve_results(root_url + qsearch + "cat:" + cat + "&start=" + str(n*10) + "&sortBy=submittedDate&sortOrder=descending&max_results=10")
                for result in results:
                    # get today's time
                    unix_epoch = time.time()   #the popular UNIX epoch time in seconds
                    ts = datetime.datetime.fromtimestamp(unix_epoch)
                    today = ts.strftime(date_format)
                    updated = result['updated']
                    us = datetime.datetime.strptime(updated, date_format)
                    if (ts - us).days == delay:
                        raw = [str(today), updated].append(self.refactor_data(result), self.output_type)
                        if self.output_type == 1:
                            writer = csv.writer(f)
                            writer.writerow(raw)
                        else:
                            writer = csv.writer(f, delimiter='|')
                            writer.writerow(raw)
            f.close()
        else:
            print("cannot save to directory...")


class TestDataRetriever(Arxiv):
    '''
    object for getting test data for analysis
    '''
    def __init__(self, total_paper=100, max_number=10):
        Arxiv.__init__(self)
        self.total_paper = total_paper # number of total papers to get
        self.max_number = max_number # number of papers per each api requests (maximum request size is 10)
        pass

    def data_print(self, cat, N):
        if N < self.total_paper:
            total_paper_ = N
        else:
            total_paper_=self.total_paper
        remainder = total_paper_%self.max_number
        num_run = total_paper_//self.max_number
        if remainder > 0:
            num_run += 1

        for n in range(0, num_run):
            url = self.root_url + self.qsearch + "cat:" + cat+ "&start=" + str(n*self.max_number) + "&sortBy=submittedDate&sortOrder=descending&max_results=" + str(self.max_number)
            d = feedparser.parse(url)
            results = d['entries']
            for result in results:
                data = self.test_data_refactor(result, True)
                print("============================================")
                for i in data:
                    print(i)

            # wait 3 seconds (for safety)
            time.sleep(3)

    def data2csv(self, cat, N):
        if N < self.total_paper:
            total_paper_ = N
        else:
            total_paper_=self.total_paper
        remainder = total_paper_%self.max_number
        num_run = total_paper_//self.max_number
        if remainder > 0:
            num_run += 1

        f = open('./test_csv/'+cat.replace('.', '')+'.csv', 'a')

        for n in range(0, num_run):
            url = self.root_url + self.qsearch + "cat:" + cat+ "&start=" + str(n*self.max_number) + "&sortBy=submittedDate&sortOrder=descending&max_results=" + str(self.max_number)
            d = feedparser.parse(url)
            results = d['entries']
            for result in results:
                data = self.test_data_refactor(result, False)
                writer = csv.writer(f)
                writer.writerow(data)

            # wait 3 seconds (for safety)
            time.sleep(3)
        f.close()

    def data2psv(self, cat, N):
        if N < self.total_paper:
            total_paper_ = N
        else:
            total_paper_=self.total_paper
        remainder = total_paper_%self.max_number
        num_run = total_paper_//self.max_number
        if remainder > 0:
            num_run += 1

        f = open('./raw_csv/test_'+cat.replace('.', '')+'.txt', 'a')

        for n in range(0, num_run):
            url = self.root_url + self.qsearch + "cat:" + cat+ "&start=" + str(n*self.max_number) + "&sortBy=submittedDate&sortOrder=descending&max_results=" + str(self.max_number)
            d = feedparser.parse(url)
            results = d['entries']
            for result in results:
                fd = FormatData()
                # get today's time
                unix_epoch = time.time()           #the popular UNIX epoch time in seconds
                ts = datetime.datetime.fromtimestamp(unix_epoch)
                today = ts.strftime(self.date_format)

                updated = result['updated']
                link = result['link']
                pdf = result['links'][1]['href']
                title = result['title'].replace('|', ' ')
                title = title.replace('\n', ' ')
                summary = result['summary'].replace('|', ' ')
                summary = summary.replace('\n', ' ')
                authors = result['authors']
                author_names = fd.arr2psv(authors, 'name')
                tags = result['tags']
                tag_names = fd.arr2psv(tags, 'term')
                data = [today, updated, link, pdf, title, summary, author_names, tag_names]
                writer = csv.writer(f, delimiter='|')
                writer.writerow(data)

            # wait 3 seconds (for safety)
            time.sleep(3)
        f.close()

    def data2all(self, cat, N):
        fd = FormatData()
        if N < self.total_paper:
            total_paper_ = N
        else:
            total_paper_=self.total_paper
        remainder = total_paper_%self.max_number
        num_run = total_paper_//self.max_number
        if remainder > 0:
            num_run += 1

        f = open('./all_csv/'+cat.replace('.', '')+'.txt', 'a')

        for n in range(0, num_run):
            url = self.root_url + self.qsearch + "cat:" + cat+ "&start=" + str(n*self.max_number) + "&sortBy=submittedDate&sortOrder=descending&max_results=" + str(self.max_number)
            d = feedparser.parse(url)
            results = d['entries']
            for result in results:
                fd = FormatData()
                # get today's time
                unix_epoch = time.time()           #the popular UNIX epoch time in seconds
                ts = datetime.datetime.fromtimestamp(unix_epoch)
                today = ts.strftime(self.date_format)

                updated = result['updated']
                link = result['link']
                pdf = result['links'][1]['href']
                title = result['title'].replace('|', ' ')
                title = title.replace('\n', ' ')
                title_refact = fd.format_string(result['title'])

                summary = result['summary'].replace('|', ' ')
                summary = summary.replace('\n', ' ')
                summary_refact = fd.format_string(result['summary'])
                authors = result['authors']
                author_names = fd.arr2psv(authors, 'name')
                tags = result['tags']
                tag_names = fd.arr2psv(tags, 'term')
                data = [today, updated, link, pdf, title, title_refact, summary, summary_refact, author_names, tag_names]
                writer = csv.writer(f, delimiter='|')
                writer.writerow(data)

            # wait 3 seconds (for safety)
            time.sleep(3)
        f.close()

    def test_data_refactor(self, result, raw=True):
        fd = FormatData()
        # get today's time
        unix_epoch = time.time()           #the popular UNIX epoch time in seconds
        ts = datetime.datetime.fromtimestamp(unix_epoch)
        today = ts.strftime(self.date_format)

        updated = result['updated']
        link = result['link']
        try:
            pdf = result['links'][1]['href']
        except:
            pdf = ''
        if raw:
            title = result['title']
            summary = result['summary']
        else:
            title = fd.format_string(result['title'])
            summary = fd.format_string(result['summary'])
        # make authors into one string
        authors = result['authors']
        author_names = fd.arr2csv(authors, 'name')
        # get category keyword
        tags = result['tags']
        tag_names = fd.arr2csv(tags, 'term')

        return [str(today), updated, link, pdf, title, summary, author_names, tag_names]

    ## ouput [1: csv format, 2: '|' separated]
    def get_data(self, category, output=0):
        for cat in category:
            # find total # papers
            total_num = self.count_total_papers(cat)
            print(total_num)
            if not (total_num is None):
                if output == 1:
                    self.data2csv(cat, total_num)
                elif output == 2:
                    self.data2psv(cat, total_num)
                elif output == 3:
                    self.data2all(cat, total_num)
                else:
                    self.data_print(cat, total_num)
            else:
                print("No papers in %s" % cat)
        pass


class FormatData(object):
    '''
    object for preprocessing raw data
    '''

    def __init__(self):

        pass

    def init_nltk(self):
        corpus = ['snowball_data', 'stopwords'] # corpus/model for nltk
        for corpa in corpus:
            if self.download_model(corpa):
                print('checked that snowball_data exists...')
            else:
                return False
        return True

    def download_model(self, model):
        return nltk.download(model) # returns boolean

    def format_word(self, word, digits=True, char_length=2):
        sno = nltk.stem.SnowballStemmer('english')
        if digits == True:
            word = ''.join([i for i in word if not i.isdigit()])
        if len(word) < char_length:
            return None
        else:
            return sno.stem(word)

    def format_string(self, a):
        sno = nltk.stem.SnowballStemmer('english')
        stopwords = nltk.corpus.stopwords.words('english')
        a = a.lower()
        a = re.sub('[^a-zA-Z0-9]', ' ', a)
        words = a.split(' ')
        _new_words = []
        for word in words:
            word = self.format_word(word)
            if not (word is None):
                if word not in stopwords:
                    _new_words.append(word)
        a = ' '.join(_new_words) # return string concatinating every words
        return a

    def arr2csv(self, items, query):
        item_list = items[0][query]
        items.pop(0)
        if len(items) > 0:
            for item in items:
                item_list = item_list.replace(',', '') + '|' + item[query]
        return item_list

    def arr2psv(self, items, query):
        arr = []
        for item in items:
            arr.append(item[query].replace('|', ' '))
        return arr


def main():
    category = ["stat.ML", "stat.AP", "stat.CO", "stat.ME", "stat.TH", "cs.AI", "cs.CL", "cs.CC", "cs.CG", "cs.GT", "cs.CV", "cs.DS", "cs.MA", "cs.SD"]

    #category = ["stat.ML"]
    tdr = TestDataRetriever()
    tdr.get_data(category, 3)
    pass



if __name__ == '__main__':
    main()
