import requests;
import os,re,urllib,uuid
from bs4 import BeautifulSoup;
import time;
from urllib.error import URLError, HTTPError, ContentTooShortError
from random import choice

totalSize = 0
fileNum = 0
dirNum = 0
#currentURL='http://www.crayola.com/free-coloring-pages/seasons/'
currentURL='http://www.crayola.com/free-coloring-pages/seasons/?page=6&count=24'
#startURL='http://www.crayola.com/free-coloring-pages/seasons/'
startURL='http://www.crayola.com/free-coloring-pages/all/'
baseURL='http://www.crayola.com'
localPath='d:\\download'
NextEnabled=True
localDownLoadPath=""
parentPage=[]
#headers = {'User-agent' : 'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:22.0) Gecko/20100101 Firefox/22.0'}
user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36"
headers={"User-Agent":user_agent}
dic = {}
#proxy_list = [
#    {"http" : "61.135.217.7:80"},
#    {"http" : "122.114.31.177:808"},
#    {"http" : "115.55.150.160:8118"}
#]
proxy_list=None

def download(url, num_retries=2, user_agent='wswp', proxies=None):
    """ Download a given URL and return the page content
        args:
            url (str): URL
        kwargs:
            user_agent (str): user agent (default: wswp)
            proxies (dict): proxy dict w/ keys 'http' and 'https', values
                            are strs (i.e. 'http(s)://IP') (default: None)
            num_retries (int): # of retries if a 5xx error is seen (default: 2)
    """
    headers = {'User-Agent': user_agent}
    try:
        aProxy = choice(proxies) if proxies else None
        resp = requests.get(url, headers=headers, proxies=aProxy)
        html = resp.text
        if resp.status_code >= 400:
            print('Download error:', resp.text)
            html = None
            if num_retries and 500 <= resp.status_code < 600:
                # recursively retry 5xx HTTP errors
                return download(url, num_retries - 1)
    except requests.exceptions.RequestException as e:
        print('Download error:', e)
        html = None
    return html

def find_n_sub_str(src, sub, pos, start):
    index = src.find(sub, start)
    if index != -1 and pos > 0:
        return find_n_sub_str(src, sub, pos - 1, index + 1)
    return index

def visitDir(path):
    global totalSize
    global fileNum
    global dirNum
    fileNum=0
    dirNum=0
    totalSize=0
    isExists=os.path.exists(path)
    if isExists:
        for lists in os.listdir(path):
            sub_path = os.path.join(path, lists)
            #print(sub_path)
            if os.path.isfile(sub_path):
                fileNum = fileNum+1                      # 统计文件数量
                totalSize = totalSize+os.path.getsize(sub_path)  # 文件总大小
            elif os.path.isdir(sub_path):
                dirNum = dirNum+1                       # 统计文件夹数量
                visitDir(sub_path)                           # 递归遍历子文件夹

def findShowAll():
    html=download(startURL,3,user_agent,proxy_list)
    soup=BeautifulSoup(html, "html.parser");
    showAllLink=soup.find_all(id="hlViewAll");    
    for i in showAllLink:
        print(i['href'])
        index=find_n_sub_str(i['href'],'/',1,0)
        lastIndex=find_n_sub_str(i['href'],'/',2,0)
        title=i['href'][index+1:lastIndex]       
        newtitle=title.replace("-"," ").replace("and","&")
        print(title + " " + newtitle)
        localDownLoadPath=localPath + '\\'+newtitle;
        visitDir(localDownLoadPath)
        print()
        totalNum=int(i.parent.find_next_sibling().text)
        print("totalNum: " + str(totalNum) + " " + localDownLoadPath +" file num: " + str(fileNum))
        if totalNum> fileNum:
            parentPage.append(i['href'])
             

def getURLs(url,newDir=False):
    global NextEnabled;
    global currentURL;
    global localDownLoadPath;
    NextEnabled=False;
    existDir=True;
    time.sleep(10);
    html=download(url,3,user_agent,proxy_list);
    soup=BeautifulSoup(html, "html.parser");
    title=soup.find(id="cpHeaderSEO").getText();    
    localDownLoadPath=localPath + '\\'+title;
    
    if newDir:
        mkdir(localDownLoadPath);
    if existDir:
        links=soup.find_all(id="hlTitle");
        nextPage=soup.find(id="hlNextPage");
        if not nextPage['href']:
            nextPageClass=nextPage['class'];
            nextPageClass[0];
            if len(nextPageClass)==1:
                currentURL= baseURL + nextPage['href'];
                NextEnabled=True;
        list=[];
        for c in links:
            list.append(c);
        return list

def gotoDetailURL(urlList):   
    for url in urlList:
        print("----------------------------------------------------")
        print("url: "+url['href'])
        time.sleep(20);
        html=download(url['href'],3,user_agent,proxy_list)
        if html:
            soup=BeautifulSoup(html, "html.parser");
            printLink=soup.find(id="uxPrintLink");
            fileName=soup.find('h1').getText()
            fileName=fileName.replace("?","").replace("!","")            
            if printLink['href'].endswith("pdf"):
                fileName=fileName+'.pdf'
                fullFileName=createFileWithFileName(localDownLoadPath,fileName)                                 
                if not fullFileName is None:
                    if os.path.getsize(fullFileName) ==0:
                        print("retrieve file")
                        urllib.request.urlretrieve(printLink['href'].replace(" ","%20"),fullFileName)
                continue
            fileName=fileName+'.jpg'
            gotoDownloadURL(printLink,fileName);  

def gotoDownloadURL(printLink,fileName):
    time.sleep(20);
    html=download(printLink['href'],3,user_agent)
    if html:
        soup=BeautifulSoup(html, "html.parser");    
        img=soup.find('img')
        imgUrl=baseURL+img['src']
        imgUrl=imgUrl.replace(" ","%20")
        print("imgUrl: "+imgUrl);
        print("fileName: "+fileName);
        fullFileName=createFileWithFileName(localDownLoadPath,fileName)     
        if not fullFileName is None:
            if os.path.getsize(fullFileName) ==0:
                print("retrieve file")
                urllib.request.urlretrieve(imgUrl,fullFileName) 

def getFile(url,file_name):
    print("getfile url "+url)
    u = urllib.request.urlopen(url)
    f = open(file_name, 'wb')

    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break

        f.write(buffer)
    f.close()
    print ("Sucessful to download" + " " + file_name)

#根据文件名创建文件  
def createFileWithFileName(localPathParam,fileName): 
  totalPath=localPathParam+'\\'+fileName 
  if not os.path.exists(totalPath): 
    file=open(totalPath,'a+') 
    file.close() 
    return totalPath

#生成一个文件名字符串  
def generateFileName(): 
  return str(uuid.uuid1()) 

def mkdir(path):
    # 引入模块
    import os
 
    # 去除首位空格
    path=path.strip()
    # 去除尾部 \ 符号
    path=path.rstrip("\\")
 
    # 判断路径是否存在
    # 存在     True
    # 不存在   False
    isExists=os.path.exists(path)
     
    # 判断结果
    if not isExists:
        # 如果不存在则创建目录
        # 创建目录操作函数
        os.makedirs(path) 
 
        print( path+' 创建成功')
        return True
    else:
        # 如果目录存在则不创建，并提示目录已存在
        print( path+' 目录已存在')
        return False


def starter():
    global NextEnabled;
    for i in parentPage:        
        print(i);
        urlList=getURLs(baseURL + i,True)
        if not urlList is None:
            gotoDetailURL(urlList)
        while(NextEnabled==True):
            print(currentURL)
            NextEnabled=False        
            urlList=getURLs(currentURL)
            if not urlList is None:
                gotoDetailURL(urlList)
        
     

#fileName='Art With Edge Say What?!.jpg'
#fileName=fileName.replace("?","").replace("!","")
#print(fileName)
findShowAll()
parentPage.append('/free-coloring-pages/dome-light-designer/dome-light-designer-coloring-pages/')
parentPage.append('/free-coloring-pages/see-thru-light-designer/see-thru-light-designer-scenes-coloring-pages/')
parentPage.append('/free-coloring-pages/tracing/light-up-tracing-pad-coloring-pages/')
starter()
