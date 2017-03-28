
# coding: utf-8

import pandas as pd
import numpy as np
import gensim
from gensim import corpora, models, matutils
from sklearn.cluster import KMeans
from pprint import pprint

# ### 事前付与ジャンルのリストを作成
pre_genre = ["csAI", "csCC", "csCG", "csCL", "csCV", "csDS", "csGT", "csMA", "csSD", "statAP", "statCO", "statME", "statML", "statTH"]

# CSV読み込み
df = pd.DataFrame()
for genre in pre_genre:
    df = pd.concat([df, pd.read_csv("./csv/" +  genre + ".csv", header=None)])

# データフレームにカラム名をつける
header_names =  ["プログラム実行日時", "論文更新日時", "論文リンク", "PDFリンク", "論文タイトル", "サマリ", "著者", "事前付与ジャンル"]

df.columns = header_names #コラム定義

data_len = len(df) # データフレームの長さ

# カテゴリおよびそれに対応する辞書
'''
- 0: ニューラルネットワーク/ディープラーニング
- 1: 自然言語処理
- 2: マーケティング
- 3: 画像解析
- 4: 音声解析
- 5: 強化学習
'''

# カテゴリ名のリスト
cat_names = ["ニューラルネットワーク"
                     , "自然言語処理"
                     , "マーケティング"
                     , "画像解析"
                     , "音声解析"
                     , "強化学習"]

# カテゴリ対応辞書
cat_kw = [
  ['neural'
    , 'rnn'
    , 'cnn'
    , 'deep'
    ],
  ['languag'
    , 'word'
    , 'document'
    , 'nlp'],
  ['market'
    , 'custom'
    , 'commerc'
    , 'advertis'
    ],
  ['imag'
    , 'vision'
    , 'photo'
    ],
  ['sound'
  , 'speech'],
  ['reinforc']
]

# 辞書ベースでの教師データ作成、カテゴリ付与
easy_cat = [] #簡易的なカテゴリ振り分けリスト

for n, row in df.iterrows():
    row_cat = []
    for i, cat in enumerate(cat_kw):
        flag = False
        for kw in cat:
            if kw in (row["論文タイトル"] + row["サマリ"]):
                flag = True
        if flag:
            row_cat.append(1)
        else:
            row_cat.append(0)
    easy_cat.append(row_cat)

df_cat = pd.DataFrame(easy_cat)

df.index = range(data_len)

df_all = df.join(df_cat)
df_all.columns = header_names + cat_names

# 仮カテゴリごとのデータフレーム作成
df_cat_list = [] #各ジャンルのタグがついたデータフレームを保持するリスト

for cat in cat_names:
    tmp = df_all[df_all[cat] == 1]
    df_cat_list.append(tmp)

# ナイーブベイズ分類
pcat_list = []

for df_cat in df_cat_list:
    pcat_list.append(len(df_cat))

pcat_list = np.array(pcat_list)/(sum(pcat_list) * 1.0)
pcat_list #P(cat)

# $P(word_i | cat) $ の算出
word_dict_list = []
word_num_all_list = []

for df_cat in df_cat_list:
    word_list = []
    word_dict = {}
    for i, row in df_cat.iterrows():
        word_list += (row["論文タイトル"] + row["サマリ"]).split(" ")

    word_num_all = len(word_list) #カテゴリ内の総単語数
    word_num_all_list.append(word_num_all)

    for word in word_list:
        if word in word_dict:
            word_dict[word] += 1
        else:
            word_dict[word] = 1 #+ 1# スムージング用に１を足しておく

    for word in word_dict:
        word_dict[word] = 1.0 * word_dict[word] / word_num_all

    word_dict_list.append(word_dict)

# テスト・評価（Naive bayes classifier）
correct = 0 #正解数
wrong = 0
uncover = 0 # タグが付与されていない論文の数

# データ受け取り: df_recv
pred_list = []
for j, row in df_recv.iterrows(): #元のデータフレームからテキストを抽出
    document = row["論文タイトル"] + row["サマリ"]
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

    pred_list.append(cat_prob>0.79) #事前に算出した閾値
