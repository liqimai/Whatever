#coding=utf-8
from bs4 import BeautifulSoup
from parse import Parser
import math
import json
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
    def __init__(self,invertedindex='invertedindex'):
        self.__p = Parser()
        self.index = {}
        self.__urlnum = 0
        self.__fileName = invertedindex
        try :
            with open(invertedindex,'r') as fin:
                sys.stderr.write( 'Reading invertedindex in...')
                self.__urlnum = int(fin.readline())
                line = fin.readline()
                self.index = json.loads(line)
                # i = 0
                # key = ''
                # val = ''
                # for line in fin:
                #     if i == 0:
                #         key = eval(line)
                #     if i == 1:
                #         val = eval(line)
                #         self.index.update({key:val})
                sys.stderr.write( '[Success]'+'\n')
        except IOError as err:
            sys.stderr.write( str(type(err)) + str(err.args)+'\n')
            sys.stderr.write('Will rebuild the Inverted Index'+'\n')

    def process(self,soup,urlid): 
        urlid = str(urlid)
        self.__urlnum = self.__urlnum + 1
        text = soup.get_text()
        length = 0
        if text :
            for word in self.__p.normalize(text):
                records = self.index.setdefault(word,[0,{},0])[1]
                record = records.setdefault(urlid,[0,0])
                record[0] = record[0] + 1
                length = length + 1
        try :
            title = soup.title.string
        except:
            title = None
        if title is not None:
            title = unicode(title)[:-16]*5
        if title :
            for word in self.__p.normalize(title):
                records = self.index.setdefault(word,[0,{},0])[1]
                record = records.setdefault(urlid,[0,0])
                record[0] = record[0] + 1
                length = length + 1

        return length

    def save(self):
        self.__calculateTf_idf()
        try :
            with open(self.__fileName,'w') as fout:
                sys.stderr.write( 'Save back to \"invertedindex\"...')
                fout.write(str(self.__urlnum)+'\n')
                fout.write(json.dumps(self.index))
                # for key,value in self.index.items():
                #     fout.write(repr(key)+'\n')
                #     fout.write(repr(value)+'\n')
                sys.stderr.write( '[Success]'+'\n')

        except IOError as err:
            sys.stderr.write(str(err)+'\n')
            sys.stderr.write('Can not write back to \"invertedindex\"!!!'+'\n')
        return

    def __calculateTf_idf(self) :
        sys.stderr.write( 'Calculating...')
        #tf-idf = (1+log(tf,base))*log(N/df,base)
        base = 10
        for postingList in self.index.itervalues():
            postingList[0] = len(postingList[1])
            df = postingList[0]
            postingList[2] = 0
            for record in postingList[1].itervalues():
                tf = record[0]
                record[1] = (1+math.log(tf,base))*math.log(self.__urlnum/float(df),base)
                # sys.stderr.write( 'tf_idf=',record[1]+'\n')
                postingList[2] = postingList[2] + tf
        for i in xrange(self.__urlnum):    #for every urlnum
            i = str(i)
            length = 0
            for postingList in self.index.itervalues():  #for every term records
                records = postingList[1]
                tf_idf = records.get(i,[0,0])[1]
                length = length + tf_idf*tf_idf
                # if i in records:
                #     sys.stderr.write( 'tf_idf = ', tf_idf+'\n')
                #     sys.stderr.write( 'changed vector length =',length+'\n')
            length = math.sqrt(length)
            # sys.stderr.write( i, 'vector length =',length+'\n')
            for postingList in self.index.itervalues():  #for every term records
                records = postingList[1]
                if i in records:
                    record = records[i]
                    record[1] = record[1] / length
        sys.stderr.write( '[Success]'+'\n')
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
    if '-r' not in sys.argv:
        urlnum = indexbuilder._IndexBuilder__urlnum
        files = ['test.html','test0.dat']
        for fileName, i in zip(files,xrange(urlnum,urlnum+len(files))):
            with open(fileName,'r') as fin:
                indexbuilder.process(BeautifulSoup(fin),i)
    indexbuilder.save()

