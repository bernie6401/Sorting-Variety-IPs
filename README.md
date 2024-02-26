# Sorting Variety IPs

## Description

這個tool主要是把雜亂的各種IP，以有序並且IP range的形式或是有Wildcard的形式呈現

## Input

`list_original`這個file就是儲存各式各樣的IP，可能有domain、有wildcard代表的所有subdomain的domain、IP range顯示的IP、單獨的IP、有Wildcard形式的IP，而且沒有一定誰先誰後，有可單獨IP接續domain又接續IP range的IP

```bash
www.tsim.org.tw
www.w3.org
*.microsoft.com
yahoo.com
1.0.0.0-2.0.0.0
1.1.1.1-2.2.2.2
0.0.0.0
114.35.123.91
120.96.24.*
4.4.5.*
5.*
```





## Output

主要是`list_ip_range_with_star`和`list_ip_range`這兩個檔案，前者主要是把上述亂七八糟的IP轉換成只有以下四種並且按照順序排列

```bash
{Wildcard Domain}
{Normal Domain}
{All Sorting Domain with Wildcard}
{Solo IP}
```

---

後者主要是合併所有**可以**連貫成IP range的IP們，變成一個大的IP Range，如下

```bash
{Wildcard Domain}
{Normal Domain}
{All Sorting Domain with IP range}
{Solo IP}
```

