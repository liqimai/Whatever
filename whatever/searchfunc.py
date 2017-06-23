# coding: utf-8
import heapq
from parse import Parser
from Indexbuild import IndexBuilder
import math
import sys
import os
import json
import random
import nltk
from vocabulary.vocabulary import Vocabulary as vb
from vocabtree import VocabTree
# 辅助类 用于建立id和score的关系
class id_score:
    def __init__(self, urlid, score):
        self.urlid = urlid
        self.score = score

    def __cmp__(x, y):
        if (x.score < y.score):
            return 1
        elif (x.score == y.score):
            return 0
        else:
            return -1

def add_synonyms(query):
    try:
        synonyms = json.loads(vb.synonym(query))
    except Exception as e:
        synonyms = []
    return query+' '+' '.join([item['text']for item in synonyms])

# 搜索类
class searcher:
    # 定义构造方法
    def __init__(self):
        self.__invertedindex = IndexBuilder().index
        self.parser = Parser()
        self.parser.normalize('a')
        self.dictionary = None
        self.totallength = 0
        self.lave = 0
        self.roll_index = VocabTree()

        with open(os.path.join(os.path.dirname(__file__), 'urllist'), 'r') as f1:  # 打开文件urllist
            self.__urlnum = int(f1.readline())  # 总url数目
            self.urllist = []
            n = 0

            while n < self.__urlnum:  # 将url信息存入字典中
                s = f1.readline()
                arr = s.split(' ')
                # urlid = int(arr[0])          #url ID
                url = arr[1]  # url地址
                indegree = int(arr[2])  # url入度:用于计算PageRank
                outdegree = int(arr[3])  # url出度
                length_of_texts = int(arr[4])
                self.urllist.append([url, indegree, outdegree, length_of_texts])
                n = n + 1
                self.totallength += length_of_texts
        self.lave = self.totallength / self.__urlnum

        with open(os.path.join(os.path.dirname(__file__), 'htmls'), 'r') as file:
            self.htmls = json.load(file)
        # [
        #   [title, text],
        #   [title, text],
        # ]
        with open(os.path.join(os.path.dirname(__file__), 'dictionary'), 'r') as file:
            self.dictionary = json.load(file)
        #todo: 轮盘索引
        sys.stderr.write('Building roll index...')
        for word in self.dictionary:
            for i in range(len(word)+1):
                self.roll_index.add_word(word[i:]+'$'+word[:i])
        sys.stderr.write('[Success]\n')


    def search_cos(self, query, k =50):
        querydict_tf = {}
        weight = {}
        scoredict = {}
        length = 0
        heap = []
        urlids = []
        self.querylist = self.parser.normalize(query)
        totaldoc = len(self.urllist)
        for item in self.querylist:
            if (item in querydict_tf):
                querydict_tf[item] += 1
            else:
                querydict_tf[item] = 1
        for item in querydict_tf.iterkeys():
            if (item in self.__invertedindex):
                weight[item] = (1.0 + math.log10(querydict_tf[item])) * math.log10(
                    1.0 * totaldoc / self.__invertedindex[item][0])
            else:
                weight[item] = 0

        i = 0
        for i in range(self.__urlnum):
            score = 0

            for item in weight.iterkeys():
                if (item in self.__invertedindex and str(i) in self.__invertedindex[item][1]):
                    score += weight[item] * self.__invertedindex[item][1][str(i)][1]
            uid = id_score(i, score)
            if (uid.score > 0):
                heap.append(uid)

        # 输出
        heapq.heapify(heap)
        for i in range(k):
            if heap:
                urlids.append(heapq.heappop(heap).urlid)
        return urlids

    def abstract(self, query, urlid):
        query_list = self.parser.normalize(query)
        result_list = []
        for item in query_list:
            index = self.htmls[urlid][1].lower().find(item)
            if index != -1:
                result_list.append([])
                start = -int(random.random() * 10)
                length = 15 - start * 2
                ll = len(item)
                if index >= -start:
                    i = start
                    a = 0
                    result_list[len(result_list) - 1].append('')
                    while i < start + length and index + i < len(self.htmls[urlid][1]):
                        if i == 0:
                            a += 1
                            result_list[len(result_list) - 1].append('')
                        if i == ll:
                            a += 1
                            result_list[len(result_list) - 1].append('')
                        result_list[len(result_list) - 1][a] += self.htmls[urlid][1][index + i]
                        i += 1
                    if i <= ll:
                        result_list[len(result_list) - 1].append('')
                else:
                    i = 0
                    a = 0
                    result_list[len(result_list) - 1].append('')
                    while i < length and index + i < len(self.htmls[urlid][1]):
                        if i == 0:
                            a = 0
                            result_list[len(result_list) - 1].append('')
                        if i == ll:
                            a = 0
                            result_list[len(result_list) - 1].append('')
                        result_list[len(result_list) - 1][a] += self.htmls[urlid][1][index + i]
                        i += 1
                    if i <= ll:
                        result_list[len(result_list) - 1].append('')
        return result_list

    # boolean search
    def boolean(self, query, k=50):
        def query_to_tree(query):
            text2token = r'AND|OR|NOT|\w+|\(|\)'
            token2tag = {
                'AND': 'AND',
                'OR': 'OR',
                'NOT': 'NOT',
                '(': 'LP',
                ')': 'RP'
            }
            grammar = """
            exp -> orexp
            orexp -> orexp "OR" andexp
            orexp -> andexp
            andexp -> andexp "AND" notexp
            andexp -> andexp notexp
            andexp -> notexp
            notexp -> "NOT" metaexp
            notexp -> metaexp
            metaexp -> "LP" exp "RP"
            metaexp -> "#TERM#"
            """
            token = nltk.regexp_tokenize(query, text2token)
            tags = [token2tag.get(t, '#TERM#') for t in token]
            terms = [t for t in token if t not in ['AND', 'OR', 'NOT', '(', ')']]
            parser = nltk.ChartParser(nltk.CFG.fromstring(grammar))
            for tree in parser.parse(tags):
                treestr = str(tree)
                for t in terms:
                    treestr = treestr.replace("#TERM#", t, 1)
                tree = nltk.Tree.fromstring(treestr)
            return tree

        def traversal(tree):
            def dict_or(id_score_dict1, id_score_dict2):
                rval = {}
                for key in set(id_score_dict1.keys()).union(id_score_dict2.keys()):
                    rval[key] = id_score_dict1.get(key, 0) + id_score_dict2.get(key, 0)
                return rval

            def dict_and(id_score_dict1, id_score_dict2):
                rval = {}
                for key in set(id_score_dict1.keys()).intersection(id_score_dict2.keys()):
                    rval[key] = min(id_score_dict1.get(key), id_score_dict2.get(key))
                return rval

            def dict_not(id_score_dict):
                return {url:0 for url in {str(url) for url in range(len(self.urllist))} - set(id_score_dict.keys())}

            def word2dict(word):
                term = self.parser.stem(word)
                return {urlid:tf_idf[0]
                        for urlid, tf_idf in self.__invertedindex.get(term, [0, {}, 0])[1].iteritems()}

            if isinstance(tree, str) or isinstance(tree, unicode):
                return word2dict(tree)
            elif len(tree) == 1:
                return traversal(tree[0])
            elif tree.label() == 'orexp':
                assert tree[1] == 'OR'
                return dict_or(traversal(tree[0]), traversal(tree[2]))
            elif tree.label() == 'andexp':
                if tree[1] == 'AND':
                    return dict_and(traversal(tree[0]), traversal(tree[2]))
                else:
                    return dict_and(traversal(tree[0]), traversal(tree[1]))
            elif tree.label() == 'notexp':
                assert tree[0] == 'NOT'
                return dict_not(traversal(tree[1]))
            elif tree.label() == 'metaexp':
                assert tree[0] == 'LP'
                assert tree[2] == 'RP'
                return traversal(tree[1])

        if not self.parser.normalize(query):
            return []
        tree = query_to_tree(query)
        url_score_dict = traversal(tree)
        heap=[]
        for url, socre in url_score_dict.iteritems():
            heap.append(id_score(int(url), socre))

        # finalindex = self.__invertedindex.get(character_set[0], [0, {}, 0])[1].keys()  # 获得第一个term的倒排文件索引
        # for term in character_set:
        #     if finalindex:
        #         index = self.__invertedindex.get(term, [0, {}, 0])[1].keys()  # 获得第i个term的倒排文件索引
        #         finalindex = list(set(finalindex) & set(index))
        #     else:
        #         return finalindex
        #
        # heap = []
        # for url in finalindex:
        #     score = 0
        #     for term in character_set:
        #         score = score + self.__invertedindex.get(term, [0, {}, 0])[1][url][0]
        #     heap.append(id_score(int(url), score))

        urlids = []
        heapq.heapify(heap)
        for i in range(k):
            if heap:
                urlids.append(heapq.heappop(heap).urlid)
        return urlids

    def search_rsv(self, query, k=50):
        k1 = 1.5
        k3 = 1.5
        b = 0.75
        querydict_tf = {}
        weight = {}
        scoredict = {}
        length = 0
        heap = []
        urlids = []
        self.querylist = self.parser.normalize(query)
        totaldoc = len(self.urllist)
        for item in self.querylist:
            if (item in querydict_tf):
                querydict_tf[item] += 1
            else:
                querydict_tf[item] = 1

        i = 0
        for i in range(self.__urlnum):
            score = 0
            for item in querydict_tf.iterkeys():
                if (item in self.__invertedindex and str(i) in self.__invertedindex[item][1]):
                    score += math.log10(1.0 * self.__urlnum / self.__invertedindex[item][0]) * (k1 + 1) * \
                             self.__invertedindex[item][1][str(i)][0] / (
                             k1 * ((1 - b) + b * (1.0 * self.urllist[i][3] / self.lave)) +
                             self.__invertedindex[item][1][str(i)][0]) * (k3 + 1) * querydict_tf[item] / (
                             k3 + querydict_tf[item])
            uid = id_score(i, score)
            if (uid.score > 0):
                heap.append(uid)
                # if (len(heap) <= 50):
                #     heapq.heappush(heap, uid)
                # else:
                #     heapq.heappushpop(heap, uid)


        # 输出
        #     while len(heap) > 0:
        #         tmp = heapq.heappop(heap).urlid
        #         urlids.append(tmp)
        #     urlids.reverse()
        #     return urlids
        heapq.heapify(heap)
        for i in range(k):
            if heap:
                urlids.append(heapq.heappop(heap).urlid)
        return urlids

    def lm(self, query, k=50, ):
        querydict_tf = {}
        weight = {}
        scoredict = {}
        length = 0
        heap = []
        urlids = []
        lam = 0.8
        self.querylist = self.parser.normalize(query)
        totaldoc = len(self.urllist)
        for item in self.querylist:
            if (item in querydict_tf):
                querydict_tf[item] += 1
            else:
                querydict_tf[item] = 1
        for item in querydict_tf.iterkeys():
            if (item in self.__invertedindex):
                weight[item] = (1.0 + math.log10(querydict_tf[item])) * math.log10(
                    1.0 * totaldoc / self.__invertedindex[item][0])
            else:
                weight[item] = 0

        i = 0
        for i in range(self.__urlnum):
            score = 1

            for item in weight.iterkeys():
                if (item in self.__invertedindex and str(i) in self.__invertedindex[item][1]):
                    a = float(self.__invertedindex[item][1][str(i)][0]) / self.urllist[i][3]
                    b = float(self.__invertedindex[item][2]) / self.totallength
                    score *= (lam * a + (1 - lam) * b) ** weight[item]
                else:
                    score = 0
            uid = id_score(i, score)
            if (uid.score > 0):
                heap.append(uid)

        # 输出
        # while len(heap) > 0:
        #     tmp = heapq.heappop(heap).urlid
        #     urlids.append(tmp)
        # urlids.reverse()
        # return urlids
        heapq.heapify(heap)
        for i in range(k):
            if heap:
                urlids.append(heapq.heappop(heap).urlid)
        return urlids

    def gettitle(self, url):
        return u'in_gettitle'
        # try:
        #     req_header = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}
        #     req = urllib2.Request(url,None,req_header)
        #     page = urllib2.urlopen(req,None,54)
        #     html = page.read()
        #     page.close()
        #     soup = BeautifulSoup(html, 'lxml')  
        #     title = soup.title
        #     title = title.string
        # except Exception as e:
        #     print e
        #     title = None
        # return title
    def word_correct(self, word):
        word = self.parser.normalize(word)
        word_list = []
        term = self.__invertedindex.keys()
        # todo correction
        return word_list

    def wildcard2word(self, wildcard):
        def derolled(word):
            assert '$' in word
            first, second = word.split('$')
            return second + first

        assert '*' in wildcard
        first, second = wildcard.split('*')
        rolled_word = second+'$'+first
        return map(derolled, self.roll_index.find_by_prefix(rolled_word))

if __name__ == '__main__':
    pass

    # import urllib2
    # import locale
    # from bs4 import BeautifulSoup
    #
    # ss = searcher()
    # query = unicode(raw_input('Search for:\n').decode(locale.getpreferredencoding()))
    # while query != '':
    #     sys.stderr.write('Start cosine searching...')
    #     urlids = ss.search_cos(query)
    #     sys.stderr.write('[Success]\n')
    #     print 'Cosine result:'
    #     print urlids
    #
    #     sys.stderr.write('Start boolean searching...')
    #     urlids = ss.boolean(query)
    #     sys.stderr.write('[Success]\n')
    #     print 'Boolean result:'
    #     print urlids
    #
    #     query = unicode(raw_input('Another Search for:\n').decode(locale.getpreferredencoding()))

    # '''for iitem in urlids:
    #     try:
    #         item=int(iitem.urlid)
    #         html=urllib2.urlopen(ss.urls[item][0]).read()
    #         soup=BeautifulSoup(html,'lxml')
    #         content=soup.get_text()
    #         ppp=Parser()
    #         txt=ppp.normalize(content)
    #         cc=''
    #         for each in txt:
    #             cc+=each+'-'
    #         print(iitem.score)
    #         for eeach in ss.querylist:
    #             print(eeach,ss.__invertedindex[eeach][1][str(item)][0],ss.__invertedindex[eeach][1][str(item)][1])
    #         print(ss.urls[item][0])
    #         print(cc.encode(locale.getpreferredencoding()))
    #         time.sleep(0.1)
    #     except Exception as e:
    #         print(e)
    #         time.sleep(0.1)
    #         pass'''
