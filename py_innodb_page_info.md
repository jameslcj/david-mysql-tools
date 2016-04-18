**py\_innodb\_page\_info.py**

# Introduction #

a python script to get the page type from innodb tablespace, such as **.ibd, ibdata1**


# Command #

```
[root@xen-server py_innodb_page_type]# python py_innodb_page_info.py 
Usage: python py_innodb_page_info.py [OPTIONS] tablespace_file
For more options, use python py_innodb_page_info.py -h
```

for example:
```
[root@xen-server py_innodb_page_type]# python py_innodb_page_info.py item.ibd 
Total number of page: 1088:
Freshly Allocated Page: 494
Insert Buffer Bitmap: 1
File Space Header: 1
B-tree Node: 591
File Segment inode: 1
```

you can add -v to see more detail info:
```
[root@xen-server py_innodb_page_type]# python py_innodb_page_info.py -v  warehouse.ibd 
page offset 00000000, page type <File Space Header>
page offset 00000001, page type <Insert Buffer Bitmap>
page offset 00000002, page type <File Segment inode>
page offset 00000003, page type <B-tree Node>, page level <0000>
page offset 00000000, page type <Freshly Allocated Page>
page offset 00000000, page type <Freshly Allocated Page>
Total number of page: 6:
Freshly Allocated Page: 2
Insert Buffer Bitmap: 1
File Space Header: 1
B-tree Node: 1
File Segment inode: 1
```