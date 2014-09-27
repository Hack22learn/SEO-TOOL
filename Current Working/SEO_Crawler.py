# Extract All links of A website

import anydbm
import urllib2
import time

class database(object):
    def __init__(self):
        self.to_crawl = anydbm.open('Tocrawl.db', 'c')
        self.crawled = anydbm.open('crawled.db','c')
        self.len_crawled = 0
        self.len_to_crawl = 0
    
    def union(self,urls):
        #Take Union of new URLS found with to_crawl
        for url in urls:
            if url not in self.to_crawl:
                self.to_crawl[url]='?'
        self.len_to_crawl=len(self.to_crawl)
    
    def Update_crawled(self,url):
        #add url to crawled list
        self.crawled[url]='@'
        self.len_crawled +=1

    def next_link_2_crawl(self):
        # get a link from to_crawl 
        # return link and delete that key from to_crawl
        key=self.to_crawl.keys()[0] #get a key from to crawl
        del self.to_crawl[key] #delete that key from to_crawl
        self.len_to_crawl -=1 #decrement length of to crawl 
        return key
        
    def create_XML(self):
        # create XML file on basis of link in crawled
        f=open('sitemap.xml','w')
        for key in self.to_crawl:
            f.write(key+'\n')
        f.close()
    
    def close(self):
        #close all database and file
        self.to_crawl.close()
        self.crawled.close()


def find_main_domain(url):
    #This function use to exract main Body of URL
    #Example :> http://beginer2cs.blogspot.com  >>beginer2cs
    #        :> www.google.com >>google
    #        :>http://www.facebook.com >>facebook
    
    url=url.lower()
    if url.find("http://") !=-1 and url.count("/")>2:
        print 'Check You Url Format , Ex: www.helloworld.com >> No more "/" or anything allowed'
        return False
    elif url.find("http://") ==-1 and url.count("/")>0:
        print 'Check You Url Format , Ex: www.helloworld.com >> No more "/" or anything allowed'
        return False
    
    temp=url.find("www.")
    if temp !=-1:
        return url[temp+4:]
    elif url.find("http://") !=-1:
        return url[url.find("http://")+7:]
    else:
        return url
 
    
def do_crawl(link,domain):
    '''
       This function used to test this is not url for any download or image or anything we do't
       want to index by testing its end extention .i.e .img,.pdf,.css,.js
    '''
    if link.find(domain) !=-1 :
        if ('(' not in link) and (','not in link) and ("'" not in link) and ("#" not in link):
            temp=link[-6:]
            pos=temp.find('.')
            temp=temp[pos+1:]
            if temp in ['css','js','img','pdf','ico']:
                return False
            else:
                return True
        else:
            return False
    else:
        return False       


def link_create(cur_link,append_link):
    '''
      for link like href="test.html"
      it create whole link to fetch that url
    '''
    if append_link[0] not in './':
        return cur_link+'/'+append_link
    elif append_link[0] == '/':
        return cur_link+append_link
    elif append_link[0]=='.':
        back_url=0
        while True:
            if append_link.find('../')!=-1:
                back_url +=1
                append_link=append_link[3:]
            else:
                break
        try:
            count=0
            for j in range(len(cur_link)-1,-1,-1):
                if count == back_url+1:
                    cur_link=cur_link[:i+2]
                    break
                elif cur_link[i]=='/':
                    count +=1
            return cur_link+append_link
        except:
            return append_link
                    
    else:
        return append_link
    
    
def collect_all_link(page_data,cur_link,domain):
    '''
      collect all valid urls from a web page
      #Start Collecting Links after end of head tag </head>
    '''
    url=[]
    #Find </head> Start collecting link from there
    start_link=page_data.find('</head>')
    if start_link ==-1:
        return url
    
    while True:
        #   this loop is continued until all links are extracted i.e. no links are
        #   left in the page
        
        start_link=page_data.find("href=",start_link+1)
        if start_link == -1: #If No more URL left at that page break this loop
            break
        else:
            start_quote=page_data.find('"',start_link)
            end_quote=page_data.find('"',start_quote+1)
            
            temp_url=page_data[start_quote+1:end_quote]
            temp_url=temp_url.lower()
            
            if temp_url.find("http://") == -1 and ("www." not in temp_url ):
                    temp_url=link_create(cur_link,temp_url)
            elif 'http://' not in temp_url:
                temp_url='http://'+temp_url
                
            if do_crawl(temp_url,domain) and temp_url not in url:
                url.append(temp_url)
                
            
            
        
    return url

def connect_to_link(link):
    '''
      connect to given url and store data of that page in a variable
      then return that var
    '''
    try:
        response=urllib2.urlopen(link)
        page_data=response.read()
        return page_data
    except:
        return False


if __name__ == '__main__':
    first_link=raw_input("Enter Your Website URL \n Example : www.beginer2cs.blogspot.com \n:> ")
        
    ##TIme Stamp
    start_time=time.clock()
    count=0
    ##########################
    sitemap=database() #create Object
    sitemap.union([first_link]) #add base url to to_crawl
    #Start Crawl
    while sitemap.len_to_crawl >0:
        url=sitemap.next_link_2_crawl() #get Next link to crawl
        domain=find_main_domain(first_link)
        if domain !=False:
            page_data=connect_to_link(url)
            if page_data !=False:
                urls=collect_all_link(page_data,url,domain)
                sitemap.union(urls)
                sitemap.Update_crawled(url)
        ##Time Stamp Print
        count +=1
        if count==20:
            print time.clock-start_time(),'Sec\npage crawled->',sitemap.len_crawled,'\n page to crawl ->',sitemap.len_to_crawl
            count=0
    sitemap.create_XML()
    sitemap.close()
    raw_input('END')
