#coding: utf-8
import crawl
import heapq
from parse import Parser
from Indexbuild import IndexBuilder
import math
import time
import sys
import urllib2
from bs4 import BeautifulSoup
#辅助类 用于建立id和score的关系
class id_score:
    def __init__(self,urlid,score):
        self.urlid=urlid
        self.score=score

    def __cmp__(x,y):
        if(x.score<y.score):
            return -1
        else:
            if(x.score==y.score):
                return 0
            else:
                return 1
#搜索类
class searcher:
    #IndexBuilder().index
    #... = Parser()
    #....normalize(str) #['word','word'...]
    #定义构造方法
    def __init__(self):
        self.__invertedindex = IndexBuilder().index
        self.pp=Parser()
        self.pp.normalize('a')
        self.pagerank = []
        with open('urllist', 'r') as f1:     #打开文件urllist
            self.__num1 = int(f1.readline()) #总url数目
            self.urllist = []
            n = 0

            while n < self.__num1:           #将url信息存入字典中
                s = f1.readline()
                arr = s.split(' ')
                # urlid = int(arr[0])          #url ID
                url = arr[1]                 #url地址
                indegree = int(arr[2])       #url入度:用于计算PageRank
                outdegree = int(arr[3])      #url出度
                length_of_texts = int(arr[4])
                self.urllist.append([url, indegree, outdegree,length_of_texts])
                n = n + 1
        with open('pagerank','r') as file:
            for line in file:
                self.pagerank.append(float(line))
            
    def search_cos(self,query,pagerank=True):
        querydict_tf={}
        weight={}
        scoredict={}
        length=0
        heap=[]
        urlids=[]
        self.querylist=self.pp.normalize(query)
        totaldoc=len(self.urllist)
        for item in self.querylist:
            if(item in querydict_tf):
                querydict_tf[item]+=1
            else:
                querydict_tf[item]=1
        for item in querydict_tf.iterkeys():
            if(item in self.__invertedindex):
                weight[item]=(1.0+math.log10(querydict_tf[item]))*math.log10(1.0*totaldoc/self.__invertedindex[item][0])
            else:
                weight[item]=0
        
        i=0
        while i < self.__num1:
            score=0

            for item in weight.iterkeys():
                if(item in self.__invertedindex and str(i) in self.__invertedindex[item][1]):
                    score+=weight[item]*self.__invertedindex[item][1][str(i)][1]
            if pagerank:
                score*=self.pagerank[i]
            uid=id_score(i,score)
            if(uid.score>0):
                if(len(heap)<=50):
                    heapq.heappush(heap,uid)
                else:
                    heapq.heappushpop(heap,uid)

            i+=1
  
        #输出
        while len(heap)>0:
            tmp=heapq.heappop(heap).urlid
            urlids.append(tmp)
        urlids.reverse()
        return urlids

    #boolean search
    def boolean(self, query): 
        query = self.pp.normalize(query) #解析query
        # character = []
        # for term in query:
        #     print type(term)
        #     query.append(term)
        character_set = list(set(query)) #去重

        #根据term的倒排索引数目排序
        # character_set = []
        # for term in character:
        #     T = (term, len(self.__invertedindex[term][1]))
        #     character_set.append(T)
        # character_set.sort(lambda x, y: cmp(x[1], y[1]))

        #获取倒排文件索引
        finalindex = self.__invertedindex.get(character_set[0],[0,{},0])[1].keys() #获得第一个term的倒排文件索引
        for term in character_set:
            if finalindex:
                index = self.__invertedindex.get(term,[0,{},0])[1].keys() #获得第i个term的倒排文件索引
                finalindex = list(set(finalindex) & set(index))
            else:
                return finalindex

        heap = []
        for url in finalindex:
            score = 0
            for term in character_set:
                score = score + self.__invertedindex.get(term,[0,{},0])[1][url][0]
            heap.append(id_score(int(url),score))
        heapq.heapify(heap)

        urlids = []
        while len(heap)>0:
            tmp=heapq.heappop(heap).urlid
            urlids.append(tmp)
        urlids.reverse()
        return urlids

    def gettitle(url):
        try:
            req_header = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}
            req = urllib2.Request(url,None,req_header)
            page = urllib2.urlopen(req,None,54)
            html = page.read()
            page.close()
            soup = BeautifulSoup(html)  
            title = soup.title
            title = title.string
        except Exception as e:
            print e
            title = None
        return title

if __name__ == '__main__':
    import urllib2
    import locale
    from bs4 import BeautifulSoup
    ss = searcher()
    query = unicode(raw_input('Search for:\n').decode(locale.getpreferredencoding()))
    while query!='':

        sys.stderr.write('Start cosine searching...')
        urlids = ss.search_cos(query)
        sys.stderr.write('[Success]\n')
        print 'Cosine result:'
        print urlids

        sys.stderr.write('Start boolean searching...')
        urlids = ss.boolean(query)
        sys.stderr.write('[Success]\n')
        print 'Boolean result:'
        print urlids

        query = unicode(raw_input('Another Search for:\n').decode(locale.getpreferredencoding()))


    '''for iitem in urlids:
        try:
            item=int(iitem.urlid)
            html=urllib2.urlopen(ss.urls[item][0]).read()
            soup=BeautifulSoup(html,'lxml')
            content=soup.get_text()
            ppp=Parser()
            txt=ppp.normalize(content)
            cc=''
            for each in txt:
                cc+=each+'-'
            print(iitem.score)
            for eeach in ss.querylist:
                print(eeach,ss.__invertedindex[eeach][1][str(item)][0],ss.__invertedindex[eeach][1][str(item)][1])
            print(ss.urls[item][0])
            print(cc.encode(locale.getpreferredencoding()))
            time.sleep(0.1)
        except Exception as e:
            print(e)
            time.sleep(0.1)
            pass'''
