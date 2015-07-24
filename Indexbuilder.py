#coding=utf-8
from bs4 import BeautifulSoup
from parse import Parser
import math
# {
#     'term':
#         [
#             df=0,   #document frequency
#             {   #urlid-record dictionary
#                 urlid:  #   a record
#                     [
#                         tf=0,   #term frequency
#                         tf_idf=0    #normalized tf-idf
#                     ],
#                 urlid:  #   Another record
#                     [
#                         tf=0,
#                         tf_idf=0
#                     ]
#                 ...
#             }
#         ]
#     'Another term':
#         [
#             ...
#         ],
#     ...
# }
class IndexBuilder(object):
    def __init__(self):
        self.__p = Parser()
        self.index = {}
        self.__urlnum = 0
        try :
            with open('invertedindex','r') as fin:
                self.__urlnum = int(fin.readline())
                self.index = eval(fin.readline()+'\n')
        except IOError as err:
            print('Rebuild the Inverted Index')

    def process(self,html,urlid): 
        self.__urlnum = self.__urlnum + 1
        soup = BeautifulSoup(html,'html.parser')
        text = soup.get_text()
        for word in self.__p.normalize(text):
            # if word not in index :
            #     index.update({word:[0,{}]})
            records = self.index.setdefault(word,[0,{}])[1]
            # if urlid not in records :
            #     records.update({urlid:[0,0]})
            record = records.setdefault(urlid,[0,0])
            record[0] = record[0] + 1
        return
    def save(self):
        self.__calculateTf_idf()
        try :
            with open('invertedindex','w') as fout:
                print('Save back to \"invertedindex\"...')
                fout.write(str(self.__urlnum)+'\n')
                fout.write(repr(self.index))
        except IOError as err:
            print(err)
            print('Can not write back to \"invertedindex\"!!!')
        return

    def __calculateTf_idf(self) :
        #tf-idf = (1+log(tf,base))*log(N/df,base)
        base = 10
        for postingList in self.index.itervalues():
            postingList[0] = len(postingList[1])
            df = postingList[0]
            for record in postingList[1].itervalues():
                tf = record[0]
                record[1] = (1+math.log(tf,base))*math.log(self.__urlnum/float(df),base)
                # print (1+math.log(tf,base))
                # print '4/3=', 4/3
                # print math.log(4/3,base)
                # print 'tf=', tf, 'df=', df, 'urlnum=', self.__urlnum, 'tf-idf=', record[1]
        for i in xrange(self.__urlnum):    #for every urlnum
            length = 0
            for postingList in self.index.itervalues():  #for every term records
                records = postingList[1]
                tf_idf = records.get(i,[0,0])[1]
                length = length + tf_idf*tf_idf
            length = math.sqrt(length)
            # print 'doc', i, length
            for postingList in self.index.itervalues():  #for every term records
                records = postingList[1]
                if i in records:
                    record = records[i]
                    record[1] = record[1] / length
        return

    def __str__(self):
        import locale
        res = ''
        for key,val in self.index.items():
            type(key)
            res = res + key.encode(locale.getpreferredencoding()) +'    '+ str(val[0]) +'    ' + '{'
            for i in xrange(self.__urlnum):
                res = res + str(i) + ':' + str(val[1].get(i,[0,0.0]))
            res = res + '}' + '\n'
        return res

    def __repr__(self):
        return str(self)
    
if __name__ == '__main__':
    import sys
    indexbuilder = IndexBuilder()
    urlnum = indexbuilder._IndexBuilder__urlnum
    files = ['test0.dat','test1.dat']
    for fileName, i in zip(files, xrange(urlnum, urlnum + len(files))):
        # print fileName
        # print type(fileName)
        with open(fileName,'r') as fin:
            indexbuilder.process(fin,i)
    indexbuilder.save()
    print(indexbuilder)

