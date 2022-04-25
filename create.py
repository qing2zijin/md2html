'''
数据结构：列表+对象结点
方式：采取先读取，后生成的方式。
具体步骤：
        1.读取source目录下文件
        2.文件细节插入到数据结构中
        3.排序
        4.使用线程，分段生成网页
        5.生成目录，并结束
'''
import os, markdown, re, threading, time

class thread_str(object):
    def __init__(self,first, last):
        self.first = first
        self.last = last
        print("采取分段分块进行网页的生成，该段区间为[%s , %s)" %(self.first, self.last))
        
class Node:  #用于存放数据的结点，搭配数组使用
    def __init__(self, title=None, date=None, tags=None, topping=None, md_url=None):
        self.title = title              #标题
        self.date = date                #创建时间
        self.tags = tags                #标签
        self.topping = topping          #是否置顶
        self.md_url = md_url            #makdown文章地址

class md2html(object):
    pages = 0
    articleMax = 15                      #设置每页文章数
    post_num = 0
    is_only2page = False                 #总共只有2页判断
    template_post = ''
    template_nav = ''    
    def __init__(self, base, site_name):
        self.base = base
        self.site_name = site_name
        self.arr = []
    def findAllFile(self):
        for root, ds, fs in os.walk(self.base):
            for f in fs:
                yield os.path.join(root,f)
 
    def GetmdDetail(self, full_Raw_URL):    #os.path.join(root,f)
        with open(full_Raw_URL, 'r', encoding='utf-8') as raw_File:
            raw_Data = raw_File.read()
        pattern_title = 'title:(.*?)\n'       #文章标题
        pattern_date = 'date:(.*?)\n'         #文章日期
        pattern_tags = 'tags:(.*?)\n'         #文章标签
        pattern_private = 'priv:(.*?)\n'      #文章是否保密,保密文章不收录到目录中。
        pattern_topping = 'top:(.*?)\n'       #文章是否置顶
        
        try:  #尝试读取标题
          ti = re.compile(pattern_title, re.S).findall(raw_Data)
          title = ti[0]
        except:
          title = '无标题'
          
        try:  #尝试读取日期
          da = re.compile(pattern_date, re.S).findall(raw_Data)
          date = da[0]
        except:
          date = '1997-01-01 19:12:00'
          
        try:  #尝试读取标签
          tg = re.compile(pattern_tags, re.S).findall(raw_Data)
          tags = tg[0]
        except:
          tags = 'life'
        
        try:  #尝试读取是否置顶
          top = re.compile(pattern_topping, re.S).findall(raw_Data)
          topping = top[0]
        except:
          topping = 'No'
        
        if(topping.replace(" ", "") == "Yes"):
            title = "【置顶】" + title
        
        try:  #尝试读取是否保密
          pri = re.compile(pattern_private, re.S).findall(raw_Data)
          private = pri[0]
        except:
          private = "No"
        if(private.replace(" ", "") == "No"):
            self.arr.append(Node(title, date, tags,topping, full_Raw_URL))
        else:
            print("文章：《%s》保密，不生成HTML"%title) 
    #title, date, tags,topping, full_Raw_URL

    def PrintArr(self):
        for n in self.arr:
            print("标题：%s，是否置顶：%s，创建时间：%s"%(n.title, n.topping, n.date))
        print('\n\n')

    def HTML_url(self, md_Rurl):
        return ( '%s.html'%(os.path.basename(md_Rurl).lower().replace('.md', '')) )
        
    def parse_to_HTML(self, FF, str):
        prev_article = ""  # 时间距离最远的文章为 上一篇 列表序号最大处
        next_article = ""  # 时间距离最近的文章为 下一篇 列表序号为0处
        if(FF == 0):
            next_article = ""
        else:
            next_article = '下一篇：<a href="'+self.HTML_url(self.arr[FF-1].md_url)+'">'+self.arr[FF-1].title+'</a>' #<a href="{{next_article}}">下一篇</a>
        
        if(FF == self.post_num-1):
            prev_article = ""
        else:
            prev_article = '上一篇：<a href="'+self.HTML_url(self.arr[FF+1].md_url)+'">'+self.arr[FF+1].title+'</a>' #<a href="{{prev_article}}">上一篇</a>
        
        with open(self.arr[FF].md_url, 'r', encoding='utf-8') as raw_File:
            raw_Data = raw_File.read()        
        
        out_path = 'posts/'+self.HTML_url(self.arr[FF].md_url)  #输出地址及HTML文件名称结构
        
        html_content = markdown.markdown(raw_Data,extensions=['markdown.extensions.toc','markdown.extensions.tables']).replace('<<', '&lt;&lt;').replace('>>', '&gt;&gt;')#特定转换，针对C++
        
        
        post_html_content = self.template_post.replace('{{title}}', self.arr[FF].title)\
        .replace('{{site-name}}',self.site_name)\
        .replace('{{date}}', self.arr[FF].date)\
        .replace('{{post-content}}', html_content)\
        .replace('{{tags}}', self.arr[FF].tags)\
        .replace('{{prev_article}}',prev_article)\
        .replace('{{next_article}}',next_article)\
        
        with open(out_path, 'w', encoding='utf-8', errors='xmlcharrefreplace') as out_File:
            out_File.write(post_html_content)
        print('使用线程%s生成文章：《%s》,其标签为：%s，是否置顶%s'%(str, self.arr[FF].title, self.arr[FF].tags, self.arr[FF].topping))
        
    def parse_main(self, thread_str, str):    #线程调用函数
        first = thread_str.first
        last = thread_str.last
        for i in range(first,last):
            self.parse_to_HTML(i, str)             

    def preFunc(self):  #预先处理
        #读取模板存到内存中
        with open('template/post_tem.html','r',encoding='utf-8') as aa:
            self.template_post = aa.read()
        with open('template/home_tem.html','r',encoding='utf-8') as bb:
            self.template_nav= bb.read()
            
        for x in self.findAllFile():
            self.GetmdDetail(x)          
        self.post_num = len(self.arr)
        
        #排序
        for i in range(1, self.post_num):#这里不需要-1，因为下面已经有j = i-1，否则在-数组最后一个排不到
            key = self.arr[i] 
            j = i-1 
            while j>=0 and key.date.replace("-", "").replace(":", "").replace(" ", "") > self.arr[j].date.replace("-", "").replace(":", "").replace(" ", ""):
                self.arr[j+1] = self.arr[j]
                j-=1
            self.arr[j+1] = key
        # self.PrintArr()
        '''
        #置顶 错误示例
        for k in range(self.post_num-1, 0, -1):
            if(self.arr[k].topping.replace(" ", "") == "Yes"):
                self.arr[k].title = "[置顶] "+self.arr[k].title
                temp = self.arr[k]
                n = k
                while n>0:
                    self.arr[n] = self.arr[n-1]
                    n-=1
                self.arr[n] = temp
        self.PrintArr()
        '''
        
        #置顶 正确示例
        topArr = []
        # Max = self.post_num
        top = self.post_num-1
        while top>=0:
            if(self.arr[top].topping.replace(" ", "") == "Yes"):
                topArr.insert(0,self.arr[top])    #插入到列表topArr中
                del (self.arr[top])               #删除列表arr中该元素
            top -= 1    
        self.arr = topArr + self.arr              #两个列表合并
        del topArr                                #删除列表topArr
        self.PrintArr()
        
        self.pages = (self.post_num//(self.articleMax+1)) + 1
        print('博客导航有%s页，每页有%s篇文章（含隐藏页）。'%(self.pages,self.articleMax))
        if(self.pages == 2):
            self.is_only2page = True #判断一开始就是不是只有两个页面
            
    def Main(self):
        self.preFunc()
        '''加入线程'''
               
        lr = self.post_num  
        if lr>=3:        
            p1 = threading.Thread( target=self.parse_main, args=( thread_str(0, lr//3),'t1') )
            p2 = threading.Thread( target=self.parse_main, args=( thread_str(lr//3, 2*lr//3),'t2') )
            p3 = threading.Thread( target=self.parse_main, args=(thread_str(2*lr//3, lr),'t3') ) 
            p1.start()
            p2.start()
            p3.start()
            
            p1.join()  
            p2.join()
            p3.join()          
               
        else:
            try:
                for j in range(lr): 
                    self.parse_to_docHTML(j, "没用线程")
            except:
                print("空目录")        
        
    def create_catalog(self):
        print('生成目录中')
        temp = '''<div class="archive-post">
                  <span class="archive-post-time">{{date}}</span>
                  <span class="archive-post-title">
                   <a href="/posts/{{md_url}}" class="archive-post-link">{{post_name}}</a>
                  </span>
                 </div>'''
        temp_id_l = '''<a class="prev" href="{{left-link}}"><span class="prev-text">Prev</span></a>'''
        temp_id_r = '''<a class="next" href="{{right-link}}"><span class="next-text">Next</span></a>'''
        
        if (self.post_num <= self.articleMax): #只有一页
            s1 = ''
            for i in range(0, self.post_num):   
                a = temp.replace('{{date}}',self.arr[i].date.replace(" ", "")[0:10])\
                .replace('{{md_url}}',self.HTML_url(self.arr[i].md_url))\
                .replace('{{post_name}}',self.arr[i].title)               
                s1 =  s1+a
                
            with open('index.html','w',encoding='utf-8') as only_onepg:
                only_onepg.write(self.template_nav.replace('{{page_nav}}',s1)\
                .replace('{{title}}',self.site_name)\
                .replace('{{site-name}}',self.site_name)\
                .replace('{{nav}}',''))                 

        elif(self.pages == 1): #第一页没有pre
            s1 = ''
            for i in range(0, self.articleMax):    
                a = temp.replace('{{date}}',self.arr[i].date.replace(" ", "")[0:10])\
                .replace('{{md_url}}',self.HTML_url(self.arr[i].md_url))\
                .replace('{{post_name}}',self.arr[i].title)       
                s1 =  s1+a
                
            with open('index.html','w',encoding='utf-8') as pg:
                pg.write(self.template_nav\
                .replace('{{page_nav}}',s1)\
                .replace('{{title}}',self.site_name)\
                .replace('{{site-name}}',self.site_name)\
                .replace('{{nav}}',temp_id_r.replace('{{right-link}}','pages/'+str(self.pages+1)+'.html')))
        elif(self.pages == 2 and (self.is_only2page != True) ): #由递归衰减而到的第2页
            s1 = ''
            for i in range(self.articleMax, self.pages*self.articleMax):   
                a = temp.replace('{{date}}',self.arr[i].date.replace(" ", "")[0:10])\
                .replace('{{md_url}}',self.HTML_url(self.arr[i].md_url))\
                .replace('{{post_name}}',self.arr[i].title)       
                s1 =  s1+a
                
            with open('pages/'+str(self.pages)+'.html','w',encoding='utf-8') as pg:
                pg.write(self.template_nav\
                .replace('{{page_nav}}',s1)\
                .replace('{{title}}','第'+str(self.pages)+'页 | '+ self.site_name)\
                .replace('{{site-name}}',self.site_name)\
                .replace('{{nav}}', temp_id_l.replace('{{left-link}}','/')+temp_id_r.replace('{{right-link}}',str(self.pages+1)+'.html')))
                
        elif(self.is_only2page): #如果一开始就是只有2页便执行如下代码
            s1 = ''
            for i in range(self.articleMax, self.post_num):   
                a = temp.replace('{{date}}',self.arr[i].date.replace(" ", "")[0:10])\
                .replace('{{md_url}}',self.HTML_url(self.arr[i].md_url))\
                .replace('{{post_name}}',self.arr[i].title)       
                s1 =  s1+a
                
            with open('pages/'+str(self.pages)+'.html','w',encoding='utf-8') as pg:
                pg.write(self.template_nav\
                .replace('{{page_nav}}',s1)\
                .replace('{{title}}','第'+str(self.pages)+'页 | '+ self.site_name)\
                .replace('{{site-name}}',self.site_name)\
                .replace('{{nav}}', temp_id_l.replace('{{left-link}}','/')))

        elif((self.pages+1)*self.articleMax>=self.post_num and (self.pages*self.articleMax<=self.post_num ) ): #最后一页
            s1 = '' 
            for i in range((self.pages-1)*self.articleMax, self.post_num):
                a = temp.replace('{{date}}',self.arr[i].date.replace(" ", "")[0:10])\
                .replace('{{md_url}}',self.HTML_url(self.arr[i].md_url))\
                .replace('{{post_name}}',self.arr[i].title)       
                s1 =  s1+a
                
            with open('pages/'+str(self.pages)+'.html','w',encoding='utf-8') as pg:
                pg.write(self.template_nav\
                .replace('{{page_nav}}',s1)\
                .replace('{{title}}','第'+str(self.pages)+'页 | '+ self.site_name)\
                .replace('{{site-name}}',self.site_name)\
                .replace('{{nav}}', temp_id_l.replace('{{left-link}}',str(self.pages-1)+'.html')))

        else:  #一般页面
            s1 = ''
            for i in range((self.pages-1)*self.articleMax, (self.pages-1)*self.articleMax+self.articleMax):
                
                    
                    
                a = temp.replace('{{date}}',self.arr[i].date.replace(" ", "")[0:10])\
                .replace('{{md_url}}',self.HTML_url(self.arr[i].md_url))\
                .replace('{{post_name}}',self.arr[i].title)       
                s1 =  s1+a
                
            with open('pages/'+str(self.pages)+'.html','w',encoding='utf-8') as pg:
                pg.write(self.template_nav\
                .replace('{{page_nav}}',s1)\
                .replace('{{title}}','第'+str(self.pages)+'页 | '+ self.site_name)\
                .replace('{{site-name}}',self.site_name)\
                .replace('{{nav}}', temp_id_l.replace('{{left-link}}',str(self.pages-1)+'.html')+temp_id_r.replace('{{right-link}}',\
                str(self.pages+1)+'.html')))
        self.pages -=1
        if self.pages >0:
            self.create_catalog()


if __name__ == '__main__':
    
    start = time.time()
    print('欢迎使用基于python的静态博客生成器\n现在开始生成页面了。\n')
    base = 'source/'
    site_name = '月牙博客'
    a = md2html(base, site_name) #创建对象
    a.Main()  #调用对象内的函数
    a.create_catalog()  
    del a

    end = time.time()
    print('程序总用时：%s秒'%(end-start))    