require 'csv'

dir_name = "./hoge_name/"

example = Dir[dir_name+"*.csv"][0]
month = example.split('/')[2].split('_')[1].to_i.to_s
day = example.split('/')[2].split('_')[2].to_i.to_s
date_name = month + '月' + day + '日'

text = "<h2>"+date_name+"に公開された論文"+"</h2>"

Dir["./hoge_name/*.csv"].each do |f|
  cat = f.split('/')[2].split('_')[3].split('.')[0]
  p cat
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
    authors = authors.gsub("[","").gsub("]","").gsub("'","")
    
    text = text + "<li><a href='" + abs_link + "'>" + title + "</a><ul><li>著者：" + authors + "</li></ul>"
  end
  text += "</ul>"
end

begin
  file = File.open(dir_name+"daily.txt", "w")
  file.write(text) 
rescue IOError => e
  #some error occur, dir not writable etc.
  p "error when saving to file"
ensure
  file.close unless file.nil?
end



