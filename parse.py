#encoding=utf-8
import jieba
import stem

class Parser(object):
    __stemmer = stem.PorterStemmer()
    # __punctuation = [
    # '!','@','#','$','%','^','&','*','(',')','_','+','-','=','~','`',
    # ',','.','/',';','\'','[',']','\\','<','>','?',':','\"','{','}','|',
    # '，','。','、','；','‘','’','【','】','、','《','》','？','：','“',
    # '”','｛','｝','|','￥','！','…','（','）','——','-']
    def normalize(self,str):
        a = []
        for word in jieba.cut(str):
            word = word.strip()
            if word: #and word not in self.__punctuation:
                if word.isalpha():
                   word = self.__stemmer.stem(word.lower(),0,len(word)-1)
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