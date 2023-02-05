"""
 希望坚持，微语像日记，记叙自己的琐碎，日子久了，记叙多了，也成了一笔宝贵的时间财富 -- 2022.9.20
"""

import re, os

OUT_DIR = "../_public/t"

def File_toData(file): #读取文件，返回结果
    if os.path.isfile(file):
        with open(file, "r", encoding="utf-8") as f:
            data = f.read()
        f.close()
        return data
    else:
        print("文件{}不存在！".format(file))
        return
    
def html_re(data, pattern):  
    if data == None:
        return
    item = re.compile(pattern).findall(data)
    return item               #返回列表
 
def t_maincontent(first_id, last_id, list_date, list_text):
    s = ""
    if len(list_date) == 0:
        return s
    
    for m in range(first_id, last_id):
        sll = '\n\t\t<div><i>{0}</i><br>{1}</div>'.format(list_date[m], list_text[m])
        s = s + sll
    return s

def create_tt(site_namel, pages, temp_data, is_only2page, Max, list_date, list_text):
    global OUT_DIR 
    if pages <= 0:
        return None
    length = len(list_date)
    nav_prev = None
    nav_next = None
    main_content = None
    if length <= Max: #只有一页
        print("1.只有一页")
        nav_prev = ""
        nav_next = ""
        main_content = t_maincontent(0, length, list_date, list_text)
    elif pages == 1:     #衰减为第一页
        print("2.衰减为第一页")
        nav_prev = ""
        nav_next = '<a href="pages/{}.html">Next</a>'.format( str(pages+1) )
        main_content = t_maincontent(0, Max, list_date, list_text)
    elif pages == 2 and is_only2page == False: #缩减为第二页
        print("3.缩减为第二页")
        nav_prev = '<a href="../index.html">Prev</a> '
        nav_next = '<a href="{}.html">Next</a>'.format( str(pages+1) )
        main_content = t_maincontent( (pages-1)*Max, pages*Max, list_date, list_text)
    elif is_only2page:
        print("4.刚开始就为2页") 
        nav_prev = '<a href="../index.html">Prev</a> '
        nav_next = ""
        main_content = t_maincontent(Max, length, list_date, list_text)
    elif (pages*Max >= length) and (pages-1)*Max <= length: #最后一页
        print("5.最后一页")
        nav_prev = '<a href="{}.html">Prev</a> '.format( str(pages-1) )
        nav_next = ""
        main_content = t_maincontent( (pages-1)*Max, length, list_date, list_text)
    else:
        print("6.一般页面")
        nav_prev = '<a href="{}.html">Prev</a> '.format( str(pages-1) )
        nav_next = '<a href="{}.html">Next</a>'.format( str(pages+1) )
        main_content = t_maincontent( (pages-1)*Max, pages*Max, list_date, list_text)
        
    if pages == 1:
        s_top = '最新发布时间：{}，合计发布{}条。'.format( str(list_date[0]), str(length) )
    else:
        s_top = ""
    html_data = temp_data.replace("{{site-name}}",site_namel)\
                         .replace("{{t_content}}", main_content)\
                         .replace("{{nav_prev}}", nav_prev)\
                         .replace("{{nav_next}}", nav_next)\
                         .replace("{{_top}}", s_top)
    
    """输出"""
    outPath = None
    if pages == 1:
        outPath = "{}/index.html".format(OUT_DIR)
    else:
        outPath = "{}/pages/{}.html".format(OUT_DIR, pages )
    with open(outPath, "w", encoding="utf-8") as tt:
        tt.write(html_data)
    
    pages -= 1
    create_tt(site_namel, pages, temp_data, is_only2page, Max, list_date, list_text)
    return
    
def main(site_namel,source_file,file_temphtml,everyPage_Max):
    global OUT_DIR
    """读取txt文件源数据"""
    if os.path.isdir("source") == False:
        print("source源文件夹不存在，请创建！程序终止，该行代码为第102行")
        return
    
    #以后记录多了，source_file文件变大了，又该如何？2022.11.12
    DATA = File_toData(source_file) 
    
    """从txt文件中分拣出需要的数据"""
    pattern_date = '[0-9]{4}-[0-9]*-[0-9]*'
    
    pattern_content = '\n[^#](.*。)' #pattern_content = '\n[^#](.*。)|(.*！)'  
    t_date = html_re(DATA, pattern_date) #关于时间的列表
    t_content = html_re(DATA, pattern_content) #关于内容的列表
    
    """读取模板文件"""
    #file_temphtml 模板文件
     
    if os.path.isfile(file_temphtml) == False: #模板文件
        print("无模板文件template_t.html，请先创建！该行代码为第117行")
        return
    temp_data = File_toData(file_temphtml)
    
    length = len(t_date)
    
    
    if os.path.isdir( "{}/pages".format( OUT_DIR) )  == False:
        os.mkdir( "{}/pages".format( OUT_DIR) )
    
    """每页输出数量，自定"""
    #everyPage_Max
    
    pages = length//everyPage_Max
    if pages*everyPage_Max < length:
        pages += 1
    is_only2page = None
    if pages == 2:
        is_only2page = True
    else:
        is_only2page = False
    create_tt(site_namel, pages, temp_data, is_only2page, everyPage_Max, t_date, t_content)
    
    
    
    
if __name__ == "__main__":
    
    source = "source/t.txt"
    template = "../template/NEW/template_t.html" #模板文件
    site_name = ""
    pageMax = 90
    
    main(site_name,source,template,pageMax)
    
 #90条分页   
