## **New flash cache solution is here:**<br><a href='http://code.google.com/p/david-mysql-tools/wiki/Flash_Cache_For_InnoDB'>http://code.google.com/p/david-mysql-tools/wiki/Flash_Cache_For_InnoDB</a>.<br>No plan to continue this project<b></h2></b>

Contact me if you wanna know more about this project or my support in using secondary buffer pool:<br>
Mail: jiangchengyao@gmail.com<br>
MSN: jiangchengyao@gmail.com<br>

<h1>Introduction</h1>

Enable using flash memory or solid state drive(SSD) as innodb's secondary buffer pool.<br>
This feature is much like flash cache in Oracle's Exadata<br>
<br>
After enable this feature, innodb will add a new backgound thread, when the page was removed from the innodb buffer pool, InnoDB will move it to the flash memory or ssd storage if the thread is availible. When InnoDB read a new page which is not in the buffer pool, it will read the secondary buffer pool first. If the page is cached in secondary buffer pool, it will not read the disk. Because the high random read performance of flash memory or ssd, this will boost the database performance.<br>
<br>
<h1>Sysbench OLTP benchmark</h1>
Server: Intel(R) Xeon Quad-Core E5405 2.00GHz X 2<br>
Database: ~19G ( created by sysbench, row: 80000000 )<br>
disk: 4 disk RAID 10<br>
flash storage: Intel X25-M 80G SSD<br>
test command:<br>
sysbench --test=oltp --oltp-table-size=80000000 --oltp-read-only=off --init-rng=on --num-threads=16 --max-requests=0 --oltp-dist-type=uniform --max-time=7200  --mysql-user=root   --mysql-socket=/tmp/mysql.sock --db-driver=mysql   run<br>

<table><thead><th> <b>innodb_buffer_pool</b> </th><th> <b>innodb_secondary_buffer_pool</b> </th><th>  <b>read-write(tps)</b> </th></thead><tbody>
<tr><td> 8G                        </td><td> 0G                                  </td><td> 55.03                   </td></tr>
<tr><td> 8G(sbtest on SSD)         </td><td> 0G                                  </td><td> 60.8                    </td></tr>
<tr><td> 8G                        </td><td> 30G                                 </td><td> 86.23                   </td></tr></tbody></table>



<h1>TPC-C benchmark</h1>

Server: Intel(R) Xeon Quad-Core E5405 2.00GHz X 2<br>
Database: 9G ( created by tpcc_load, 100 warehouse )<br>
disk: 4 disk RAID 10<br>
flash storage: Intel X25-M 80G SSD<br>

MySQL configuration:<br>
<pre><code>| innodb_flush_log_at_trx_commit    | 1        |<br>
| innodb_flush_method               | O_DIRECT |<br>
</code></pre>

tpcc-mysql: tpcc_start 127.0.0.1 tpcc root '123456' 10 16 1 7200<br>

<table><thead><th> <b>innodb_buffer_pool</b> </th><th> <b>innodb_secondary_buffer_pool</b> </th><th> <b>result(tpmC)</b> </th></thead><tbody>
<tr><td> 4G                        </td><td> 30G                                 </td><td> 10543.02            </td></tr>
<tr><td> 4G(tpcc on SSD)           </td><td> 0                                   </td><td> 10771.2             </td></tr></tbody></table>

<h1>Configuration</h1>

1. create the file on flash memory, we use this file as secondary buffer pool. (In windows, InnoDB will auto create this file)<br>
<br>
<pre><code>[root@xen-server ~]# dd if=/dev/zero of=ib_sbpfile bs=16384 count=58880 <br>
[root@xen-server ~]# chown mysql:mysql ib_sbpfile<br>
</code></pre>

2. edit the my.cnf file, add followings:<br>
<br>
<pre><code>[mysqld]<br>
innodb-secondary-buffer-pool-size=920M<br>
innodb-secondary-buffer-pool-file=/flash/ib_sbpfile<br>
innodb_secondary_buffer_pool_preload_table=tpcc.*:test.t<br>
</code></pre>


3. watch secondary buffer pool status using show innodb status\G:<br>
<pre><code>mysql&gt; show engine innodb status\G;<br>
*************************** 1. row ***************************<br>
......<br>
----------------------<br>
SECONDARY BUFFER POOL<br>
----------------------<br>
Secondary buffer pool size      58880<br>
Free pages      126<br>
LRU pages       58754<br>
Page reads 971180, sync 548939, swap 490185<br>
Secondary buffer pool hit rate 916 / 1000 (in 23.00 sec)<br>
649.10 reads/s, 334.16 sync/s, 336.25 swap/s (in 23.00 sec)<br>
......<br>
</code></pre>
4. new innodb status variables:<br>
<pre><code>mysql&gt; show global status like 'innodb_sec%';<br>
+----------------------------------------------------+--------+<br>
| Variable_name                                      | Value  |<br>
+----------------------------------------------------+--------+<br>
| Innodb_secondary_buffer_pool_reads                 | 269080 |<br>
| Innodb_secondary_buffer_pool_sync                  | 201435 |<br>
| Innodb_secondary_buffer_pool_swap                  | 214080 |<br>
| Innodb_secondary_buffer_pool_make_young            | 269080 |<br>
| Innodb_secondary_buffer_pool_skip_unuseful         | 9325   |<br>
| Innodb_secondary_buffer_pool_skip_write_overloaded | 0      |<br>
+----------------------------------------------------+--------+<br>
6 rows in set (0.00 sec)<br>
</code></pre>
5. after enable innodb_secondary_buffer_pool_preload_table, you will see the following lines in .err file:<br>
<pre><code>100329 11:09:55  InnoDB: preloading table tpcc.warehouse to secondary buffer pool.(0.00%)<br>
100329 11:09:55  InnoDB: preloading table tpcc.item to secondary buffer pool.(0.00%)<br>
100329 11:09:55  InnoDB: preloading table tpcc.new_orders to secondary buffer pool.(1.01%)<br>
100329 11:09:55  InnoDB: preloading table tpcc.history to secondary buffer pool.(1.27%)<br>
100329 11:09:55  InnoDB: preloading table tpcc.district to secondary buffer pool.(4.57%)<br>
100329 11:09:55  InnoDB: preloading table tpcc.customer to secondary buffer pool.(4.57%)<br>
100329 11:09:56  InnoDB: preloading table tpcc.order_line to secondary buffer pool.(25.85%)<br>
100329 11:09:56  InnoDB: preloading table tpcc.orders to secondary buffer pool.(57.90%)<br>
100329 11:09:57  InnoDB: preloading table tpcc.stock to secondary buffer pool.(60.12%)<br>
100329 11:09:57  InnoDB: preloading to secondary buffer pool finish.<br>
</code></pre>
<h1>Next New Feature</h1>
<ol><li>allow to pin the table into secondary buffer pool.<br>
</li><li><del>add LRU aglorithm to secondary buffer pool.</del>
</li><li>add secondary buffer pool status info to INFORMATION_SCHEMA.</li></ol>
