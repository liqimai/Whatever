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
	indegree=[]
	outdegree=[]
	head=[]
	totalcount=0
	count=0
	read_web=set()
	
	def __init__(self,baseurl):#将主网址加入集合
		self.baseurl=baseurl

	
	def user_agent(self,url): #宽度优先遍历网页
		try:
			if(url in self.read_web):
				try:
					self.indegree[self.urls.index(url)]+=1
				except:
					pass
				if(len(self.urlqueue)>0):
					self.user_agent(self.urlqueue.pop(0))
			else:
				self.read_web.add(url)
				tmpoutdegree=0
				print("it's the %d time"%(self.count))
				self.count=self.count+1
				if(self.count<=100):#搜索网页数
       					req = urllib2.Request(url,None,self.req_header)
        				page = urllib2.urlopen(req,None,self.req_timeout)
        				html = page.read()
					page.close()
					soup = BeautifulSoup(html,'lxml')			
					self.urls.append(url)
					self.indegree.append(1)

					#ibuilder.process(urls.size()-1,html) 李奇卖实现

					a = soup.find_all(['a'])
					for i in a:
						tmpurl=i.get('href')
						if(tmpurl is not None and tmpurl.find('javascript')==-1):
							if(tmpurl.find('http')==-1):
								tmpurl=self.baseurl+'/'+tmpurl
							if(tmpurl.find('www.cc98.org')!=-1):
								#print(tmpurl)
								self.urlqueue.append(tmpurl)
								tmpurl=''
								tmpoutdegree=tmpoutdegree+1
					#c=raw_input()
					self.outdegree.append(tmpoutdegree)
					time.sleep(0.1)
					nexturl=self.urlqueue.pop(0)
					self.user_agent(nexturl)
				else: #结束了
					with open('queue','w') as qq:
						for item in self.urlqueue:
							try:
								if(item is not None):
									qq.write(item+'\n')
							except:
								print ('queue wrong but things well')
								pass
			
					with open('urllist','w') as uu:
						uu.write('%d\n'%(len(self.urls)))
						i=0
						for item in self.urls:
							try:
								uu.write('%d %s %d %d\n'%(i,item,self.indegree[i],self.outdegree[i]))
								i+=1
							except:
								print('%d %s %d %d\n'%(i,item,self.indegree[i],self.outdegree[i]))
								print ('urls output wrong')
								pass
				#return html
		except urllib2.URLError as e:
        		print e.message
        		self.user_agent(self.urlqueue.pop(0))
		except socket.timeout as e:
        		self.user_agent(self.urlqueue.pop(0))
		except:
			pass
	

	def fillset(self,urllist,queue):#将以前访问过的网站加入set，重新获取queue
		with open(urllist,'r') as FILE:
			totalcount=FILE.readline()
			for item in FILE.readlines():
				try:
					(tmpid,tmpurl,tmpind,tmpoud)=(item.strip('\n').split(' '))
					self.urls.append(tmpurl)
					self.read_web.add(tmpurl)
					self.indegree.append(int(tmpind))
					self.outdegree.append(int(tmpoud))
				except:
					print('read in data error')

		with open(queue,'r') as FILE1:
			for item in FILE1.readlines():
				try:
					self.urlqueue.append(item.strip('\n'))
				except:
					print('read queue in error but well')
		self.baseurl=self.urlqueue.pop(0)#重设主网址

#main
baseurl="http://www.cc98.org"
cc=crawl(baseurl)
if(os.path.exists('urllist') and os.path.exists('queue')):
	cc.fillset('urllist','queue') #检查是否继续上次爬取
	cc.user_agent(cc.baseurl)
else:
	cc.user_agent(baseurl)
