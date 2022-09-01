"""
*设计说明
*使用列表存储md文件细节信息
*排序等操作整理列表
*编排导航页面也使用排序后的列表
"""

import os, re, threading, markdown

"""判断文件夹存在并创建"""
def isDIR(DIR):
    if ( False == os.path.isdir(DIR) ):
        os.mkdir(DIR)
        
"""判断文件存在并创建"""
def isFILE(FILE):
    if os.path.isfile(FILE):
        return True
    else:
        return False

class thread_str(object):
    def __init__(self,first, last):
        self.first = first
        self.last = last
        # print("该段区间为[%s , %s)" %(self.first, self.last))

"""用于存放数据的结点，搭配列表使用"""
class Node:  
    def __init__(self, title=None, date=None, tags=None, md_url=None,topping=None, is_archive=None,use_markdownmodule=None,kwds=None, descri=None):
        self.title = title                             #标题
        self.date = date                               #创建时间
        self.tags = tags                               #标签
        self.md_url = md_url                           #makdown文章地址
        self.topping = topping                         #置顶
        self.is_archive = is_archive                   #archive页收录
        self.use_markdownmodule = use_markdownmodule   #启用markdown库
        self.keywords = kwds                           #文章关键词 
        self.description = descri                      #文章摘要

class md2html(object):
    dir_public = None
    dir_posts = None
    dir_pages = None
    pages = 0                            #页数
    articleMax = 40                      #设置每页文章数，默认值40
    post_num = 0                         #文章数量
    is_only2page = False                 #总共只有2页判断
    template_post = None                 #文章模板
    template_acrchive = None             #archive页模板                 
    archlink_Detail = None               #archive页文章链接处细节模板
    page_nav_l = None                    #各个pages里面prev next按钮
    page_nav_r = None    
    menu = None                          #菜单设置
    pattern = ["title:(.*?)\n", "date:(.*?)\n", "tags:(.*?)\n", "priv:(.*?)\n", "top:(.*?)\n", \
              "is_archive:(.*?)\n", "use_markdownmodule:(.*?)\n", "keywords:(.*?)\n", "description:(.*?)\n" ] 
    tagg = [ "无标题", "1997-01-01 19:12:00", "life", "No", "No", "Yes", "Yes", "", "" ]
    md_rawlist = list()                      #原始Md文件地址存储    
    thread_str1 = None
    thread_str2 = None
    thread_str3 = None
    thread_str4 = None
    
    def __init__(self, base, site_name, site_UL, max_article=None, output_ALL=None, output_DETAIL=None, output_PAGE=None):
        md2html.dir_public = output_ALL
        md2html.dir_posts = output_DETAIL
        md2html.dir_pages = output_PAGE
        
        self.base = base
        self.site_name = site_name
        self.site_url = site_UL
        self.arr = list()
        if max_article != None:
            md2html.articleMax = max_article
    
    def __del__(self):
        print("程序结束, Good bye !")

    def findALLFile(self):
        for root, ds, fs in os.walk(self.base):
            for f in fs:
                md_l = os.path.join(root, f) 
                """source\gongkao_zhaunlan => _public\posts\gongkao_zhuanlan"""
                parent_dir = os.path.dirname(md_l).replace( self.base, "{}\{}".format(self.dir_public, self.dir_posts) )
                isDIR( parent_dir )
                self.md_rawlist.append(md_l)
    
    """根据原始文件地址读取文件，得出需要的细节信息"""
    def GetmdDetail(self, addrid):    
        md_addr = self.md_rawlist[addrid]
        if md_addr != None: #传递的不是空地址
            try:
                with open(md_addr, 'r', encoding='utf-8') as raw_File:
                    raw_Data = raw_File.read()
            except:
                print("文件地址不对！")
                return None
            """              说明：采取的是列表之间对比，列表needthing作为匹配结果，列表tagg作为设置的原始值，"""
            
            needthing = list() #title 0, date 1, tags 2, private 3, topping 4, is_archive 5, use_markdownmodule 6, keywords 7, description 8
            
            length = len(self.pattern)
            
            for k in range(length):
                # needthi = re.compile(self.pattern[k]).findall(raw_Data[0:400])  #返回列表
                # if len(needthi) == 0:
                    # needthing.append(self.tagg[k])
                # else:
                    # needthing.append(needthi[0])
            # if needthing[7].replace(" ", "") == "":
                # needthing[7] = needthing[0] + "," + self.site_name
            # if needthing[8].replace(" ", "") == "":
                # needthing[8] = needthing[0]
            
                matchaddr = re.search(self.pattern[k], raw_Data[:400])  #循环匹配
                if matchaddr is not None:           #排查：如果md文件里面没有设置参数
                    needthing.append(matchaddr.group(1))                    
                else:
                    needthing.append(self.tagg[k])
            for m in range(length):
                if needthing[m].replace(" ", "") == "":       #排查：如果md文件里面设置了参数但是没值
                    if m == 7:
                        needthing[m] = needthing[0] + "," + self.site_name   #keywords
                    elif m == 8:
                        needthing[m] = needthing[0]             #description
                    else:
                        needthing[m] = self.tagg[m] 

            # print(needthing[0] + needthing[6])
            if(needthing[3] == "No"):
                """这里有点多此一举，不过这个程序以前的版本：元素最开始不是存储在列表needthing里面的。
                而现在为了节省代码量就使用了列表needthing，其实是可以直接插入列表的，形成二维列表，不过后面的形式要更改，
                偷懒就这样了。"""
         
                self.arr.append(Node(needthing[0], needthing[1], needthing[2], md_addr, needthing[4], needthing[5], needthing[6], needthing[7], needthing[8]))
            else:
                print("文章：《%s》保密%s，不生成HTML，地址为：%s\n"%(needthing[0], needthing[3], md_addr) ) 
            del needthing
            return True
        else:
            return False
    
    def HTML_url(self, md_addr, parse_to_HTML=None):
        if parse_to_HTML == True:
            a = "{}\\".format(self.base)
            return md_addr.replace(a, "/{}/".format(self.dir_posts) ).replace(".md", ".html")
        else:
            return md_addr.replace(self.base, self.dir_posts).replace("\\", "/").replace(".md", ".html")
    
    """转为HTML"""
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

        out_path = self.HTML_url('{}/{}'.format(self.dir_public, self.arr[listNumber].md_url) )  #输出地址及HTML文件名称结构
        if self.arr[listNumber].use_markdownmodule == "Yes":
            html_content = markdown.markdown( raw_Data, extensions=['markdown.extensions.toc', 'markdown.extensions.tables', 'markdown.extensions.fenced_code',  'markdown.extensions.meta'] )
        else:
            html_content = raw_Data
        post_html_content = self.template_post.replace('{{title}}', self.arr[listNumber].title)\
            .replace('{{site-name}}',self.site_name)\
            .replace('{{date}}', self.arr[listNumber].date)\
            .replace('{{post-content}}', html_content)\
            .replace('{{tags}}', self.arr[listNumber].tags)\
            .replace('{{prev_article}}',prev_article)\
            .replace('{{next_article}}',next_article)\
            .replace('{{keywords}}', self.arr[listNumber].keywords)\
            .replace('{{description}}',self.arr[listNumber].description)\
            .replace("{{menu}}", self.menu)
        
        with open(out_path, 'w', encoding='utf-8', errors='xmlcharrefreplace') as out_File:
            out_File.write(post_html_content)
        print('使用线程%s生成文章：《%s》,其标签为：%s，地址在：%s'%(str, self.arr[listNumber].title, self.arr[listNumber].tags, out_path))
    
    """生成目录"""
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
            posts_url = "{}/index.html".format(self.dir_public)
            with open(posts_url,'w',encoding='utf-8') as only_onepg:
                only_onepg.write(self.template_acrchive.replace('{{page_nav}}',s1)\
                .replace('{{title}}',self.site_name)\
                .replace('{{site-name}}',self.site_name)\
                .replace('{{nav}}','') \
                .replace("{{menu}}", self.menu) \
                )                 
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
            posts_url = "{}/index.html".format(self.dir_public)
            with open(posts_url,'w',encoding='utf-8') as pg:
                pg.write(self.template_acrchive\
                .replace('{{page_nav}}',s1)\
                .replace('{{title}}',self.site_name)\
                .replace('{{site-name}}',self.site_name)\
                .replace('{{nav}}',page_nav_r.replace('{{right-link}}','{}/'.format(self.dir_pages) + str(self.pages+1)+'.html'))\
                .replace("{{menu}}", self.menu) \
                )
            self.sitemap(posts_url)
        elif(self.pages == 2 and (self.is_only2page == False) ): #由递归衰减而到的第2页 c
            print("c")
            s1 = ''
            for i in range(self.articleMax, self.pages*self.articleMax):   
                if self.arr[i].is_archive == "Yes":
                    a = temp.replace('{{date}}',self.arr[i].date.replace(" ", "")[0:10])\
                    .replace('{{md_url}}',self.HTML_url(self.arr[i].md_url))\
                    .replace('{{post_name}}',self.arr[i].title)       
                    s1 =  s1+a
            posts_url = "{}/{}/".format(self.dir_public, self.dir_pages) + str(self.pages)+".html"
            with open(posts_url,'w',encoding='utf-8') as pg:
                pg.write(self.template_acrchive\
                .replace('{{page_nav}}',s1)\
                .replace('{{title}}','第'+str(self.pages)+'页 | '+ self.site_name)\
                .replace('{{site-name}}',self.site_name)\
                .replace('{{nav}}', page_nav_l.replace('{{left-link}}','../index.html')+page_nav_r.replace('{{right-link}}',str(self.pages+1)+'.html'))\
                .replace("{{menu}}", self.menu) \
                )
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
            posts_url = "{}/{}/".format(self.dir_public, self.dir_pages) + str(self.pages)+".html"
            with open(posts_url,'w',encoding='utf-8') as pg:
                pg.write(self.template_acrchive\
                .replace('{{page_nav}}',s1)\
                .replace('{{title}}','第'+str(self.pages)+'页 | '+ self.site_name)\
                .replace('{{site-name}}',self.site_name)\
                .replace('{{nav}}', page_nav_l.replace('{{left-link}}','../index.html'))\
                .replace("{{menu}}", self.menu) \
                )
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
            posts_url = "{}/{}/".format(self.dir_public, self.dir_pages) + str(self.pages)+".html"
            with open(posts_url,'w',encoding='utf-8') as pg:
                pg.write(self.template_acrchive\
                .replace('{{page_nav}}',s1)\
                .replace('{{title}}','第'+str(self.pages)+'页 | '+ self.site_name)\
                .replace('{{site-name}}',self.site_name)\
                .replace('{{nav}}', page_nav_l.replace('{{left-link}}',str(self.pages-1)+'.html'))\
                .replace("{{menu}}", self.menu) \
                )
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
            posts_url = "{}/{}/".format(self.dir_public, self.dir_pages) + str(self.pages)+".html"
            with open(posts_url,'w',encoding='utf-8') as pg:
                pg.write(self.template_acrchive\
                .replace('{{page_nav}}',s1)\
                .replace('{{title}}','第'+str(self.pages)+'页 | '+ self.site_name)\
                .replace('{{site-name}}',self.site_name)\
                .replace('{{nav}}', page_nav_l.replace('{{left-link}}',str(self.pages-1)+'.html')+page_nav_r.replace('{{right-link}}',\
                str(self.pages+1)+'.html'))\
                .replace("{{menu}}", self.menu) \
                )
            self.sitemap(posts_url)
        self.pages -=1
        if self.pages >0:
            self.Create_archive()
      
    """生成站点地图sitemap"""
    def sitemap(self, URL=None): 
        if URL == None:
            sitemapstring = ""
            for i in self.arr:
                sitemapstring = sitemapstring + self.site_url +"/"+self.HTML_url(i.md_url) + "\n"
            try:
                with open("{}/sitemap.txt".format(self.dir_public), "w",encoding="utf-8") as sitemap:
                    sitemap.write(sitemapstring)
                sitemap.close()
            except:
                return False
        else:
            try:
                with open("{}/sitemap.txt".format(self.dir_public), "a",encoding="utf-8") as sitemap:
                    sitemap.write(self.site_url +URL.replace("{}".format(self.dir_public),"") + "\n")
                sitemap.close()
            except:
                return False
        return True
    
    """线程调用函数"""
    def parse_main(self, thread_str, str):
        first = thread_str.first
        last = thread_str.last
        if str == "PreGetmdDetail":
            for i in range(first, last):
                self.GetmdDetail(i)
        else:
            for i in range(first, last):
                if i < 2:
                    self.parse_to_HTML(i, str)
                elif os.path.isfile( "{}/{}".format(self.dir_public, self.HTML_url(self.arr[i].md_url) ) ):
                    continue
                else:    
                    self.parse_to_HTML(i, str)
    
    """按长度确定节点可控制的长度，以此创建节点"""
    def CreatNode(self, length):
        self.thread_str1 = thread_str(0, length//4)
        self.thread_str2 = thread_str(length//4, length//2)
        self.thread_str3 = thread_str(length//2, 3*length//4)
        self.thread_str4 = thread_str(3*length//4, length)
        print("四个结点已创建") 
    
    """"主函数 调度用"""
    def Main(self):
        isDIR("template")
        if ( isFILE("template/post_tem.html") and isFILE("template/archive_tem.html") and isFILE("template/subtle_set.html") ):
            with open("template/post_tem.html", "r", encoding="utf-8") as aa:
                self.template_post = aa.read()
            with open("template/archive_tem.html", "r", encoding="utf-8") as bb:
                self.template_acrchive = bb.read()
            with open("template/subtle_set.html","r", encoding="utf-8") as cc:
                archlink_Detail_data = cc.read()
            self.archlink_Detail = re.compile("archive_post:(.*?)\n", re.S).findall(archlink_Detail_data)   
            self.page_nav_l = re.search('page_nav_l:(.*?)\n', archlink_Detail_data, re.S).group(1)
            self.page_nav_r = re.search('page_nav_r:(.*?)\n', archlink_Detail_data, re.S).group(1)
            self.menu = re.search("menu:(.*?)\n", archlink_Detail_data, re.S).group(1)
        else:
            print("模板文件夹里面欠缺必要的文件！\n 请参考：https://github.com/qing2zijin/staticblog 进行搭建")
            return False
        
        """多线程读取文件，得到文件的细节"""
        self.findALLFile()
        len_md = len( self.md_rawlist )
        
        """创建4个对象"""
        self.CreatNode(len_md)
        
        """使用线程读取md文件细节"""
        if len_md >= 20:
            p1 = threading.Thread( target=self.parse_main, args=( self.thread_str1, "PreGetmdDetail") )
            p2 = threading.Thread( target=self.parse_main, args=( self.thread_str2, "PreGetmdDetail") )
            p3 = threading.Thread( target=self.parse_main, args=( self.thread_str3, "PreGetmdDetail") )
            p4 = threading.Thread( target=self.parse_main, args=( self.thread_str4, "PreGetmdDetail") )
            p1.start()
            p2.start()
            p3.start()
            p4.start()
            p1.join()
            p2.join()
            p3.join()
            p4.join()
        else:
            for k in range(len_md):
                self.GetmdDetail(k)
                
        md2html.post_num = len(self.arr)
        if self.post_num == 0:
            return False
        
        """排序"""
        if self.post_num >=2:
            for i in range(1, self.post_num):#这里不需要-1，因为下面已经有j = i-1，否则在列表最后一个排不到
                key = self.arr[i] 
                j = i-1 
                while j>=0 and key.date.replace("-", "").replace(":", "").replace(" ", "") > self.arr[j].date.replace("-", "").replace(":", "").replace(" ", ""):
                    self.arr[j+1] = self.arr[j]
                    j-=1
                self.arr[j+1] = key
        #self.PrintArr()
        self.sitemap() #生成sitemap.txt文件
        
        #置顶
        topArr = []
        top = self.post_num - 1
        while top>=0:
            if(self.arr[top].topping.replace(" ", "") == "Yes"):
                topArr.insert(0,self.arr[top])    #插入到列表topArr中
                del (self.arr[top])               #删除列表arr中该元素
            top -= 1    
        self.arr = topArr + self.arr              #两个列表合并
        del topArr                                #删除列表topArr
       
        postsnum = 0 #能显示的有多少
        for i in range(self.post_num):
            if self.arr[i].is_archive == "Yes":
                postsnum += 1
        self.pages = int( postsnum/(self.articleMax) )  #向下取整
        if (self.pages * self.articleMax) < postsnum:
            self.pages += 1
        print('博客导航有%s页，每页有%s篇文章（%s篇非archive显示），合计%s篇文章。'%(self.pages,self.articleMax, self.post_num-postsnum, self.post_num))
        if(self.pages == 2):
            self.is_only2page = True      #判断一开始就是不是只有两个页面
        
                
        if self.post_num == len_md:
            pass
        else:
            self.CreatNode(self.post_num)
        if self.post_num>=20: 
            p5 = threading.Thread( target=self.parse_main, args=( self.thread_str1,'t5') )
            p6 = threading.Thread( target=self.parse_main, args=( self.thread_str2,'t6') )
            p7 = threading.Thread( target=self.parse_main, args=( self.thread_str3,'t7') ) 
            p8 = threading.Thread( target=self.parse_main, args=( self.thread_str4,'t8') )
            p5.start()
            p6.start()
            p7.start()
            p8.start()
            p5.join()  
            p6.join()
            p7.join()
            p8.join()
        else:
            for j in range(self.post_num): 
                self.parse_to_HTML(j, "没使用线程")            
        
        for i in range(self.post_num-1,-1, -1):  #倒序删除符合条件的元素
            if self.arr[i].is_archive != "Yes":
                del ( self.arr[i] )
        self.post_num = len(self.arr)                    
        
        #生成目录
        self.Create_archive()
        
        return True        
            
if __name__ == "__main__":
    
    source = "source"    #文章源
 
    output_ALL = "_public"  #输出地址总文件夹
    output_DETAIL = "posts"   #输出地址具体的文件夹 _public/posts
    output_PAGE = "pages"    #输出地址分页文件夹 _public/pages
    
    isDIR(output_ALL)
    
    outfilePATH = "{}/{}".format(output_ALL, output_DETAIL)
    isDIR(outfilePATH)
    
    outfilePAGE = "{}/{}".format(output_ALL, output_PAGE)
    isDIR(outfilePAGE) 
    """-----------------------------------------------------------------------------------"""
    
    site_name = "月牙博客"   #博客名称
    site_url = "http://blog.jtjiang.top"  #博客网址
    page_MaxNum = 20      #页面显示最大数量
    
    a = md2html(source, site_name, site_url, page_MaxNum, output_ALL, output_DETAIL, output_PAGE)
    a.Main()
    del a
    