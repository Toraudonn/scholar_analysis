# scholar_analysis
Arxivの論文を日次で取得し、カテゴリタグを付与して返すプログラム。

## Parameters
- delay (Default: 2)
  - プログラム実行日の delay 日前の論文を取得

## Requirements
- Python 3.5
- Pandas
- nltk
  - nltk.download("stopwords")
- requests
- feedparser
