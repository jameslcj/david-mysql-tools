Contact me if you wanna know more about this patch or my support in using it:<br>
Mail & Skype: jiangchengyao@gmail.com.<br>
Twitter: jdaaaaaavid<br>

<h1>Introduction</h1>

This patch improves MySQL slave to accelerate applying relay log.<br>
<br>
<br>
<h1>Details</h1>

MySQL(5.5) replication is a single-thread architecture, which means the slave apply the binary log one by one. This limits the total bandwidth of disk IO capacity and data on slave usually lag behind those on master. Sometimes this lag can be hours if more write IO pressure on master server. This problem will block user to use slave for scalability which usually migrate master read operation to slave.<br>
<br>
Start from MySQL 5.6, slave can use multiple thread to apply the binary log based on schema. This reduce the lag, but when all DML operation in one database, it still has the lag problem.<br>
<br>
Hence, I wanna a different solution to solve the problem. Slave applying the binary log is still in a single thread design. However, applying the binary log is in a batch style which likes :<br>
<pre><code>BEGIN:<br>
apply binary log;<br>
apply binary log;<br>
……<br>
apply binary log;<br>
COMMIT;<br>
</code></pre>

This will significantly reduce the fsync on slave, thus result in less lag or no lag at all. Nevertheless, another problem arises. How to solve data consistency when slave is crash. We can use a table to store  binary(relay) log position like MySQL 5.6 do. So the batch commit style like :<br>
<pre><code>BEGIN;<br>
apply binary log;<br>
update slave_relay_log_info set xxx ….<br>
apply binary log;<br>
update slave_relay_log_info set xxx …<br>
……<br>
apply binary log;<br>
update slave_relay_log_info set xxx …<br>
COMMIT;<br>
</code></pre>

<h1>Variables</h1>
<h3>batch_commit_max</h3>
max batch commit count<br>
<br>
<br>
<h1>Benchmark</h1>
benchmark: sysbench 0.5<br>
script: sysbench --test=update_index.lua --oltp-table-size=80000000 --oltp-dist-type=uniform --num-threads=16 --max-requests=0 --max-time=1800 --oltp-read-only=off  --report-interval=10 run<br>
result:<br>
<img src='http://img7.ph.126.net/VN-nMGXwFLHt9GrKZcEiWQ==/6598253940679858557.jpg' />

bc=1 means commit SQL query one by one, which likes what vanilla MySQL do. bc=500 means batching commit original 500 transactions all in one.  From the result you can see setting bc=500, almost no lag when benchmark finishes while bc=1 still need extra 30 minute to apply the relay log.<br>
<br>
<h1>Patch</h1>
patch for MySQL 5.5.20:<br>
<a href='https://david-mysql-tools.googlecode.com/files/batch_commit.patch'>https://david-mysql-tools.googlecode.com/files/batch_commit.patch</a>