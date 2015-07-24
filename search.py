#coding: utf-8


#搜索类
class searcher:

    #定义构造方法
    def __init__(self):
        with open('urllist', 'r') as f1: #打开文件urllist
            self.__num1 = int(f1.readline()) #总url数目
            self.__urladict = {}
            n = 0

            while n < self.__num1: #将url信息存入字典中
                s = f1.readline()
                arr = s.split(' ')
                urlid = int(arr[0]) #url ID
                url = arr[1] #url地址
                indegree = int(arr[2]) #url入度:用于计算PageRank
                outdegree = int(arr[3]) #url出度
                self.__urladict[urlid] = [url, indegree, outdegree]
                n = n + 1

            #其他操作

        #处理invertedindex文件

s = searcher()


