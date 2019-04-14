# -*- coding: utf-8 -*-
"""
Created on Fri Apr 12 10:06:39 2019

@author: Administrator
"""
import requests
from bs4 import BeautifulSoup
import os


def saveFile(title,time,category,content):
    '''
        保存文件的函数，默认保存在C盘 可修改
    '''
    cleantitle_temp = title.replace('"','')
    cleantitle = cleantitle_temp.replace('?','')
    directory = "C:\\爬虫数据2\\"+category #如果目录不存在 建立
    if not os.path.exists(directory):
        os.makedirs(directory)
    f = open(directory+"\\"+cleantitle+".txt",'w',encoding='utf-8')
    f.write(time+'\n'+content)
    f.close
    
def seekNextPageContent(url):
    '''
        寻找故事下一页的内容并返回，若无则结束
    '''
    ret = requests.get(url=url)
    ret.encoding = ret.apparent_encoding
    soup = BeautifulSoup(ret.text, 'html.parser')
    list1 = soup.select('.ari_content')
    story = ''
    i=0 #计数器 去除前两次加入的无关内容
    for contents in list1:
        content = contents.strings
        for sentence in content:
            if i>2:
                story+=sentence
            i+=1      
    cleanstory = story.split('Math.ceil(new Date()/3600000)')[1]
    if soup.select('.page .next'):
        nextPage = 'http://tool.xdf.cn'+soup.select('.page .next')[0].a['href']
        print(nextPage)
        cleanstory+=seekNextPageContent(nextPage)
    return cleanstory
    
def collectStory(url):
    #网址格式 http://tool.xdf.cn/th/result_(yiqianlingyiye)(2)-(10).html  
    #第一个括号内是童话故事的种类，第二个括号是第几篇故事 第三个括号是故事的第几页
    #url = 'http://tool.xdf.cn/th/result_yiqianlingyiye'+count+'.html'
    '''
        参数是故事第一页的url返回完整的一整篇故事
    '''
    ret = requests.get(url=url)
    ret.encoding = ret.apparent_encoding
    if ret.status_code!=200:
        return None #确保连接
    soup = BeautifulSoup(ret.text, 'html.parser')
    para = soup.find(name='div',class_='ari_content')   
    title = "".join(para.h1.string) #很重要，把NaString转化为普通str的方法
    time = "".join(para.p.span.string)[3:] #拔下来格式是 时间:xxxx-xx-xx xx 所以要去除前三个字符
    category = "".join(soup.find(name='div',class_='locations fix').p.select('a')[3].string)
    list1 = soup.select('.ari_content ')
    #list2 = para.find_all(name='p')
    story = ''
    i=0 #计数器 去除前两次加入的无关内容
    for contents in list1:
        content = contents.strings
        for sentence in content:
            if i>2:
                story+=sentence
            i+=1
    #cleanstory = story.split('Math.ceil(new Date()/3600000)')[1]
    print(url)
    allStory = seekNextPageContent(url)
    saveFile(title,time,category,allStory)

def readHomePageList(url="http://tool.xdf.cn/th/"):
    '''
        返回主页下的童话目录列表和网址 categorylist
    '''
    ret = requests.get(url=url)
    ret.encoding = ret.apparent_encoding
    if ret.status_code!=200:
        return None #确保连接
    soup = BeautifulSoup(ret.text, 'html.parser')
    list1 = soup.find(name='ul',class_='story_nav').select('li')
    categoryList = []
    for li in list1:
        if li.text:
            categoryUrl = "http://tool.xdf.cn"+li.a['href']
            categoryList.append(["".join(li.text),categoryUrl])
    return categoryList

def getStoryFromCategory(url,saveList=[]):
    '''
        第一个参数是种类目录下的第一页，第二个是遍历最后输出的保存list
        实现从第一页自动检索到最后一页，获取所有故事并保存
    '''
    ret = requests.get(url=url)
    ret.encoding = ret.apparent_encoding
    soup = BeautifulSoup(ret.text, 'html.parser')
    currentPage_li_list = soup.find(name='ul',class_='lists').select('li')
    for currentPage_li in  currentPage_li_list:
        storyUrl = "http://tool.xdf.cn"+currentPage_li.strong.a['href']
        print("收集故事url"+storyUrl+"进行爬虫")
        collectStory(storyUrl)
    if soup.select('.page .next'):
        nextPageUrl = "http://tool.xdf.cn"+soup.select('.page .next')[0].a['href']
        getStoryFromCategory(nextPageUrl,saveList)
 
def workStart():       
    '''
     爬虫工作的主程序
    '''
    categorys = readHomePageList()
    for category in categorys:
        print("开始进行"+category[0]+"类故事的爬虫")
        categoryUrl = category[1]
        getStoryFromCategory(categoryUrl)

        
workStart()