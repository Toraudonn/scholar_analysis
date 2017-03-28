require 'csv'

example = Dir["./hoge_name/*.csv"][0]
month = example.split('/')[2].split('_')[1].to_i.to_s
day = example.split('/')[2].split('_')[2].to_i.to_s
date_name = month + '月' + day + '日'

text = "<h2>"+date_name+"に公開された論文"+"</h2>"

Dir["./hoge_name/*.csv"].each do |f|
  cat = f.split('/')[2].split('_')[3].split('.')[0]
  text += "<h3>"+cat+"</h3><ul>"
  data = CSV.read(f, headers: true)
  data.each do |d|
    date = d[1]
    create_date = d[2]
    abs_link = d[3]
    pdf_link = d[4]
    title = d[5]
    summary = d[7]
    authors = d[9]
    p authors
    author_list = ""
    authors.each do |a|
      author_list = author_list + a + ", "
    end
    
    text = text + "<li><a href='" + abs_link + "'>" + title + "</a><ul><li>著者：" + author_list + "</li></ul>"
  end
  text += "</ul>"
  
  p text
end



