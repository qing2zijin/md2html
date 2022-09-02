模板页面

下面是几个核心关键词 keywords

## archive_tem.html

`{{page_nav}}`：使用模板文件`subtle_set.html`中`archive_post:`后面的片段循环读取列表生成。

 `{{nav}} `：上下页面链接
 
 ## post_tem.html
 
 `{{post-content}}`：文章主要内容，此处是靠`markdown`库生成
 
 `{{prev_article}}`：上一页面链接
 
 `{{next_article}}`：下一页面链接
 
 ## public tags
 
 `{{title}}`：标题
 
 `{{site-name}}`：站点名称
 
 `{{date}}`：创建日期
 
 `{{tags}}`：标签
 
 `{{menu}}`: 菜单 使用模板文件`subtle_set.html`中的`menu:`后面的片段
