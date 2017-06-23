# coding=utf-8
from __future__ import print_function
import os
import time
import urllib2
import sys
import socket
from Indexbuild import IndexBuilder
import json


class crawl:

    def __init__(self, urllist='urllist', invertedindex='invertedindex',
                 htmls='htmls'):  # 将主网址加入集合
        self.urllistName = os.path.join(os.path.dirname(__file__), urllist)
        self.htmlsName = os.path.join(os.path.dirname(__file__), htmls)
        self.indexbuilder = IndexBuilder(invertedindex)
        self.urls = []
        self.htmls = []
        self.length = []

    def process(self):
        file_names = urllib2.urlopen("http://127.0.0.1:9000/index.txt").read().split()
        for file_name in file_names:
            try:
                url = "http://127.0.0.1:9000/{}".format(file_name)
                content = urllib2.urlopen(url).read()
                title = content[:content.find("\n")]
                self.urls.append(url)
                self.length.append(self.indexbuilder.process(content, title, len(self.urls) - 1))
                self.htmls.append([title, content])
            except urllib2.URLError as e:
                print(type(e), e.message, e.args)
                print(url)
            except socket.timeout as e:
                print(type(e), e.message, e.args)
                print(url)
            except Exception as e:
                print(e)
                print(url)

    def save(self):
        self.indexbuilder.save()
        json.dump(self.htmls, open(self.htmlsName, 'w'))

        with open(self.urllistName, 'w') as uu:
            uu.write('%d\n' % (len(self.urls)))
            i = 0
            print('Writing urllist back into file...')
            for item in self.urls:
                try:
                    uu.write('%d %s %d %d %d\n' % (i, item, 0, 0, self.length[i]))
                    i += 1
                except:
                    sys.stderr.write(
                        '%d %s\n' % (i, item) + '\n')
                    sys.stderr.write('urls output wrong\n')


if __name__ == '__main__':
    cc = crawl()
    cc.process()
    cc.save()
