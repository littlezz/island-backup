Island Backup
=============

|Author| |Python-Version| |PyPI-Status| |LICENCE|

`Island Backup` is a utility that download threads content and images from Anonymously broad website.
The content will be saved as html file.

`Island Backup` is written by aiohttp which use `asyncio`, so only support Python3.

So far, `Island Backup` Support website below

- A岛 (https://h.nimingban.com/)
- kukuku (http://kukuku.cc/)
- 备胎岛 (http://h.adnmb.com/Forum)
- 4chan (http://www.4chan.org/)


..  code-block::
    island_backup http://boards.4chan.org/a/thread/149376017



Installation
------------

Use PyPI
~~~~~~~~
..  code:: sh
    pip3 install island-backup

For Windows User
~~~~~~~~~~~~~~~~
Download latest binary package

https://github.com/littlezz/island-backup/releases


Usage
-----

.. code:: sh

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


Using Config File
-----------------
Create a json file named `island_backup.json`, write you config in it.
Program will search on current path or `~/.island_backup/`

For windows user, you should create file in program main folder.

For example, a  `island_backup.json` could be

.. code:: json

    {
      "conn-count": "10",
      "debug": true,
      "proxy": "127.0.0.1:1080"
    }


ScreenShot
----------
|ScreenShot-1|



..  |Author| image:: https://img.shields.io/badge/Author-littlezz-blue.svg
    :target: https://github.com/littlezz
..  |Python-Version| image:: https://img.shields.io/pypi/pyversions/island-backup.svg
..  |PyPI-Status| image:: https://img.shields.io/pypi/v/island-backup.svg
    :target: https://pypi.python.org/pypi/island-backup
..  |LICENCE| image:: https://img.shields.io/github/license/mashape/apistatus.svg?maxAge=2592000)
    :target: https://github.com/littlezz/island-backup/blob/master/LICENSE
..  |ScreenShot-1| image:: https://github.com/littlezz/island-backup/blob/master/screenshot/html-preview.png

