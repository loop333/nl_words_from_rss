#!python3
# -*- coding: utf-8 -*-
import urllib.request
import xml.etree.ElementTree as ET
import re
import datetime

cfg = []
words = {}

def process(s):
    s = s.lower()
    s = re.sub(r'\d+', ' ', s)
    s = re.sub(r'[.,:?]', ' ', s)
    s = re.sub(r'\s+[-&]\s+', ' ', s)

    for word in s.split():
        word = re.sub(r'^[(\'"‘’]', '', word)
        word = re.sub(r'[)\'"‘’]$', '', word)
        if word != '':
            old = words.get(word, {'count': 0, 'translation': '-'})
            words[word] = {'count': old['count']+1, 'translation': old['translation']}

with open('words.cfg', 'r') as f:
    for line in f:
        line = line.strip()
        d = line.split('^')
        cfg.append({'name': d[0], 'url': d[1], 'date': datetime.datetime.strptime(d[2], '%d.%m.%Y %H:%M:%S %z')})

with open('words.txt', 'r') as f:
    for line in f:
        line = line.strip()
        d = line.split('^')
        words[d[1]] = {'count': int(d[0]), 'translation': d[2]}

#for rss in cfg:
#    print(rss['date'])

for rss in cfg:
    print(rss['name'])
    url = rss['url']
    req = urllib.request.Request(url)
    resp = urllib.request.urlopen(req)
    xml = ET.parse(resp)
    root = xml.getroot()
#    ET.dump(root)
    old_date = rss['date']
    max_date = old_date

    if root.tag == '{http://www.w3.org/2005/Atom}feed':
        find_tag = '{*}entry'
        tags = ['{*}title', '{*}summary']
        date_tag = '{*}published'
        date_fmt = '%Y-%m-%dT%H:%M:%S.000%z'
    elif root.tag == 'rss':
        find_tag = 'channel/item'
        tags = ['title', 'description']
        date_tag = 'pubDate'
        date_fmt = '%a, %d %b %Y %H:%M:%S %z'
    else:
        print('Error: Unknown RSS Format')
        continue

    for item in root.findall(find_tag):
        date_elem = item.find(date_tag)
        date_str = date_elem.text
        pub_date = datetime.datetime.strptime(date_str, date_fmt)
        if pub_date > max_date:
            max_date = pub_date
        if pub_date <= old_date:
            continue
        print(pub_date)
        for tag in tags:
            text = ''
            elem = item.find(tag)
            if elem is not None and elem.text is not None:
                text = elem.text
            process(text)

    rss['date'] = max_date

with open('words.txt', 'w') as f:
    for i in sorted(words.items(), key=lambda item: item[1]['count'], reverse=True):
        s = str(i[1]['count']) + '^' + i[0] + '^' + i[1]['translation']
        f.write(s + '\n')

with open('words.cfg', 'w') as f:
    for rss in cfg:
        s = rss['date'].strftime('%d.%m.%Y %H:%M:%S %z')
        f.write(rss['name'] + '^' + rss['url'] + '^' + s + '\n')
