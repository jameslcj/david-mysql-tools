Contact me if you wanna know more about this project or my support in using it:<br>
Mail: jiangchengyao@gmail.com<br>
MSN: jiangchengyao@gmail.com<br>
Weibo: insidemysql<br>

# Flash Cache for InnoDB<br>
<br>
<h1>Introduction</h1>

This is a new flash cache solution for InnoDB, which is totally different from the previous Secondary Buffer Pool for InnoDB. The main feature is:<br>
<br>
1. Write on SSD is sequential, no random writes on SSD<br>
2. Flash cache is a persistent cache.<br>
3. Can do merge write.<br>
4. Cache both read and write.<br>


<h1>Architecture</h1>

In this flash cache solution, it replaces the original InnoDB doublewrite file, where pages first sequential write here and then flush to disk. Originally, doublewrite is to avoid partial write problem, no read on it. The difference is when using SSD, we can have a large doublewrite, for example, 100G or 300G. Page first write still happened here(also sequential). After a period time, the page on SSD is flush to disk. Because same page, with different LSN, may on the flash cache, flushing page from flash cache to disk only need the newest page with the fresh version. Hence, this makes the merge write happen. Furthermore, page can be read from doublewrite, which use the feature of high random IOPS of SSD.<br>
<br>
<b>Figure 1-1 Flash Cache Architecture</b><br>
<img src='http://img5.ph.126.net/jDZ7G2l-LujTW7D4T9-3LQ==/6597371032844386065.jpg' />

For internal view, flash cache is more like a redo log file. All the writes are appended in the end of the file.<br>
<br>
<b>Figure 1-2 Flash Cache Internal Architecture</b><br>
<img src='http://blog.chinaunix.net/attachment/201112/20/196376_1324350655OBBV.png' />

There is a new background thread, flash cache thread, for flushing flash cache block on SSD to the real tablespace location. The flush strategy is:<br>
1. If the total number of flash cache block is lower than <b>innodb_flash_cache_write_cache_pct</b>(default is 10, means 10% of flash cache size), flash cache thread will not flush flash cache block to disk except that MySQL server is idle. The design is for high merge write ratio. If you want high merge write ratio, you can increase this variable. <br>
2. Else, if If the total number of flash cache block is lower than <b>innodb_flash_cache_do_full_io_pct</b>, flash cache thread will flush 10% innodb_io_capacity page to disk per second. For example, if you set innodb_io_capacity to 1000, then only 100 pages will be flushed. But, because of merge write, not all 100 pages will be flushed to disk.<br>
3. Else, flash thread will flush 100% innodb_io_capactiy pages to disk.<br>
<br>
<h2>Data Structure</h2>

<pre><code>/** flash cache block strunct */<br>
struct fc_block_struct{<br>
	ulint	space:32;	/*!&lt; tablespace id */<br>
	ulint	offset:32;	/*!&lt; page number */<br>
	ulint	fil_offset:32;	/*!&lt; flash cache page number */<br>
	ulint	state:2;			/*!&lt; flash cache block state */<br>
	fc_block_t* hash;	/*!&lt; hash chain */<br>
	unsigned	is_aio_reading:1; /*!&lt; if is in aio reading status */<br>
};<br>
<br>
/** flash cache struct */<br>
struct fc_struct{<br>
	mutex_t			mutex; /*!&lt; mutex protecting flash cache */<br>
	hash_table_t*	hash_table; /*!&lt; hash table of flash cache blocks */<br>
	mutex_t			hash_mutex; /* mutex protecting flash cache hash table */<br>
	ulint			size; /*!&lt; flash cache size */<br>
	ulint			write_off; /*!&lt; write to flash cache offset */<br>
	ulint			flush_off; /*!&lt; flush to disk this offset */<br>
	ulint			write_round; /*!&lt; write round */<br>
	ulint			flush_round; /*!&lt; flush round */<br>
	fc_block_t* block; /*!&lt; flash cache block */<br>
	byte*			read_buf_unalign; /*!&lt; unalign read buf */<br>
	byte*			read_buf;	/*!&lt; read buf */<br>
};<br>
</code></pre>

<h1>Variables</h1>
<h3>innodb_flash_cache_file</h3>
Where is the flash cache file name. For example:<br>
<pre><code>innodb_flash_cache_file=/ssd/my_fcfile<br>
</code></pre>
<h3>innodb_flash_cache_size</h3>
Size of flash cache. For example:<br>
<pre><code>innodb_flash_cache_size = 100G<br>
</code></pre>
<h3>innodb_flash_cache_is_raw</h3>
You can use raw device as flash cache. Default valuse is 0.<br>
<h3>innodb_flash_cache_enable_migrate</h3>
Enable page migrate to flash cache. If page is read into buffer pool, and than swap from LRU list. But this page is not changed in the buffer pool, so it will not in the flash cahce. Set innodb_flash_cache_enable_migrate to 1 will write is page to flash cache when swap out from LRU list. Default: 1<br>
<h3>innodb_flash_cache_enable_move</h3>
Enable flash cache block move to new position. This design is for better read hit ratio. Default: 1<br>
<h3>innodb_flash_cache_move_limit</h3>
When to trigger flash cache block move. When the page is read from flash cache, but the flash cache block is in the lower part of the position(which means it maybe write soon), then it will move the flash cache block to new position. Default: 90<br>
<h3>innodb_flash_cache_warmup_table</h3>
Read page from table to flash cache. For example:<br>
<pre><code>innodb_flash_cache_warmup_table=tpcc.*<br>
innodb_flash_cache_warmup_table=tpcc.stock<br>
innodb_flash_cache_warmup_table=tpcc.stock:sbtest:sbtest1<br>
</code></pre>
<h1>Patch</h1>
patch for MySQL 5.5.20<br>
<a href='http://david-mysql-tools.googlecode.com/files/fc.patch'>http://david-mysql-tools.googlecode.com/files/fc.patch</a>