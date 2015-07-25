#encoding=utf-8
import jieba
import stem
import stop_words

class Parser(object):
    def __init__(self):
        self.__stemmer = stem.PorterStemmer()
        s = stop_words.get_stop_words('en')
        self.__stopwords = []
        for word in s:
            if word.isalpha():
                self.__stopwords.append(self.__stemmer.stem(word.lower(),0,len(word)-1))
        self.__stopwords = set(self.__stopwords)
    __punctuation = set([
    u'!',u'@',u'#',u'$',u'%',u'^',u'&',u'*',u'(',u')',u'_',u'+',u'-',u'=',u'~',u'`',
    u',',u'.',u'/',u';',u'\'',u'[',u']',u'\\',u'<',u'>',u'?',u':',u'\"',u'{',u'}',u'|'])#,
    # u'，',u'。',u'、',u'；',u'‘',u'’',u'【',u'】',u'、',u'《',u'》',u'？',u'：',u'“',u
    # u'”',u'｛',u'｝',u'|',u'￥',u'！',u'…',u'（',u'）',u'——',u'-'])
    def normalize(self,str):
        a = []
        for word in jieba.cut(str):
            word = word.strip()
            if word and word not in self.__punctuation: #and word not in self.__punctuation:
                if word.isalpha():
                    word = self.__stemmer.stem(word.lower(),0,len(word)-1)
                    if word not in self.__stopwords:
                        a.append(word)
                else:
                    if not word.isdigit():
                        a.append(word)
        return a

if __name__ == '__main__':
    import sys
    p = Parser()
    fin = open(sys.argv[1])
    for line in fin:
        words = p.normalize(line)
        for word in words:
            print word,