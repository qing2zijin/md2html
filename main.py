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
        
class Node:  #用于存放数据的结点，搭配数组使用
    def __init__(self, title=None, date=None, tags=None, md_url=None,topping=None, kwds=None, descri=None):
        self.title = title              #标题
        self.date = date                #创建时间
        self.tags = tags                #标签
        self.md_url = md_url            #makdown文章地址
        self.topping = topping          #置顶
        self.keywords = kwds            #文章关键词 
        self.description = descri       #文章摘要

class md2html(object):
    pages = 0                            #页数
    articleMax = 20                      #设置每页文章数
    post_num = 0                         #文章数量
    is_only2page = False                 #总共只有2页判断
    template_post = None                 #文章模板
    template_acrchive = None             #archive页模板                 
    archlink_Detail = None               #archive页文章链接处细节模板
    page_nav_l = None                    #各个pages里面prev next按钮
    page_nav_r = None    
    def __init__(self, base, site_name):
        self.base = base
        self.site_name = site_name
        self.arr = []
    def findAllFile(self):
        for root, ds, fs in os.walk(self.base):
            for f in fs:
                yield os.path.join(root,f)
 
    def GetmdDetail(self, full_Raw_URL):    
        if full_Raw_URL is not None: #传递的不是空地址
            with open(full_Raw_URL, 'r', encoding='utf-8') as raw_File:
                raw_Data = raw_File.read()
            pattern_title = 'title:(.*?)\n'       #文章标题
            pattern_date = 'date:(.*?)\n'         #文章日期
            pattern_tags = 'tags:(.*?)\n'         #文章标签
            pattern_private = 'priv:(.*?)\n'      #文章是否保密,保密文章不收录到目录中。
            pattern_topping = 'top:(.*?)\n'       #文章是否置顶
            pattern_keywords = 'keywords:(.*?)\n'  #文章关键词
            pattern_description = 'description:(.*?)\n' #文章摘要
            
            try:  #尝试读取标题
              ti = re.compile(pattern_title, re.S).findall(raw_Data)
              title = ti[0].replace(" ", "")
            except:
              title = '无标题'
              
            try:  #尝试读取日期
              da = re.compile(pattern_date, re.S).findall(raw_Data)
              date = da[0]
            except:
              date = '1997-01-01 19:12:00'
              
            try:  #尝试读取标签
              tg = re.compile(pattern_tags, re.S).findall(raw_Data)
              tags = tg[0].replace(" ", "").replace("[", "").replace("]", "")
            except:
              tags = 'life'
              
            try:  #尝试读取关键词
              kwds = re.compile(pattern_keywords, re.S).findall(raw_Data)
              keywords = kwds[0].replace(" ", "")
            except:
              keywords = title + ',' + self.site_name

            try:  #尝试读取内容摘要
              descri = re.compile(pattern_description, re.S).findall(raw_Data)
              description = descri[0].replace(" ", "")
            except:
              description = title
            
            try:  #尝试读取是否置顶
              top = re.compile(pattern_topping, re.S).findall(raw_Data)
              topping = top[0].replace(" ", "")
            except:
              topping = 'No'

            try:  #尝试读取是否保密
              pri = re.compile(pattern_private, re.S).findall(raw_Data)
              private = pri[0]
            except:
              private = "No"
              
            if(private.replace(" ", "") == "No"):
                self.arr.append(Node(title, date, tags, full_Raw_URL, topping, keywords, description))
            else:
                print("文章：《%s》保密，不生成HTML %s"%(title, full_Raw_URL) ) 
            #title, date, tags, full_Raw_URL, topping, kwds, description
        else:
            return None
            
    def PrintArr(self):
        for n in self.arr:
            print("《%s》，写于：%s"%(n.title, n.date))
        print('\n')

    def HTML_url(self, md_Rurl):
        return ( '%s.html'%(os.path.basename(md_Rurl).lower().replace('.md', '')) )
        
    def parse_to_HTML(self, listNumber, str):
        prev_article = None  # 时间距离最远的文章为 上一篇 列表序号最大处方向
        next_article = None  # 时间距离最近的文章为 下一篇 列表序号为0处方向
        if(0 == listNumber):
            next_article = "下一篇：没有了"
        else:
            next_article = '下一篇：<a href="'+self.HTML_url(self.arr[listNumber-1].md_url)+'">'+self.arr[listNumber-1].title+'</a>' #<a href="{{next_article}}">下一篇</a>
        
        if(self.post_num-1 == listNumber):
            prev_article = "上一篇：没有了"
        else:
            prev_article = '上一篇：<a href="'+self.HTML_url(self.arr[listNumber+1].md_url)+'">'+self.arr[listNumber+1].title+'</a>' #<a href="{{prev_article}}">上一篇</a>
        
        with open(self.arr[listNumber].md_url, 'r', encoding='utf-8') as raw_File:
            raw_Data = raw_File.read()        
        
        out_path = 'posts/'+self.HTML_url(self.arr[listNumber].md_url)  #输出地址及HTML文件名称结构
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
        # print('使用线程%s生成文章：《%s》,其标签为：%s'%(str, self.arr[listNumber].title, self.arr[listNumber].tags))
        
    def parse_main(self, thread_str, str):    #线程调用函数
        first = thread_str.first
        last = thread_str.last
        for i in range(first,last):
            self.parse_to_HTML(i, str)             

    def preFunc(self):  #预先处理
        '''预先判定这几个文件夹是否存在： source  posts  pages   template   '''
        if os.path.isdir(self.base) and os.path.isdir("posts") and os.path.isdir("pages") and os.path.isdir("template"):
            '''判断这几个模板文件是否存在'''
            if os.path.isfile('template/post_tem.html') and os.path.isfile('template/archive_tem.html') and os.path.isfile('template/archlink_Detail.html'):
                with open('template/post_tem.html','r',encoding='utf-8') as aa:
                    self.template_post = aa.read()
                with open('template/archive_tem.html','r',encoding='utf-8') as bb:
                    self.template_acrchive= bb.read()
                with open('template/archlink_Detail.html','r',encoding='utf-8') as cc:
                    archlink_Detail_data = cc.read()
                self.archlink_Detail = re.compile('archive_post:(.*?)\n', re.S).findall(archlink_Detail_data)
                self.page_nav_l = re.compile('page_nav_l:(.*?)\n', re.S).findall(archlink_Detail_data) 
                self.page_nav_r = re.compile('page_nav_r:(.*?)\n', re.S).findall(archlink_Detail_data)
            else:
                print("模板文件夹里面欠缺必要的文件！")
                return False
               
            for md in self.findAllFile():
                self.GetmdDetail(md)          
            self.post_num = len(self.arr)
        
            if self.post_num >=2:
                #排序
                for i in range(1, self.post_num):#这里不需要-1，因为下面已经有j = i-1，否则在-数组最后一个排不到
                    key = self.arr[i] 
                    j = i-1 
                    while j>=0 and key.date.replace("-", "").replace(":", "").replace(" ", "") > self.arr[j].date.replace("-", "").replace(":", "").replace(" ", ""):
                        self.arr[j+1] = self.arr[j]
                        j-=1
                    self.arr[j+1] = key
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
                # self.PrintArr()
        
            self.pages = (self.post_num//(self.articleMax+1)) + 1
            print('博客导航有%s页，每页有%s篇文章（含隐藏页），总共有%s篇文章。'%(self.pages,self.articleMax, self.post_num))
            if(self.pages == 2):
                self.is_only2page = True      #判断一开始就是不是只有两个页面
            return True                    #正常运行时，返回True
        else:
            print("请仔细检查source、posts、pages、template这三个文件夹是否存在！")
            return False

    def create_catalog(self):
        print('生成目录中')
        temp = self.archlink_Detail[0]
        temp_first = self.archlink_Detail[1]
        page_nav_l = self.page_nav_l[0]
        page_nav_r = self.page_nav_r[0]
        
        if (self.post_num <= self.articleMax): #只有一页 a
            print("a")
            s1 = ''
            for i in range(0, self.post_num):   
                a = temp_first.replace('{{date}}',self.arr[i].date.replace(" ", "")[0:10])\
                .replace('{{md_url}}',self.HTML_url(self.arr[i].md_url))\
                .replace('{{post_name}}',self.arr[i].title)               
                s1 =  s1+a
                
            with open('index.html','w',encoding='utf-8') as only_onepg:
                only_onepg.write(self.template_acrchive.replace('{{page_nav}}',s1)\
                .replace('{{title}}',self.site_name)\
                .replace('{{site-name}}',self.site_name)\
                .replace('{{nav}}',''))                 

        elif(self.pages == 1): #第一页没有pre b
            print("b")
            s1 = ''
            for i in range(0, self.articleMax):    
                a = temp_first.replace('{{date}}',self.arr[i].date.replace(" ", "")[0:10])\
                .replace('{{md_url}}',self.HTML_url(self.arr[i].md_url))\
                .replace('{{post_name}}',self.arr[i].title)       
                s1 =  s1+a
            with open('index.html','w',encoding='utf-8') as pg:
                pg.write(self.template_acrchive\
                .replace('{{page_nav}}',s1)\
                .replace('{{title}}',self.site_name)\
                .replace('{{site-name}}',self.site_name)\
                .replace('{{nav}}',page_nav_r.replace('{{right-link}}','pages/'+str(self.pages+1)+'.html')))
        elif(self.pages == 2 and (self.is_only2page != True) ): #由递归衰减而到的第2页 c
            print("c")
            s1 = ''
            for i in range(self.articleMax, self.pages*self.articleMax):   
                a = temp.replace('{{date}}',self.arr[i].date.replace(" ", "")[0:10])\
                .replace('{{md_url}}',self.HTML_url(self.arr[i].md_url))\
                .replace('{{post_name}}',self.arr[i].title)       
                s1 =  s1+a
            with open('pages/'+str(self.pages)+'.html','w',encoding='utf-8') as pg:
                pg.write(self.template_acrchive\
                .replace('{{page_nav}}',s1)\
                .replace('{{title}}','第'+str(self.pages)+'页 | '+ self.site_name)\
                .replace('{{site-name}}',self.site_name)\
                .replace('{{nav}}', page_nav_l.replace('{{left-link}}','../index.html')+page_nav_r.replace('{{right-link}}',str(self.pages+1)+'.html')))
                
        elif(self.is_only2page): #如果一开始就是只有2页便执行如下代码 d
            print("d")
            s1 = ''
            for i in range(self.articleMax, self.post_num):   
                a = temp.replace('{{date}}',self.arr[i].date.replace(" ", "")[0:10])\
                .replace('{{md_url}}',self.HTML_url(self.arr[i].md_url))\
                .replace('{{post_name}}',self.arr[i].title)       
                s1 =  s1+a
                
            with open('pages/'+str(self.pages)+'.html','w',encoding='utf-8') as pg:
                pg.write(self.template_acrchive\
                .replace('{{page_nav}}',s1)\
                .replace('{{title}}','第'+str(self.pages)+'页 | '+ self.site_name)\
                .replace('{{site-name}}',self.site_name)\
                .replace('{{nav}}', page_nav_l.replace('{{left-link}}','../index.html')))

        elif(self.pages*self.articleMax >= self.post_num and ((self.pages-1)*self.articleMax <= self.post_num ) ): #最后一页 e
            print("e")
            s1 = '' 
            for i in range((self.pages-1)*self.articleMax, self.post_num):
                a = temp.replace('{{date}}',self.arr[i].date.replace(" ", "")[0:10])\
                .replace('{{md_url}}',self.HTML_url(self.arr[i].md_url))\
                .replace('{{post_name}}',self.arr[i].title)       
                s1 =  s1+a
                
            with open('pages/'+str(self.pages)+'.html','w',encoding='utf-8') as pg:
                pg.write(self.template_acrchive\
                .replace('{{page_nav}}',s1)\
                .replace('{{title}}','第'+str(self.pages)+'页 | '+ self.site_name)\
                .replace('{{site-name}}',self.site_name)\
                .replace('{{nav}}', page_nav_l.replace('{{left-link}}',str(self.pages-1)+'.html')))
        else:  #一般页面 f
            print("f")
            s1 = ''
            for i in range((self.pages-1)*self.articleMax, (self.pages-1)*self.articleMax+self.articleMax):
                a = temp.replace('{{date}}',self.arr[i].date.replace(" ", "")[0:10])\
                .replace('{{md_url}}',self.HTML_url(self.arr[i].md_url))\
                .replace('{{post_name}}',self.arr[i].title)       
                s1 =  s1+a          
            with open('pages/'+str(self.pages)+'.html','w',encoding='utf-8') as pg:
                pg.write(self.template_acrchive\
                .replace('{{page_nav}}',s1)\
                .replace('{{title}}','第'+str(self.pages)+'页 | '+ self.site_name)\
                .replace('{{site-name}}',self.site_name)\
                .replace('{{nav}}', page_nav_l.replace('{{left-link}}',str(self.pages-1)+'.html')+page_nav_r.replace('{{right-link}}',\
                str(self.pages+1)+'.html')))
        self.pages -=1
        if self.pages >0:
            self.create_catalog()

    
    def Main(self):
        if(self.preFunc()):
            lr = self.post_num                       
            if lr>=20:        
                import threading  
                p1 = threading.Thread( target=self.parse_main, args=( thread_str(0, lr//4),'t1') )
                p2 = threading.Thread( target=self.parse_main, args=( thread_str(lr//4, lr//2),'t2') )
                p3 = threading.Thread( target=self.parse_main, args=(thread_str(lr//2, 3*lr//4),'t3') ) 
                p4 = threading.Thread( target=self.parse_main, args=(thread_str(3*lr//4, lr),'t4') )
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
                    self.parse_to_HTML(j, "没用线程")
            else:
                return None
            self.create_catalog()
        
if __name__ == '__main__':
    start = time.time()
    print('欢迎使用基于python的静态博客生成器\n现在开始生成页面了。\n')
    site_name = '月牙博客'
    a = md2html('source/', site_name) #创建对象
    a.Main()  #调用对象内的函数
    del a
    end = time.time()
    print('程序总用时：%s秒'%(end-start))    
