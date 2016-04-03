Island Backup
==============
以 `aiohttp` `asyncio` 为主编写的备份程序  

备份匿名版上的串, 图片到本地, 以html形式查看  


特性
-----
- 支持A岛 (http://h.nimingban.com/)
- 支持kukuku (http://kukuku.cc/)
- 自动备份图片
- 并发下载  
- 使用aiohttp而非多线程


使用方法
-------
需要python >= 3.5  
依赖库请查看requirements.txt  


`python3 main.py`  

输入 url , 目前兹瓷 h.nimingban.com 和 kukuku.cc 的串  

```shell
url
http://h.nimingban.com/t/6048436?r=6048436
```


内容在backup文件夹里面.  


Screenshot
--------
![](/screenshot/html-preview.png)

