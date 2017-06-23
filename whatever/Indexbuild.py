# coding=utf-8
# from bs4 import BeautifulSoup
from parse import parser
import math
import json
import os
import sys


# {
#     'term':
#         [
#             df=0,   #document frequency
#             {   #urlid-record dictionary
#                 urlid:  #   a record
#                     [
#                         tf=0,   #term frequency
#                         tf_idf=0,    #normalized tf-idf
#                     ],
#                 urlid:  #   Another record
#                     [
#                         tf=0,
#                         tf_idf=0
#                     ]
#                 ...
#             },
#             cf  #collection frequency, total number of this term in the whole collection
#         ]
#     'Another term':
#         [
#             ...
#         ],
#     ...
# }
class IndexBuilder(object):
    def __init__(self, invertedindex='invertedindex', dictionary='dictionary'):
        self.__p = parser
        self.__urlnum = 0
        self.index = {}
        self.__filePath = os.path.join(os.path.dirname(__file__), invertedindex)
        self.dictionary = []
        self.__dictionaryPath = os.path.join(os.path.dirname(__file__), dictionary)
        self.__doc_term_list = {}
        try:
            with open(self.__filePath, 'r') as fin:
                sys.stderr.write('Reading invertedindex in...')
                self.__urlnum = int(fin.readline())
                self.index = json.load(fin)
                sys.stderr.write('[Success]' + '\n')
        except IOError as err:
            sys.stderr.write(str(type(err)) + str(err.args) + '\n')
            sys.stderr.write('Will rebuild the Inverted Index\n')
        try:
            with open(self.__dictionaryPath, 'r') as fin:
                sys.stderr.write('Reading dictionary in...')
                self.dictionary = json.load(fin)
                sys.stderr.write('[Success]' + '\n')
        except IOError as err:
            sys.stderr.write(str(type(err)) + str(err.args) + '\n')
            sys.stderr.write('Will rebuild the dictionary\n')



    def process(self, text, title, urlid):
        urlid = str(urlid)
        self.__urlnum = self.__urlnum + 1
        # text = soup.get_text()
        length = 0
        if text:
            terms = self.__p.normalize(text)
            self.__doc_term_list[urlid] = terms
            for word in terms:
                records = self.index.setdefault(word, [0, {}, 0])[1]
                record = records.setdefault(urlid, [0, 0])
                record[0] += 1
                length = length + 1
            self.dictionary.extend(list(set(self.__p.cut(text))))
        # try:
        #     title = soup.title.string
        # except:
        #     title = None
        if title:
            # title = unicode(title)[:-16] * 5
            for word in self.__p.normalize(title):
                records = self.index.setdefault(word, [0, {}, 0])[1]
                record = records.setdefault(urlid, [0, 0])
                record[0] = record[0] + 1
                length = length + 1

        return length

    def save(self):
        self.__calculateTf_idf()
        self.dictionary = list(set(self.dictionary))
        try:
            with open(self.__filePath, 'w') as fout:
                sys.stderr.write('Save back to \"invertedindex\"...')
                fout.write(str(self.__urlnum) + '\n')
                json.dump(self.index, fout, indent=1)
                sys.stderr.write('[Success]' + '\n')
        except IOError as err:
            sys.stderr.write(str(err) + '\n')
            sys.stderr.write('Can not write back to \"invertedindex\"!!!' + '\n')
        try:
            with open(self.__dictionaryPath, 'w') as fout:
                sys.stderr.write('Save back to \"dictionary\"...')
                json.dump(self.dictionary, fout, indent=1)
                sys.stderr.write('[Success]' + '\n')
        except IOError as err:
            sys.stderr.write(str(err) + '\n')
            sys.stderr.write('Can not write back to \"dictionary\"!!!' + '\n')
        return

    def __calculateTf_idf(self):
        sys.stderr.write('Calculating...')
        # tf-idf = (1+log(tf,base))*log(N/df,base)
        base = 10
        for postingList in self.index.itervalues():
            postingList[0] = len(postingList[1])
            df = postingList[0]
            postingList[2] = 0
            for record in postingList[1].itervalues():
                tf = record[0]
                record[1] = (1 + math.log(tf, base)) * math.log(self.__urlnum / float(df), base)
                # sys.stderr.write( 'tf_idf=',record[1]+'\n')
                postingList[2] = postingList[2] + tf
        # for i in xrange(self.__urlnum):  # for every urlnum
        for i, terms in self.__doc_term_list.iteritems():
            length = 0
            # for postingList in self.index.itervalues():  # for every term records
            for term in terms:
                postingList = self.index[term]
                records = postingList[1]
                tf_idf = records.get(i, [0, 0])[1]
                length = length + tf_idf * tf_idf
                # if i in records:
                #     sys.stderr.write( 'tf_idf = ', tf_idf+'\n')
                #     sys.stderr.write( 'changed vector length =',length+'\n')
            length = math.sqrt(length)
            # sys.stderr.write( i, 'vector length =',length+'\n')
            # for postingList in self.index.itervalues():  # for every term records
            for term in terms:
                postingList = self.index[term]
                records = postingList[1]
                if i in records:
                    record = records[i]
                    record[1] = record[1] / length
        sys.stderr.write('[Success]' + '\n')
        return

    def __str__(self):
        import locale
        res = ''
        for key, val in self.index.items():
            type(key)
            res = res + key.encode(locale.getpreferredencoding()) + '    ' + str(val[0]) + '    ' + '{'
            for i in xrange(self.__urlnum):
                res = res + str(i) + ':' + str(val[1].get(i, [0, 0.0]))
            res = res + '}' + '\n'
        return res

    def __repr__(self):
        return str(self)


if __name__ == '__main__':
    pass
    # import sys
    #
    # indexbuilder = IndexBuilder()
    # if '-r' not in sys.argv:
    #     urlnum = indexbuilder._IndexBuilder__urlnum
    #     files = ['test.html', 'test0.dat']
    #     for fileName, i in zip(files, xrange(urlnum, urlnum + len(files))):
    #         with open(fileName, 'r') as fin:
    #             indexbuilder.process(BeautifulSoup(fin), i)
    # indexbuilder.save()
