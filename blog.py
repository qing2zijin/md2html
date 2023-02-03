"""
*****blog.by
*设计说明
*使用列表存储md文件细节信息
*排序等操作整理列表
*编排导航页面也使用排序后的列表
********************************************使用多线程！************************************
"""

"""
2023.2.1程序更新，换模板
1.post_tem.html => post.html     [模板文件]
2.archive_tem.html => page.html  [模板文件]
    原首页移到pages目录下。对Create_archive()函数进行了较大幅度修改
    对temp_first 和 temp 值进行了统一，原来首页成了pages目录下面的一个子文件，链接路径也就进行了修改。
3.subtle_set.html未改变。
4.删除了atom.xml文件生成程序，不太使用。
"""


import os, re, markdown, time, threading

"""判断文件夹存在并创建"""
def isDIR(DIR):
    if ( False == os.path.isdir(DIR) ):
        os.mkdir(DIR)
        
"""判断文件存在"""
def isFILE(FILE):
    if os.path.isfile(FILE):
        return True
    else:
        return False

def File_io(_file, Mode, code, DATA=None):
    with open(_file, Mode, encoding=code) as file:
        if Mode == "r":
            return file.read()  #read  就返回数据
        else:
            file.write(DATA)    #write 操作
    file.close()

"""存储区段信息的结点   其实吧，也可以使用元组来替代tup(a, b)"""
class thread_str(object):
    def __init__(self,first, last):
        self.first = first
        self.last = last

"""用于存放数据的结点，搭配列表使用"""
class Node(object):  
    def __init__(self, title=None, date=None, category=None, md_url=None,topping=None, is_archive=None,use_markdownmodule=None,kwds=None, descri=None):
        self.title = title                             #标题
        self.date = date                               #创建时间
        self.category = category                       #类别
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
    dir_extra = None
    pages = 0                            #页数
    articleMax = 30                      #设置每页文章数，默认值30
    post_num = 0                         #文章数量
    is_only2page = False                 #一开始只有两页的判断
    template_post = None                 #文章模板
    template_acrchive = None             #archive页模板                 
    archlink_Detail = None               #archive页文章链接处细节模板
    page_nav_l = None                    #各个pages里面prev next按钮
    page_nav_r = None    
    #menu = None                         #菜单设置
    md_rawlist = list()                  #原始Md文件地址存储    
    thread_srtarr = list()               #线程存储列表
     
    def __init__(self, base, site_name, site_UL, max_article=None, output_ALL=None, output_DETAIL=None, output_PAGE=None, output_RECENTPOSTS=None):
        md2html.dir_public = output_ALL
        md2html.dir_posts = output_DETAIL
        md2html.dir_pages = output_PAGE
        md2html.dir_extra = output_RECENTPOSTS
        self.base = base
        self.site_name = site_name
        self.site_url = site_UL
        self.arr = list()          #列表，按照读取文件顺序存储文档信息，建立一种索引关系。
        if max_article != None:
            md2html.articleMax = max_article
    
    def __del__(self):
        print("程序结束, Good bye !")

    """遍历source源文件，寻址，插入列表中"""
    def findALLFile(self):
        for root, ds, fs in os.walk(self.base):
            for f in fs:
                md_l = os.path.join(root, f) 
                parent_dir = os.path.dirname(md_l).replace(self.base, "{}/{}".format(self.dir_public, self.dir_posts) )
                isDIR( parent_dir )
                md2html.md_rawlist.append(md_l)
               
    """根据原始文件地址读取文件，得出需要的细节信息"""
    def GetmdDetail(self, addrid):    
        md_addr = self.md_rawlist[addrid]
        if md_addr != None: #传递的不是空地址
            try:
                raw_Data = File_io(md_addr, "r", "utf-8")
            except:
                print("文件地址不对！")
                return None
            title = None
            date = None
            category = None
            private = None
            top = None
            is_archive = None
            use_markdownmodule = None
            keywords = None
            description = None
            
            DATA = raw_Data[:400]
            title_p = re.search("title:(.*?)\n", DATA)
            date_p = re.search("date:(.*?)\n", DATA)
            category_p = re.search("category:(.*?)\n", DATA)
            private_p = re.search("priv:(.*?)\n", DATA)
            top_p = re.search("top:(.*?)\n", DATA)
            is_archive_p = re.search("is_archive:(.*?)\n", DATA)
            use_markdownmodule_p = re.search("use_markdownmodule:(.*?)\n", DATA)
            keywords_p = re.search("keywords:(.*?)\n", DATA)
            description_p = re.search("description:(.*?)\n", DATA)
            
            """title"""
            if title_p != None: #设置了该属性
                title = title_p.group(1).replace(" ", "")
            else:
                title = "无标题"
            if title == "":
                title = "无标题"
            """date"""
            if date_p != None:
                date = date_p.group(1)
            else:
                date = "1997-01-01 19:12:00"
            if date == "":
                date = "1997-01-01 19:12:00"
            """category"""
            if category_p != None:
                category = category_p.group(1).replace(" ", "")
            else:
                category = "life"
            if category == "":
                category = "life"
            """private"""
            if private_p != None:
                private = private_p.group(1).replace(" ", "")
            else:
                private = "No"
            if private == "":
                private = "No"
            """top"""
            if top_p != None:
                top = top_p.group(1).replace(" ", "")
            else:
                top = "No"
            if top == "":
                top = "No"
            """is_archive"""
            if is_archive_p != None:
                is_archive = is_archive_p.group(1).replace(" ", "")
            else:
                is_archive = "Yes"
            if is_archive == "":
                is_archive = "Yes"
            """use_markdownmodule"""
            if use_markdownmodule_p != None:
                use_markdownmodule = use_markdownmodule_p.group(1)
            else:
                use_markdownmodule = "Yes"
            if use_markdownmodule == "":
                use_markdownmodule = "Yes"
            """keywords"""
            if keywords_p != None:
                keywords = keywords_p.group(1).replace(" ", "")
            else:
                keywords = "{},{},{}".format(title, self.site_name,category)
            if keywords == "":
                keywords = "{},{},{}".format(title, self.site_name,category)
            """description"""
            if description_p != None:
                description = description_p.group(1).replace(" ", "")
            else:
                description = "{}:{}".format(self.site_name, title)
            if description == "":
                description = "{}:{}".format(self.site_name, title)
            
            
            if( private != "Yes"):
                self.arr.append(Node( title, date, category, md_addr, top, is_archive, use_markdownmodule, keywords, description ))
            else:
                print("文章：《%s》保密%s，不生成HTML，地址为：%s\n"%(title, private, md_addr) ) 
            
            return True
        else:
            return False
            
    """通过md文件地址得到html文件地址"""
    def HTML_url(self, md_addr, parse_to_HTML=None):
        if parse_to_HTML == True:
            a = "{}/".format(self.base) #source\   #linux系统为"/"  windows系统为"\"
            return md_addr.replace(a, "/{}/".format(self.dir_posts) ).replace(".md", ".html") # source\...md => /posts/...html
        else:
            return md_addr.replace(self.base, self.dir_posts).replace("\\", "/").replace(".md", ".html") # source/...md => posts/...html
    
    """转为HTML"""
    def parse_to_HTML(self, listNumber, str):
        out_path = self.HTML_url('{}/{}'.format(self.dir_public, self.arr[listNumber].md_url) )  #输出地址及HTML文件名称结构
                
        """判断需要的网页是否存在，存在就不输出，并且要排除前3篇文章。"""
        if os.path.isfile( out_path ) and listNumber >=3:
            return None
            
        raw_Data = File_io(self.arr[listNumber].md_url, "r", "utf-8")            
 
        if self.arr[listNumber].use_markdownmodule == "Yes":
            html_content = markdown.markdown( raw_Data, extensions=["markdown.extensions.toc", "markdown.extensions.tables", "markdown.extensions.fenced_code",  "markdown.extensions.meta"] )
        else:
            html_content = raw_Data
               
        prev_article = None  # 时间距离最远的文章为 上一篇 列表序号最大处方向
        next_article = None  # 时间距离最近的文章为 下一篇 列表序号为0处方向
        
        """通过标签is_archive判断是否应当编排页内的上下页导航，通过下面的操作以其达到半隐藏的目的"""
        if "No" == self.arr[listNumber].is_archive:
            prev_article = ""
            next_article = ""
        else:
            if(0 == listNumber):
                next_article = "下一篇：没有了"
            else:
                n = listNumber-1
                while ( ("No" == self.arr[n].is_archive) and ( n > 0) ): 
                    n -= 1
                if -1 == n:
                    next_article = "下一篇：没有了"
                else:
                    """<a href="{{next_article}}">下一篇</a>"""
                    next_article = '下一篇：<a href="'+self.HTML_url(self.arr[n].md_url, True)+'">'+self.arr[n].title+'</a>' 
                
            if(self.post_num-1 == listNumber):
                prev_article = "上一篇：没有了"
            else:
                m = listNumber +1
                while ( ("No"==self.arr[m].is_archive) and ( m < (self.post_num-1) ) ):
                    m += 1
                if self.post_num == m:
                    prev_article = "上一篇：没有了"
                else:
                    """<a href="{{prev_article}}">上一篇</a>"""
                    prev_article = '上一篇：<a href="'+self.HTML_url(self.arr[m].md_url, True)+'">'+self.arr[m].title+'</a>' 
        
        post_html_content = self.template_post.replace('{{title}}', self.arr[listNumber].title)\
            .replace('{{site-name}}',self.site_name)\
            .replace('{{date}}', self.arr[listNumber].date)\
            .replace('{{post-content}}', html_content)\
            .replace('{{category}}', self.arr[listNumber].category)\
            .replace('{{prev_article}}',prev_article)\
            .replace('{{next_article}}',next_article)\
            .replace('{{keywords}}', self.arr[listNumber].keywords)\
            .replace('{{description}}',self.arr[listNumber].description)
            #.replace("{{menu}}", self.menu)
        File_io(out_path, "w", "utf-8", DATA=post_html_content)
        print('使用线程%s生成文章：《%s》,其标签为：%s，地址在：%s'%(str, self.arr[listNumber].title, self.arr[listNumber].category, out_path))
    
    """生成目录，定制的，没有办法通用"""
    def Create_archive(self):
        print('生成目录中')
        temp = self.archlink_Detail[0]
        #temp_first = self.archlink_Detail[1]
        temp_first = temp
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
                    s1 =  s1+"\n\t\t"+a
            posts_url = "{}/{}/index.html".format(self.dir_public,self.dir_pages)
            File_io(posts_url, "w", "utf-8", \
                  DATA=self.template_acrchive.replace('{{page_nav}}',s1)\
                   .replace('{{title}}',self.site_name)\
                   .replace('{{site-name}}',self.site_name)\
                   .replace('{{nav}}','') \
                   #.replace("{{menu}}", self.menu) 
                )
            self.sitemap(posts_url, Mode="a")
        elif(self.pages == 1): #第一页没有pre b
            print("b")
            s1 = ''
            for i in range(0, self.articleMax):    
                if self.arr[i].is_archive == "Yes":
                    a = temp_first.replace('{{date}}',self.arr[i].date.replace(" ", "")[0:10])\
                    .replace('{{md_url}}',self.HTML_url(self.arr[i].md_url))\
                    .replace('{{post_name}}',self.arr[i].title)       
                    s1 =  s1+"\n\t\t"+a
            posts_url = "{}/{}/index.html".format(self.dir_public,self.dir_pages)
            File_io(posts_url, "w", "utf-8",\
                DATA = self.template_acrchive.replace('{{page_nav}}',s1)\
                       .replace('{{title}}',self.site_name)\
                       .replace('{{site-name}}',self.site_name)\
                       .replace('{{nav}}',page_nav_r.replace('{{right-link}}','{}.html'.format( self.pages+1 ) ) )\
                      #.replace('{{nav}}',page_nav_r.replace('{{right-link}}','{}/{}.html'.format( self.dir_pages,str(self.pages+1) ) ) )\
                      #.replace("{{menu}}", self.menu) \
                )
            self.sitemap(posts_url,Mode="a")
        elif(self.pages == 2 and (self.is_only2page == False) ): #由递归衰减而到的第2页 c
            print("c")
            s1 = ''
            for i in range(self.articleMax, self.pages*self.articleMax):   
                if self.arr[i].is_archive == "Yes":
                    a = temp.replace('{{date}}',self.arr[i].date.replace(" ", "")[0:10])\
                    .replace('{{md_url}}',self.HTML_url(self.arr[i].md_url))\
                    .replace('{{post_name}}',self.arr[i].title)       
                    s1 =  s1+"\n\t\t"+a
            posts_url = '{}/{}/{}.html'.format(self.dir_public, self.dir_pages, self.pages)
            File_io(posts_url, "w", "utf-8", \
                DATA = self.template_acrchive.replace('{{page_nav}}',s1)\
                    .replace('{{title}}',"第{}页|{}".format(str(self.pages), self.site_name) )\
                    .replace('{{site-name}}',self.site_name)\
                    .replace('{{nav}}', page_nav_l.replace('{{left-link}}','index.html')+page_nav_r.replace('{{right-link}}',str(self.pages+1)+'.html'))\
                   #.replace("{{menu}}", self.menu) 
                )
            self.sitemap(posts_url,Mode="a")    
        elif(self.is_only2page): #如果一开始就是只有2页便执行如下代码 d
            print("d")
            s1 = ''
            for i in range(self.articleMax, self.post_num):   
                if self.arr[i].is_archive == "Yes":     
                    a = temp.replace('{{date}}',self.arr[i].date.replace(" ", "")[0:10])\
                    .replace('{{md_url}}',self.HTML_url(self.arr[i].md_url))\
                    .replace('{{post_name}}',self.arr[i].title)       
                    s1 =  s1+"\n\t\t"+a
            posts_url = '{}/{}/{}.html'.format(self.dir_public, self.dir_pages, self.pages)
            File_io(posts_url, "w", "utf-8",\
                DATA = self.template_acrchive.replace('{{page_nav}}',s1)\
                .replace('{{title}}',"第{}页|{}".format(str(self.pages), self.site_name) )\
                .replace('{{site-name}}',self.site_name)\
                .replace('{{nav}}', page_nav_l.replace('{{left-link}}','index.html'))\
                #.replace("{{menu}}", self.menu) \
                )    
            self.sitemap(posts_url, Mode="a")
        elif(self.pages*self.articleMax >= self.post_num and ((self.pages-1)*self.articleMax <= self.post_num ) ): #最后一页 e
            print("e")
            s1 = '' 
            for i in range((self.pages-1)*self.articleMax, self.post_num):
                if self.arr[i].is_archive == "Yes":
                    a = temp.replace('{{date}}',self.arr[i].date.replace(" ", "")[0:10])\
                    .replace('{{md_url}}',self.HTML_url(self.arr[i].md_url))\
                    .replace('{{post_name}}',self.arr[i].title)       
                    s1 =  s1+"\n\t\t"+a
            posts_url = '{}/{}/{}.html'.format(self.dir_public, self.dir_pages, self.pages)
            File_io(posts_url, "w", "utf-8",\
                DATA = self.template_acrchive.replace('{{page_nav}}',s1)\
                        .replace('{{title}}',"第{}页|{}".format(str(self.pages), self.site_name) )\
                        .replace('{{site-name}}',self.site_name)\
                        .replace('{{nav}}', page_nav_l.replace('{{left-link}}',str(self.pages-1)+'.html'))\
                       #.replace("{{menu}}", self.menu) \
                )
            self.sitemap(posts_url, Mode="a") 
        else:  #一般页面 f
            print("f")
            s1 = ''
            for i in range((self.pages-1)*self.articleMax, (self.pages-1)*self.articleMax+self.articleMax):
                if self.arr[i].is_archive == "Yes":
                    a = temp.replace('{{date}}',self.arr[i].date.replace(" ", "")[0:10])\
                    .replace('{{md_url}}',self.HTML_url(self.arr[i].md_url))\
                    .replace('{{post_name}}',self.arr[i].title)       
                    s1 =  s1+"\n\t\t"+a
            posts_url = '{}/{}/{}.html'.format(self.dir_public, self.dir_pages, self.pages)
            File_io(posts_url, "w", "utf-8",\
                DATA =  self.template_acrchive.replace('{{page_nav}}',s1)\
                .replace('{{title}}',"第{}页|{}".format(str(self.pages), self.site_name) )\
                .replace('{{site-name}}',self.site_name)\
                .replace('{{nav}}', page_nav_l.replace('{{left-link}}',str(self.pages-1)+'.html')+page_nav_r.replace('{{right-link}}',\
                str(self.pages+1)+'.html'))\
                #.replace("{{menu}}", self.menu) \
                )
            self.sitemap(posts_url ,Mode="a")
        self.pages -=1
        if self.pages >0:
            self.Create_archive()
      
    """生成站点地图sitemap"""
    def sitemap(self, URL=None, Mode="w"): 
        if URL == None:
            sitemapstring = ""
            for i in self.arr:
                sitemapstring = sitemapstring + self.site_url +"/"+self.HTML_url(i.md_url) + "\n"
            try:
                File_io("{}/sitemap.txt".format(self.dir_public) , Mode, "utf-8", DATA= sitemapstring)
            except:
                return False
        else:
            try:
                File_io("{}/sitemap.txt".format(self.dir_public) , Mode, "utf-8", DATA="{}{}\n".format( self.site_url, URL.replace(self.dir_public, "") )  )
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
                print("id: %s"%i)
        else:
            for i in range(first, last):  
                self.parse_to_HTML(i, str)
    
    """按长度确定节点可控制的长度，以此创建节点"""
    def CreatNode(self, length, thread_num):
        for i in range(thread_num):
            self.thread_srtarr.append( thread_str( i*length//thread_num, (i+1)*length//thread_num ) )
        print("已创建%s个结点用于存储区段信息"%thread_num)
        
    
    """最近文章"""
    def Recent_posts(self):
        out_file = "{}/{}/recent_posts.html".format(self.dir_public, self.dir_extra)  #_public/extra/recent_posts.html
        s = '<h2>Recent Posts</h2>\n<ul class="list_01">\n'
        for k in range(8):
            s1 = '\t<li><a href="/{}">{}</a></li>\n'.format(self.HTML_url( self.arr[k].md_url ) , self.arr[k].title)
            s += s1
        s += "</ul>\n"
        with open(out_file, "w", encoding="utf-8") as renc:
            renc.write(s)
        renc.close()
        
    """"主函数 调度用"""
    def Main(self, dir_template):
        temp_posts = "{}/post.html".format(dir_template)         #post_tem.html => post.html
        temp_archive = "{}/page.html".format(dir_template)       #archive_tem.html => page.html 原首页移到pages目录下。生成首页函数进行了修改。
        temp_subtle = "{}/subtle_set.html".format(dir_template)  #未变
        
        isDIR(dir_template)
        
        if ( isFILE(temp_posts) and isFILE(temp_archive) and isFILE(temp_subtle) ):
            """单页模板"""
            self.template_post = File_io(temp_posts, "r", "utf-8")
            
            """导航页模板"""
            self.template_acrchive = File_io(temp_archive, "r", "utf-8")
           
            """填充上面两个模板需要的小玩意"""
            archlink_Detail_data = File_io(temp_subtle, "r", "utf-8")
            
            self.archlink_Detail = re.compile("archive_post:(.*?)\n", re.S).findall(archlink_Detail_data)  
            self.page_nav_l = re.search('page_nav_l:(.*?)\n', archlink_Detail_data, re.S).group(1)
            self.page_nav_r = re.search('page_nav_r:(.*?)\n', archlink_Detail_data, re.S).group(1)
            """2022.9.3更新：使用jQuery load形式加载导航，舍弃之前做法。"""
            #self.menu = re.search("menu:(.*?)\n", archlink_Detail_data, re.S).group(1)
        else:
            print("模板文件夹里面欠缺必要的文件！\n 请参考：https://github.com/qing2zijin/staticblog 进行搭建")
            return False
        
        """多线程读取文件，得到文件的细节"""
        self.findALLFile()
        len_md = len( self.md_rawlist )
        
        thread_list = list()
        thread_num = 5
        
        self.CreatNode(len_md, thread_num)
        
        """使用线程读取md文件细节"""
 
        if len_md >= 40:
            for i in range(thread_num):
                thread_list.append( threading.Thread( target=self.parse_main, args=( self.thread_srtarr[i] , "PreGetmdDetail" ) ) )
            for i in range(thread_num):
                thread_list[i].start()
            
            for i in range(thread_num):
                thread_list[i].join()
        else:
            for k in range(len_md):
                self.GetmdDetail(k)

        thread_list.clear()               #清空线程列表
        self.md_rawlist.clear()
        
        md2html.post_num = len(self.arr)
        if self.post_num == 0:
            return False
        
        """直接插入排序"""
        if self.post_num >=2:
            for i in range(1, self.post_num):#这里不需要-1，因为下面已经有j = i-1，否则在列表最后一个排不到
                key = self.arr[i] 
                j = i-1 
                while j>=0 and key.date.replace("-", "").replace(":", "").replace(" ", "") > self.arr[j].date.replace("-", "").replace(":", "").replace(" ", ""):
                    self.arr[j+1] = self.arr[j]
                    j-=1
                self.arr[j+1] = key
        
        self.sitemap() #生成sitemap.txt文件
        
        """最近文章"""
        self.Recent_posts()
        
        """置顶"""
        topArr = list()
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
        print('博客导航有%s页，每页最大含%s篇文章（%s篇非archive显示），合计转换%s篇文章。'%(self.pages, self.articleMax, self.post_num-postsnum, self.post_num))
        if(self.pages == 2):
            self.is_only2page = True      #判断一开始就是不是只有两个页面
        
        
        """
        if self.post_num == len_md:
            pass
        else:
            for i in range(thread_num):
                self.thread_srtarr[i].first =  i* self.post_num//thread_num
                self.thread_srtarr[i].last = (i+1)*self.post_num//thread_num
        """
        
        """多线程渲染网页
        if self.post_num>=35: 
            for i in range(thread_num):
                thread_list.append( threading.Thread( target=self.parse_main, args=( self.thread_srtarr[i] , str(i)) ) )
            for i in range(thread_num):
                thread_list[i].start()
            for i in range(thread_num):
                thread_list[i].join()
        else:
            for j in range(self.post_num): 
                self.parse_to_HTML(j, "Main")            
        """
        
        """单线程渲染网页"""
        for j in range(self.post_num): 
            self.parse_to_HTML(j, "Main")
        
        
        for i in range(self.post_num-1,-1, -1):  #倒序删除符合条件的元素
            if self.arr[i].is_archive != "Yes":
                del ( self.arr[i] )
        self.post_num = len(self.arr)                    
        
        """生成目录"""
        self.Create_archive()
        
        """删除各个结点"""
        thread_list.clear()
        self.thread_srtarr.clear()
        self.arr.clear()
        
        return True        


    

if __name__ == "__main__":
    
    start = time.time()
    """---------------------------------------------------------------------------------"""
    source = "raw"            #文章源
    output_ALL = "_public"    #输出地址总文件夹
    output_DETAIL = "posts"   #输出地址具体的文件夹 _public/posts
    output_PAGE = "pages"     #输出地址分页文件夹 _public/pages
    output_RECENTPOSTS = "extra"
    dir_template = "template/NEW"    #模板源
    
    isDIR(output_ALL)
    
    outfilePATH = "{}/{}".format(output_ALL, output_DETAIL) #_public/posts
    isDIR(outfilePATH)
    
    outfilePAGE = "{}/{}".format(output_ALL, output_PAGE) #_public/pages
    isDIR(outfilePAGE) 
    
    outfileRECENT = "{}/{}".format(output_ALL, output_RECENTPOSTS) #_public/extra
    isDIR(outfileRECENT)
    
    """-------------------------生成站点页首-----------------------------------------------------"""
    """类别category有：life, work, study, exam, trip"""
    site_name = ""                #博客名称
    site_url = ""                 #博客网址
    page_MaxNum = 12      #页面显示最大数量
    
    md = md2html(source, site_name, site_url, page_MaxNum, output_ALL, output_DETAIL, output_PAGE, output_RECENTPOSTS)
    md.Main(dir_template)
    del md
    
    """------------------------------------------------------------------------------------"""
    print("程序总用时%s秒"%(time.time()-start) )
    
    """记录运行时间戳-----------------------------------------------------------------------"""
                   #https://zhuanlan.zhihu.com/p/45113970          
    File_io("work.log", "a", "utf-8",\
    DATA = "worklog:{}\n".format(  \
                time.strftime( '%Y.%m.%d.%H:%M:%S', time.localtime(start)   ) \
                )  \
    )  
