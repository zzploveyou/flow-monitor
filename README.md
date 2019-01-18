爬取路由器实时设备网速数据，记录流量消耗

路由器型号：TL-WDR7500

# 运行流量监控

```
python3 main.py
```

# 收集流量数据
```
python collect.py
```

```
$ tree flow
flow
├── Honor_6X.csv
├── iPhone8.csv
├── LAPTOP-123.csv
├── Unknown.csv
└── haha-personal.csv
```

```
$ cat flow/iPhone8.csv
2019-01-12,0M,6M
2019-01-15,0M,1M
2019-01-16,0M,16M
```