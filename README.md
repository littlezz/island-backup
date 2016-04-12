Island Backup
=============
![author](https://img.shields.io/badge/Author-littlezz-blue.svg)
![py version](https://img.shields.io/pypi/pyversions/island-backup.svg)
![pypi status](https://img.shields.io/pypi/v/island-backup.svg)
[![license](https://img.shields.io/github/license/mashape/apistatus.svg?maxAge=2592000)]()

以 `aiohttp` `asyncio` 为主编写的备份程序  

备份匿名版上的串, 图片到本地, 以html形式查看  


特性
---
- 支持A岛 (http://h.nimingban.com/)
- 支持kukuku (http://kukuku.cc/)
- 自动备份图片
- 并发下载  
- 使用aiohttp而非多线程

安装
---
###windows用户  
可以下载编译好的二进制包  

https://github.com/littlezz/island-backup/releases



###clone  

需要python >= 3.5  
依赖库请查看requirements.txt  

下载程序  
`git clone https://github.com/littlezz/island-backup`  

安装依赖
`pip(3) install -r requirements.txt`


###pip   

使用`pip` 安装   

    pip(3) install island-backup
    
之后可以使用 `island_backup` 指令


使用方法
------

###windows
windows 用户运行island_backup.exe 文件.
输入 url , 目前兹瓷 h.nimingban.com 和 kukuku.cc 的串  

```shell
Please Input Url: http://h.nimingban.com/t/6048436?r=6048436
```  

内容在backup文件夹里面.  

###Mac && Linux
推荐使用 pip 安装, 之后可以使用`island_backup`, 会在当前目录下生成backup文件夹.  

`island_backup http://h.nimingban.com/t/6048436?r=6048436`  

使用`island_backup --help` 查看所有支持的指令  


```shell

⇒  island_backup --help                    
Usage: island_backup [OPTIONS] [URL]

Options:
  -url TEXT
  --debug                     enable debug mode
  --force-update              force update image
  --conn-count INTEGER RANGE  conn number connector use. from 1 to 20.
  --version                   Show the version and exit.
  --help                      Show this message and exit.
 
```

![](/screenshot/shell.png)



Screenshot
----------
![](/screenshot/html-preview.png)


