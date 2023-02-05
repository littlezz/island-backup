Island Backup
=============
![author](https://img.shields.io/badge/Author-littlezz-blue.svg)
![py version](https://img.shields.io/pypi/pyversions/island-backup.svg)
![pypi status](https://img.shields.io/pypi/v/island-backup.svg)
[![license](https://img.shields.io/github/license/mashape/apistatus.svg?maxAge=2592000)]()

以 `aiohttp` `asyncio` 为主编写的备份程序  

备份匿名版上的串, 图片到本地, 以html形式查看  


![](/screenshot/shell.gif)


特性
---
- 支持A岛 (https://www.nmbxd1.com/)
- 支持4chan (http://www.4chan.org/)
- 2chan (http://www.2chan.net/)
- <del>支持kukuku (http://kukuku.cc/)</del>
- <del>支持备胎岛 (http://h.adnmb.com/Forum)</del>
- 自动备份图片
- 并发下载  
- 使用aiohttp而非多线程

安装
---
###windows用户  
可以下载编译好的二进制包  

https://github.com/littlezz/island-backup/releases



###clone  

需要python >= 3.11 
依赖库请查看requirements.txt  

下载程序  
`git clone https://github.com/littlezz/island-backup`  

安装依赖
`pip(3) install -r requirements.txt`4


###pip   

使用`pip` 安装   

    pip(3) install island-backup
    
之后可以使用 `island_backup` 指令


使用方法
------

###windows
windows 用户运行island_backup.exe 文件.
输入 url ,  

```shell
Please Input Url: https://www.nmbxd1.com/t/52752005?r=52752005
```  

内容在backup文件夹里面.  

###Mac && Linux
推荐使用 pip 安装, 之后可以使用`island_backup`, 会在当前目录下生成backup文件夹.  

`island_backup https://www.nmbxd1.com/t/52752005?r=52752005`  

使用`island_backup --help` 查看所有支持的指令  


```shell

⇒  island_backup --help                                                                                                                             (env: island_backup) 
Usage: island_backup [OPTIONS] [URL]

Options:
  -url TEXT
  --debug                     enable debug mode
  --force-update              force update image
  --conn-count INTEGER RANGE  max conn number connector use. from 1 to 20.
                              Default is no limit
  -p, --proxy TEXT            socks proxy address, ex, 127.0.0.1:1080
  --version                   Show the version and exit.
  --help                      Show this message and exit.
 
```

###配置文件

另外支持使用名字为"island_backup.json"的文件保存配置， 程序在启动时默认搜索当前目录，和`~/.island_backup`。  

比如一个配置文件  

```json
{
  "conn-count": "10",
  "debug": true,
  "proxy": "127.0.0.1:1080"
}
```



![](/screenshot/shell.jpg)



Screenshot
----------
![](/screenshot/html-preview.jpg)


Changelog
---------
- v1.5 分离了备份文件中的css和js；现在可以使用配置文件了。
- v1.4 修复nimingban, kukuku, 增加单元测试, 分离了类结构。  
- v1.3 支持备胎岛 2016-09-02