模板页面

下面是几个核心关键词 keywords

## NEW/page.html

`{{page_nav}}`：使用模板文件`subtle_set.html`中`archive_post:`后面的片段循环读取列表生成。

 `{{nav}} `：上下页面链接
 
 ## NEW/post.html
 
 `{{post-content}}`：文章主要内容，此处是靠`markdown`库生成
 
 `{{prev_article}}`：上一页面链接
 
 `{{next_article}}`：下一页面链接
 
 ## subtle_set.html
 
 ```
 <!-- page.html -->
 archive_post:<p>{{date}}&nbsp;<a href="../{{md_url}}">{{post_name}}</a></p>
 archive_post:<p>{{date}}&nbsp;<a href="{{md_url}}">{{post_name}}</a></p>
 <!-- 导航按钮 -->
 page_nav_l:<a href="{{left-link}}"><span style="float:left">Prev</span></a>
 page_nav_r:<a href="{{right-link}}"><span style="float:right">Next</span></a>
 ```
 
 出现两个`archive_post`的原因是：前一个模板的首页是包含了文章链接的，在新版本中，链接的位置发生了更改。
 
 
 ## public keywords
 
 `{{site_url}}`: 网址
 
 `{{title}}`：标题
 
 `{{site-name}}`：站点名称
 
 `{{date}}`：创建日期
 
 `{{category}}`：标签
 
 <del>`{{menu}}`: 菜单 使用模板文件`subtle_set.html`中的`menu:`后面的片段</del>，目前已经弃用该做法，使用jquery外挂链接
