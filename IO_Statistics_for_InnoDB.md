# Record or show SQL logical and physical reads happened in InnoDB storage engine.

# Introduction #

Record or show SQL logical and physical reads happened in InnoDB storage engine. Physical reads means page reads from disk. Logical reads means page reads in InnoDB, including page reads from buffer pool and disk. This patch adds these IO statistics into slow log and MySQL profiler. Moreover, this patch can record SQL, whose logical reads is greater than a predefined value, into slow log file.


# Example #
**slow log with logical/physical reads**
```
# Time: 111227 23:49:16
# User@Host: root[root] @ localhost [127.0.0.1]
# Query_time: 6.081214 Lock_time: 0.046800 Rows_sent: 42 Rows_examined: 727558 Logical_reads: 91584 Physical_reads: 19
use tpcc;
SET timestamp=1325000956;
SELECT orderid,customerid,employeeid,orderdate
FROM orders
WHERE orderdate IN
( SELECT MAX(orderdate)
FROM orders
GROUP BY (DATE_FORMAT(orderdate,'%Y%M'))
);
```
**IO statistics in profiler
```
mysql> set profiling=1;
Query OK, 0 rows affected (0.00 sec)

mysql> select count(1) from stock;
+----------+
| count(1) |
+----------+
| 50000000 |
+----------+
1 row in set (30.98 sec)

mysql> show profiles;
+----------+-------------+---------------+----------------+----------------------------+
| Query_ID | Duration    | Logical_reads | Physical_reads | Query                      |
+----------+-------------+---------------+----------------+----------------------------+
|        1 | 30.97979100 |       6359297 |          54673 | select count(1) from stock |
+----------+-------------+---------------+----------------+----------------------------+
1 row in set (0.00 sec)
```**

# Variables #
### slow\_query\_type ###
Type of slow query. Default: 0
  * 0: do not record SQL to slow log.
  * 1: record SQL to slow log according long\_query\_time.
  * 2: redord SQL to slow log according long\_query\_io.
  * 3: redord SQL to slow log according either long\_query\_time or long\_query\_io.
### long\_query\_io ###
Record SQL to slow log whose logical reads exceeded this value. Default: 100

# Patch #
patch: http://david-mysql-tools.googlecode.com/files/mysql-5.5.20.io_stat.patch