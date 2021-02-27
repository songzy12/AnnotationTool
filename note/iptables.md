查看设置：

```
sudo iptables -nL --line-numbers -t nat
```

删除设置：

```
sudo iptables -t nat -D PREROUTING 1
sudo iptables -t nat -D POSTROUTING 7
```

添加设置：

```
sudo iptables -t nat -A PREROUTING -p tcp --dport 9005 -j DNAT --to-destination 10.0.2.180:9005
sudo iptables -t nat -A POSTROUTING -p tcp -d 10.0.2.180 --dport 9005 -j SNAT --to-source 101.6.244.4
```

