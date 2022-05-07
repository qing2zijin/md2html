# staticblog
基于markdown和python的静态博客（网站）生成器

## 前言
版权归@qing2zijin所有，请勿擅自商业化。

## 所需的文件及文件夹
`main.py`：程序

`source` ：将需要的markdown文件存放于此处

`posts` ：程序自动将转换好的html文件存放于此处

`template`：网页模板，目前有导航页和文章页模板

## 所需用到的库

1. `markdown` `pip install markdown`
2. `os`
3. `re`
4. `threading`
5. `time`

## 使用方法
```
python main.py
```


## 文章样式&文件格式
所有文章样式是：
```
<!--
title:标题
date:时间
tags:标签
keywords:关键词
description:文章摘要
priv:是否保密
top:是否置顶
-->
内容
```
post-contents

保存为`.md`格式
