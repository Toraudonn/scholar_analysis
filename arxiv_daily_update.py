# coding: utf-8
import sys
import os
import re
import csv
import time
import datetime

import feedparser
import requests
from requests.exceptions import HTTPError
import pickle

import nltk
import pandas as pd
import numpy as np

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

class DataRetriever(Arxiv): # Object for getting data
    def __init__(self, total_paper=100, max_number=10):
        Arxiv.__init__(self)
        self.total_paper = total_paper # number of total papers to get
        self.max_number = max_number # number of papers per each api requests (maximum request size is 10)

    def data2df(self, categories, delay):
        fd = FormatData()
        df = pd.DataFrame()
        data = []

        for cat in categories:
            total_num = self.count_total_papers(cat)

            if total_num < self.total_paper:
                total_paper_ = total_num
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
                    fd = FormatData()
                    # get today's time
                    unix_epoch = time.time()           #the popular UNIX epoch time in seconds
                    ts = datetime.datetime.fromtimestamp(unix_epoch)
                    today = ts.strftime(self.date_format)

                    updated = result['updated']
                    us = datetime.datetime.strptime(updated, self.date_format)

                    if (ts - us).days != delay:
                        continue
                    else:
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
                        data.append([today, updated, link, pdf, title, title_refact, summary, summary_refact, author_names, tag_names])
                df = pd.DataFrame(data)
        return df

class CategoryClassifier(object): # object for classifying categories
    def __init__(self):
        self.header_names =  ["プログラム実行日時", "論文更新日時", "論文リンク", "PDFリンク", "元論文タイトル", "論文タイトル", "元サマリ", "サマリ", "著者", "事前付与ジャンル"]
        self.cat_names = ["ニューラルネットワーク", "自然言語処理", "マーケティング", "画像解析", "音声解析", "強化学習"]
        self.today = datetime.date.today()

    def classify(self, df_recv, pcat_list, word_dict_list, word_num_all_list, threshold = 1.2, title_weight = 15):
        df_recv.columns = self.header_names

        pred_list = []
        pred_result = []
        for j, row in df_recv.iterrows(): #元のデータフレームからテキストを抽出
            document = (row["論文タイトル"] + " ") * title_weight + row["サマリ"]
            words = document.split()

            cat_prob = []
            for i, word_dict in enumerate(word_dict_list):
                prob = np.log(pcat_list[i]) #初期化
                for word in words:
                    if word in word_dict:
                        prob += np.log(word_dict[word])
                    else:
                        prob += np.log(1.0/word_num_all_list[i])
                cat_prob.append(prob)
            pred_result.append(list((cat_prob - np.mean(cat_prob))/np.std(cat_prob) > threshold)) #事前に算出した閾値

            df_pred = pd.DataFrame(pred_result)
            df_classified = df_recv.join(df_pred)
            df_classified.columns = self.header_names + self.cat_names #ヘッダ追加
        return df_classified

    def output_csv(self, df):
        drop_list = ['プログラム実行日時', '論文更新日時', 'PDFリンク', '論文タイトル', 'サマリ', '事前付与ジャンル', 'ニューラルネットワーク', '自然言語処理', 'マーケティング', '画像解析', '音声解析', '強化学習']
        df_all = pd.DataFrame(columns = ['論文リンク',  '元論文タイトル', '元サマリ', '著者'])
        for cat in self.cat_names:
            df_classified = df[df[cat]== True]
            df_classified = df_classified.drop(drop_list, axis = 1)
            df_classified['カテゴリ'] = [cat] * len(df_classified)
            df_all = pd.concat([df_all, df_classified])
        df_all.to_csv("./output_csv/" + str(self.today.month) +"_" + str(self.today.day) + ".csv", index = False)

if __name__ == '__main__':
    categories = ["stat.ML", "stat.AP", "stat.CO", "stat.ME", "stat.TH", "cs.AI", "cs.CL", "cs.CC", "cs.CG", "cs.GT", "cs.CV", "cs.DS", "cs.MA", "cs.SD"]

    # パラメータ
    delay = 2
    threshold = 1.2
    title_weight = 15

    dr = DataRetriever()
    cc = CategoryClassifier()
    df_recv = dr.data2df(categories, delay)

    # pickle load
    with open('./dumpfile/pcat_list.dump', 'rb') as f:
        pcat_list = pickle.load(f)
    with open('./dumpfile/word_dict_list.dump', 'rb') as f:
        word_dict_list = pickle.load(f)
    with open('./dumpfile/word_num_all_list.dump', 'rb') as f:
        word_num_all_list = pickle.load(f)

    df_classified = cc.classify(df_recv, pcat_list, word_dict_list, word_num_all_list, threshold, title_weight)
    cc.output_csv(df_classified) #CSV書き出し
