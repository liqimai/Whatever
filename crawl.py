#coding=utf-8
import os
import time
import urllib2
from bs4 import BeautifulSoup
import socket

class crawl:
	baseurl=''
	req_header = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}
	req_timeout = 5
	urlqueue=[]
	urls=[]
	head=[]
	count=0
	read_web=set()
	
	def __init__(self,baseurl):#将主网址加入集合
		self.baseurl=baseurl
		self.read_web.add(baseurl)

	
	def user_agent(self,url): #宽度优先遍历网页
		try:
			print("it's the %d time"%(self.count))
			self.count=self.count+1
			if(self.count<=100):#搜索网页数
       				req = urllib2.Request(url,None,self.req_header)
        			page = urllib2.urlopen(req,None,self.req_timeout)
        			html = page.read()
				page.close()
				soup = BeautifulSoup(html)
				
				#getinf(html,url) 李奇卖实现
				
				self.urls.append(url)
				a = soup.find_all(['a'])
				for i in a:
					tmpurl=i.get('href')
					if(tmpurl is not None and tmpurl.find('javascript')==-1):
						if(tmpurl.find('http')==-1):
							tmpurl=self.baseurl+'/'+tmpurl
						if(tmpurl not in self.read_web):
							#print(tmpurl)
							self.read_web.add(tmpurl)
							self.urlqueue.append(tmpurl)
							tmpurl=''
				#c=raw_input()
				time.sleep(0.1)
				nexturl=self.urlqueue.pop(0)
				self.user_agent(nexturl)
			else: #结束了
				with open('data','a') as FILE:
					for item in self.urls:
						try:
							FILE.write(item+'\n')
						except:
							print ('data wrong')
							pass
				with open('queue','w') as qq:
					for item in self.urlqueue:
						try:
							qq.write(item+'\n')
						except:
							print ('queue wrong')
							pass
			#return html
		except urllib2.URLError as e:
        		print e.message
        		self.user_agent(self.urlqueue.pop(0))
		except socket.timeout as e:
        		self.user_agent(self.urlqueue.pop(0))

	
	def fillset(self,data,queue):#将以前访问过的网站加入set，重新获取queue
		with open(data) as FILE:
			for item in FILE.readlines():
				self.read_web.add(item.strip('\n'))
		with open(queue) as FILE1:
			for item in FILE1.readlines():
				self.urlqueue.append(item.strip('\n'))
		self.baseurl=self.urlqueue.pop(0)#重设主网址
		self.read_web.add(self.baseurl)

	
	#def getinf(html,url) 获取网页名和item的位置信息等

#main
baseurl="http://www.cc98.org"
cc=crawl(baseurl)
if(os.path.exists('/home/fhl/Documents/py/ir/data') and os.path.exists('/home/fhl/Documents/py/ir/queue')):
	cc.fillset('data','queue') #检查是否继续上次爬取
	cc.user_agent(cc.baseurl)
else:
	cc.user_agent(baseurl)
