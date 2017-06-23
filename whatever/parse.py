#encoding=utf-8
from __future__ import print_function

# import jieba
import stem
import stop_words
import re
class Parser(object):
    def __init__(self):
        self.__stemmer = stem.PorterStemmer()
        s = stop_words.get_stop_words('en')
        self.__stopwords = []
        for word in s:
            if word.isalpha():
                self.__stopwords.append(self.__stemmer.stem(word.lower(),0,len(word)-1))
        self.__stopwords = set(self.__stopwords)
    __punctuation = {
    u'!',u'@',u'#',u'$',u'%',u'^',u'&',u'*',u'(',u')',u'_',u'+',u'-',u'=',u'~',u'`',
    u',',u'.',u'/',u';',u'\'',u'[',u']',u'\\',u'<',u'>',u'?',u':',u'\"',u'{',u'}',u'|'}#,
    # u'，',u'。',u'、',u'；',u'‘',u'’',u'【',u'】',u'、',u'《',u'》',u'？',u'：',u'“',u
    # u'”',u'｛',u'｝',u'|',u'￥',u'！',u'…',u'（',u'）',u'——',u'-'])
    def normalize(self,text):
        splited = self.cut(text)
        stemmed = [self.stem(word) for word in splited]
        rval = []
        for i in range(2):
            for j in range(len(stemmed)-i):
                rval.append(' '.join(stemmed[j:j+i+1]))
        return rval

    def cut(self, text):
        splitter = re.compile("\\W+")
        splited = [word.lower() for word in splitter.split(text) if word.strip() and word.lower() not in self.__stopwords]
        return splited

    def stem(self, word):
        return self.__stemmer.stem(word.lower(), 0, len(word) - 1)

parser = Parser()

if __name__ == '__main__':
    import sys
    p = Parser()
    fin = open(sys.argv[1])
    for line in fin:
        words = p.normalize(line)
        for word in words:
            print(word, end=' ')