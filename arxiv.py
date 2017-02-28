from __future__ import print_function
import sys
import csv
import time, datetime
import requests


import feedparser
from requests.exceptions import HTTPError


root_url = 'http://export.arxiv.org/api/'

format = '%Y-%m-%dT%H:%M:%SZ'  #Formatting directives
def main():
    
    category = ["stat.ML", "stat.AP", "stat.CO", "stat.ME", "stat.TH", "cs.AI", "cs.CL", "cs.CC", "cs.CG", "cs.GT", "cs.CV", "cs.DS", "cs.MA", "cs.SD"]
    
    qsearch = "query?search_query="
    for cat in category:
        # find total # papers
        url = root_url + qsearch + "cat:" + cat + "&start=0&sortBy=submittedDate&sortOrder=descending&max_results=1"
        d = feedparser.parse(url)
        filename = cat.replace('.', '')
        print('status: ' + str(d['status']))
        if d['status'] != 200:
            print("cannot GET url...")
            continue
        else:
            N = int(d['feed']['opensearch_totalresults'])
            print(N)
            if N is None:
                print("No papers for " + cat)
            else:
                # for safety
                num_of_paper = 100
                num_pp = 10 # the maximum result is 10
                if N < num_of_paper:
                    num_of_paper = N
                
                remainder = num_of_paper%num_pp
                num_run = num_of_paper//num_pp
                
                if remainder > 0:
                    num_run += 1
                f = open(filename+'.csv', 'a')
                for n in range(0, num_run):
                    
                    # open csv
                    
                    
                    url = root_url + qsearch + "cat:" + cat+ "&start=" + str(n*num_pp) + "&sortBy=submittedDate&sortOrder=descending&max_results=" + str(num_pp)
                    d = feedparser.parse(url)
                    results = d['entries']
                    
                    
                    for result in results:
                        link = result['link']
                        try:
                            pdf = result['links'][1]['href']
                        except:
                            pdf = ''
                        title = result['title'].replace(',', '')
                        title.replace('\n', ' ')
                        summary = result['summary'].replace(',', '')
                        summary.replace('\n', ' ')
                        
                        # make authors into one string
                        authors = result['authors']
                        author_names = authors[0]['name']
                        authors.pop(0)
                        if len(authors) > 0:
                            for author in authors:
                                author_names = author_names + '|' + author['name']
                        
                        # get today's time
                        unix_epoch = time.time()           #the popular UNIX epoch time in seconds
                        ts = datetime.datetime.fromtimestamp(unix_epoch)
                        today = str(ts.strftime(format))
                        
                        updated = result['updated']
                        
                        # get category keyword
                        tags = result['tags']
                        tag_names = tags[0]['term']
                        tags.pop(0)
                        if len(tags) > 0:
                            for tag in tags:
                                tag_names = tag_names + '|' + tag['term']
                        
                        # print the output
                        # print('---------------------------------')
                        # print(link)
                        # print(title)
                        # print(author_names)
                        # print(tag_names)
                        
                        # add to csv
                        data = [today, updated, link, pdf, title, summary, author_names, tag_names]
                        writer = csv.writer(f)
                        writer.writerow(data)
                        
                    # wait 3 seconds (for safety)
                    time.sleep(3)
                
                f.close()
        
    pass
    

    
if __name__ == '__main__':
    main()