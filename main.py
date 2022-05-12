'''
数据结构：静态链表
方式：采取先读取，后生成的方式。
具体步骤：
        1.读取source目录下文件
        2.文件细节插入到数据结构中
        3.排序
        4.使用线程，分段生成网页
        5.生成目录，并结束
'''
import os, markdown, re, time
# from pathlib import Path

class thread_str(object):
    def __init__(self,first, last):
        self.first = first
        self.last = last
        print("采取分段分块进行网页的生成，该段区间为[%s , %s)" %(self.first, self.last))
        
class Node:  #用于存放数据的结点，搭配列表使用
    def __init__(self, title=None, date=None, tags=None, md_url=None,topping=None, is_archive=None,kwds=None, descri=None):
        self.title = title              #标题
        self.date = date                #创建时间
        self.tags = tags                #标签
        self.md_url = md_url            #makdown文章地址
        self.topping = topping          #置顶
        self.is_archive = is_archive    #archive页收录
        self.keywords = kwds            #文章关键词 
        self.description = descri       #文章摘要

class md2html(object):
    pages = 0                            #页数
    articleMax = 40                      #设置每页文章数
    post_num = 0                         #文章数量
    is_only2page = False                 #总共只有2页判断
    template_post = None                 #文章模板
    template_acrchive = None             #archive页模板                 
    archlink_Detail = None               #archive页文章链接处细节模板
    page_nav_l = None                    #各个pages里面prev next按钮
    page_nav_r = None    
    pattern = ['title:(.*?)\n', 'date:(.*?)\n', 'tags:(.*?)\n', 'priv:(.*?)\n', \
                'top:(.*?)\n', 'is_archive:(.*?)\n', 'keywords:(.*?)\n', 'description:(.*?)\n' ] 
    tagg = [ "无标题", "1997-01-01 19:12:00", "life", "No", "No", "Yes", "", "" ]
    def __init__(self, base=None, site_name=None, site_UL=None):
        self.base = base
        self.site_name = site_name
        self.arr = []
        self.site_url = site_UL
    
    def findAllFile(self):
        for root, ds, fs in os.walk(self.base):
            for f in fs:
                yield os.path.join(root,f)
 
    def GetmdDetail(self, md_addr):    
        if md_addr is not None: #传递的不是空地址
            try:
                with open(md_addr, 'r', encoding='utf-8') as raw_File:
                    raw_Data = raw_File.read()
            except:
                print("文件地址不对！")
                return None
            '''
              说明：采取的是列表之间对比，列表needthing作为匹配结果，列表tagg作为设置的原始值，
            '''
            needthing = [] #title 0, date 1, tags 2, private 3, topping 4, is_archive 5, keywords 6, description 7
            
            length = len(self.pattern)
            
            for k in range(length):
                matchaddr = re.search(self.pattern[k], raw_Data, re.S)  #循环匹配
                if matchaddr is not None:           #排查：如果md文件里面没有设置参数
                    needthing.append(matchaddr.group(1))
                else:
                    needthing.append(self.tagg[k])
            for m in range(length):
                if needthing[m].replace(" ", "") == "":       #排查：如果md文件里面设置了参数但是没值
                    if m == 6:
                        needthing[m] = needthing[0] + "," + self.site_name   #keywords
                    elif m == 7:
                        needthing[m] = needthing[0]             #description
                    else:
                        needthing[m] = self.tagg[m] 
            if(needthing[3] == "No"):
                '''           
                这里有点多此一举，不过这个程序以前的版本：元素最开始不是存储在列表needthing里面的。
                而现在为了节省代码量就使用了列表needthing，其实是可以直接插入列表的，形成二维列表，不过后面的形式要更改，
                捡懒就这样了。
                '''
                self.arr.append(Node(needthing[0], needthing[1], needthing[2], md_addr, needthing[4], needthing[5], needthing[6], needthing[7]))
            else:
                print("文章：《%s》保密%s，不生成HTML，地址为：%s\n"%(needthing[0], needthing[3], md_addr) ) 
            del needthing
        else:
            return None
            
    def PrintArr(self):
        for n in self.arr:
            print("《%s》，写于：%s，%s"%(n.title, n.date, n.md_url))
        print('\n')

    def HTML_url(self, md_addr, parse_to_html=None):
        if parse_to_html == True:
            return  md_addr.replace(self.base, "/posts").replace("\\", "/").replace(".md", ".html") 
        else:
            return  md_addr.replace(self.base, "posts").replace("\\", "/").replace(".md", ".html")
        #return ( '%s.html'%(os.path.basename(md_addr).lower().replace('.md', '')) )
        
    def parse_to_HTML(self, listNumber, str):
        prev_article = None  # 时间距离最远的文章为 上一篇 列表序号最大处方向
        next_article = None  # 时间距离最近的文章为 下一篇 列表序号为0处方向
        
        if(0 == listNumber):
            next_article = "下一篇：没有了"
        else:
            next_article = '下一篇：<a href="'+self.HTML_url(self.arr[listNumber-1].md_url, True)+'">'+self.arr[listNumber-1].title+'</a>' #<a href="{{next_article}}">下一篇</a>
        
        if(self.post_num-1 == listNumber):
            prev_article = "上一篇：没有了"
        else:
            prev_article = '上一篇：<a href="'+self.HTML_url(self.arr[listNumber+1].md_url, True)+'">'+self.arr[listNumber+1].title+'</a>' #<a href="{{prev_article}}">上一篇</a>
        
        with open(self.arr[listNumber].md_url, 'r', encoding='utf-8') as raw_File:
            raw_Data = raw_File.read()        

        out_path = self.HTML_url(self.arr[listNumber].md_url)  #输出地址及HTML文件名称结构
        html_content = markdown.markdown(raw_Data,extensions=[ \
                               # 'markdown.extensions.toc',\
                               'markdown.extensions.tables', \
                               'markdown.extensions.fenced_code', \
                               'markdown.extensions.meta'] \
                               )
        post_html_content = self.template_post.replace('{{title}}', self.arr[listNumber].title)\
            .replace('{{site-name}}',self.site_name)\
            .replace('{{date}}', self.arr[listNumber].date)\
            .replace('{{post-content}}', html_content)\
            .replace('{{tags}}', self.arr[listNumber].tags)\
            .replace('{{prev_article}}',prev_article)\
            .replace('{{next_article}}',next_article)\
            .replace('{{keywords}}', self.arr[listNumber].keywords)\
            .replace('{{description}}',self.arr[listNumber].description)
        
        with open(out_path, 'w', encoding='utf-8', errors='xmlcharrefreplace') as out_File:
            out_File.write(post_html_content)
        print('使用线程%s生成文章：《%s》,其标签为：%s，地址在：%s'%(str, self.arr[listNumber].title, self.arr[listNumber].tags, out_path))
            
    def Create_archive(self):
        print('生成目录中')
        temp = self.archlink_Detail[0]
        temp_first = self.archlink_Detail[1]
        page_nav_l = self.page_nav_l
        page_nav_r = self.page_nav_r
        posts_url = None
        if (self.post_num <= self.articleMax): #只有一页 a
            print("a")
            s1 = ''
            for i in range(0, self.post_num):   
                if self.arr[i].is_archive == "Yes":
                    a = temp_first.replace('{{date}}',self.arr[i].date.replace(" ", "")[0:10])\
                    .replace('{{md_url}}',self.HTML_url(self.arr[i].md_url))\
                    .replace('{{post_name}}',self.arr[i].title)               
                    s1 =  s1+a
                else:
                    continue
            posts_url = "index.html"
            with open(posts_url,'w',encoding='utf-8') as only_onepg:
                only_onepg.write(self.template_acrchive.replace('{{page_nav}}',s1)\
                .replace('{{title}}',self.site_name)\
                .replace('{{site-name}}',self.site_name)\
                .replace('{{nav}}',''))                 
            self.sitemap(posts_url)
        elif(self.pages == 1): #第一页没有pre b
            print("b")
            s1 = ''
            for i in range(0, self.articleMax):    
                if self.arr[i].is_archive == "Yes":
                    a = temp_first.replace('{{date}}',self.arr[i].date.replace(" ", "")[0:10])\
                    .replace('{{md_url}}',self.HTML_url(self.arr[i].md_url))\
                    .replace('{{post_name}}',self.arr[i].title)       
                    s1 =  s1+a
                else:
                    continue
            posts_url = "index.html"
            with open(posts_url,'w',encoding='utf-8') as pg:
                pg.write(self.template_acrchive\
                .replace('{{page_nav}}',s1)\
                .replace('{{title}}',self.site_name)\
                .replace('{{site-name}}',self.site_name)\
                .replace('{{nav}}',page_nav_r.replace('{{right-link}}','pages/'+str(self.pages+1)+'.html')))
            self.sitemap(posts_url)
        elif(self.pages == 2 and (self.is_only2page != True) ): #由递归衰减而到的第2页 c
            print("c")
            s1 = ''
            for i in range(self.articleMax, self.pages*self.articleMax):   
                if self.arr[i].is_archive == "Yes":
                    a = temp.replace('{{date}}',self.arr[i].date.replace(" ", "")[0:10])\
                    .replace('{{md_url}}',self.HTML_url(self.arr[i].md_url))\
                    .replace('{{post_name}}',self.arr[i].title)       
                    s1 =  s1+a
                else:
                    continue
            posts_url = "pages/" + str(self.pages)+".html"
            with open(posts_url,'w',encoding='utf-8') as pg:
                pg.write(self.template_acrchive\
                .replace('{{page_nav}}',s1)\
                .replace('{{title}}','第'+str(self.pages)+'页 | '+ self.site_name)\
                .replace('{{site-name}}',self.site_name)\
                .replace('{{nav}}', page_nav_l.replace('{{left-link}}','../index.html')+page_nav_r.replace('{{right-link}}',str(self.pages+1)+'.html')))
            self.sitemap(posts_url)    
        elif(self.is_only2page): #如果一开始就是只有2页便执行如下代码 d
            print("d")
            s1 = ''
            for i in range(self.articleMax, self.post_num):   
                if self.arr[i].is_archive == "Yes":     
                    a = temp.replace('{{date}}',self.arr[i].date.replace(" ", "")[0:10])\
                    .replace('{{md_url}}',self.HTML_url(self.arr[i].md_url))\
                    .replace('{{post_name}}',self.arr[i].title)       
                    s1 =  s1+a
                else:
                    continue
            posts_url = "pages/" + str(self.pages)+".html"
            with open(posts_url,'w',encoding='utf-8') as pg:
                pg.write(self.template_acrchive\
                .replace('{{page_nav}}',s1)\
                .replace('{{title}}','第'+str(self.pages)+'页 | '+ self.site_name)\
                .replace('{{site-name}}',self.site_name)\
                .replace('{{nav}}', page_nav_l.replace('{{left-link}}','../index.html')))
            self.sitemap(posts_url)
        elif(self.pages*self.articleMax >= self.post_num and ((self.pages-1)*self.articleMax <= self.post_num ) ): #最后一页 e
            print("e")
            s1 = '' 
            for i in range((self.pages-1)*self.articleMax, self.post_num):
                if self.arr[i].is_archive == "Yes":
                    a = temp.replace('{{date}}',self.arr[i].date.replace(" ", "")[0:10])\
                    .replace('{{md_url}}',self.HTML_url(self.arr[i].md_url))\
                    .replace('{{post_name}}',self.arr[i].title)       
                    s1 =  s1+a
                else:
                    continue
            posts_url = "pages/" + str(self.pages)+".html"
            with open(posts_url,'w',encoding='utf-8') as pg:
                pg.write(self.template_acrchive\
                .replace('{{page_nav}}',s1)\
                .replace('{{title}}','第'+str(self.pages)+'页 | '+ self.site_name)\
                .replace('{{site-name}}',self.site_name)\
                .replace('{{nav}}', page_nav_l.replace('{{left-link}}',str(self.pages-1)+'.html')))
            self.sitemap(posts_url) 
        else:  #一般页面 f
            print("f")
            s1 = ''
            for i in range((self.pages-1)*self.articleMax, (self.pages-1)*self.articleMax+self.articleMax):
                if self.arr[i].is_archive == "Yes":
                    a = temp.replace('{{date}}',self.arr[i].date.replace(" ", "")[0:10])\
                    .replace('{{md_url}}',self.HTML_url(self.arr[i].md_url))\
                    .replace('{{post_name}}',self.arr[i].title)       
                    s1 =  s1+a
                else:
                    continue
            with open('pages/'+str(self.pages)+'.html','w',encoding='utf-8') as pg:
                pg.write(self.template_acrchive\
                .replace('{{page_nav}}',s1)\
                .replace('{{title}}','第'+str(self.pages)+'页 | '+ self.site_name)\
                .replace('{{site-name}}',self.site_name)\
                .replace('{{nav}}', page_nav_l.replace('{{left-link}}',str(self.pages-1)+'.html')+page_nav_r.replace('{{right-link}}',\
                str(self.pages+1)+'.html')))
            self.sitemap("pages/" + str(self.pages)+".html")
        self.pages -=1
        if self.pages >0:
            self.Create_archive()

    def sitemap(self, URL=None): #生成站点地图sitemap.txt
        if URL == None:
            sitemapstring = ""
            for i in self.arr:
                sitemapstring = sitemapstring + self.site_url +"/"+self.HTML_url(i.md_url) + "\n"
            try:
                with open("sitemap.txt", "w",encoding="utf-8") as sitemap:
                    sitemap.write(sitemapstring)
                sitemap.close()
            except:
                return False
        else:
            try:
                with open("sitemap.txt", "a",encoding="utf-8") as sitemap:
                    sitemap.write(self.site_url + "/"+URL + "\n")
                sitemap.close()
            except:
                return False
        return True

    def parse_main(self, thread_str, str):    #线程调用函数
        first = thread_str.first
        last = thread_str.last
        for i in range(first,last):
            if i < 5:             #默认解析列表前5篇文章
                self.parse_to_HTML(i, str)
            elif os.path.isfile(self.HTML_url(self.arr[i].md_url) ):  #如果后面的存在就不解析，不存在就解析               
                continue
            else:
                self.parse_to_HTML(i, str)  

    def preFunc(self):  #预先处理
        '''预先判定这几个文件夹是否存在： source  pages   template   '''            
        if os.path.isdir(self.base):
            pass
        else:
            os.mkdir(self.base)
            print(self.base + "文件夹不存在，已帮忙创建！")
            return False
        if os.path.isdir("pages"):
            pass
        else:
            os.mkdir("pages")
            print("pages文件夹不存在，已帮忙创建！")
            return False
        if os.path.isdir("template"):
            pass
        else:
            os.mkdir("template")
            print("template文件夹不存在，已帮忙创建！")
            return False
        if os.path.isdir("posts"):
            pass
        else:
            os.mkdir("posts")
            print("posts文件夹不存在，已创建！")
            return False        
        if os.path.isfile('template/post_tem.html') and os.path.isfile('template/archive_tem.html') and os.path.isfile('template/archlink_Detail.html'):
            with open('template/post_tem.html','r',encoding='utf-8') as aa:
                self.template_post = aa.read()
            with open('template/archive_tem.html','r',encoding='utf-8') as bb:
                self.template_acrchive= bb.read()
            with open('template/archlink_Detail.html','r',encoding='utf-8') as cc:
                archlink_Detail_data = cc.read()
            self.archlink_Detail = re.compile('archive_post:(.*?)\n', re.S).findall(archlink_Detail_data) # return list
            self.page_nav_l = re.search('page_nav_l:(.*?)\n', archlink_Detail_data, re.S).group(1)
            self.page_nav_r = re.search('page_nav_r:(.*?)\n', archlink_Detail_data, re.S).group(1)
        else:
            print("模板文件夹里面欠缺必要的文件！\n 请参考：https://github.com/qing2zijin/staticblog 进行搭建")
            return False 
            
        for md in self.findAllFile():                
            parent_dir = (os.path.dirname(md) ).replace(self.base, "posts")  # 不换就是：source   source/gongkao_zhuanlan
            if parent_dir == "posts":
                pass
            elif os.path.isdir(parent_dir):
                pass
            else:
                os.mkdir(parent_dir)
            self.GetmdDetail(md)
        self.post_num = len(self.arr)
        #排序
        if self.post_num >=2:
            for i in range(1, self.post_num):#这里不需要-1，因为下面已经有j = i-1，否则在列表最后一个排不到
                key = self.arr[i] 
                j = i-1 
                while j>=0 and key.date.replace("-", "").replace(":", "").replace(" ", "") > self.arr[j].date.replace("-", "").replace(":", "").replace(" ", ""):
                    self.arr[j+1] = self.arr[j]
                    j-=1
                self.arr[j+1] = key
        
        self.sitemap() #生成sitemap.txt文件
        
        #置顶
        topArr = []
        top = self.post_num-1
        while top>=0:
            if(self.arr[top].topping.replace(" ", "") == "Yes"):
                topArr.insert(0,self.arr[top])    #插入到列表topArr中
                del (self.arr[top])               #删除列表arr中该元素
            top -= 1    
        self.arr = topArr + self.arr              #两个列表合并
        del topArr                                #删除列表topArr
        #self.PrintArr()
        
        postsnum = 0 #能显示的有多少
        for i in range(self.post_num):
            if self.arr[i].is_archive == "Yes":
                postsnum += 1
        
        self.pages = (postsnum//(self.articleMax+1)) + 1
        print('博客导航有%s页，每页有%s篇文章（含隐藏页），总共有%s篇文章。'%(self.pages,self.articleMax, self.post_num))
        if(self.pages == 2):
            self.is_only2page = True      #判断一开始就是不是只有两个页面
        return True                    #正常运行时，返回True
   
    def Main(self):
        if(self.preFunc()): 
            lr = self.post_num 
            if lr>=20:        
                import threading  
                p1 = threading.Thread( target=self.parse_main, args=( thread_str(0, lr//4),'t1') )
                p2 = threading.Thread( target=self.parse_main, args=( thread_str(lr//4, lr//2),'t2') )
                p3 = threading.Thread( target=self.parse_main, args=( thread_str(lr//2, 3*lr//4),'t3') ) 
                p4 = threading.Thread( target=self.parse_main, args=( thread_str(3*lr//4, lr),'t4') )
                p1.start()
                p2.start()
                p3.start()
                p4.start()
                p1.join()  
                p2.join()
                p3.join()
                p4.join()
            elif lr > 0:
                for j in range(lr): 
                    self.parse_to_HTML(j, "没使用线程")
            else:
                return None
            for i in range(lr-1,-1, -1):  #倒序删除符合条件的元素
                if self.arr[i].is_archive != "Yes":
                    del ( self.arr[i] )
            self.post_num = len(self.arr)
            self.Create_archive()
            
if __name__ == '__main__':
    start = time.time()
    print('欢迎使用基于python的静态博客生成器，\n项目地址：https://github.com/qing2zijin/staticblog \n现在开始生成页面了。\n')
    site_name = '月牙博客'
    a = md2html("source", site_name, "http://blog.jtjiang.top") #创建对象
    a.Main()  #调用对象内的函数
    del a
    end = time.time()
    print('程序总用时：%s秒'%(end-start))    

"""
        Introduce  template 
--------------------------------------------
file: archive_tem.html   archive template
---------------------------------------------
file: post_tem.html    post template
---------------------------------------------
file: archlink_Detail.html :

archive_post: 

archive_post:

page_nav_l:

page_nav_r:

"""
