这个工具是用来标注小木的问答情况的。

这里有两个代码主文件：

* `question_server.py`：问题分类的标注，问题质量的标注
* `answer_server.py`：平台使用相关的问题，标注 es 给出的备选答案。

目前应该只使用了 question 相关的标注。



这里因为我们要对外能够访问，所以端口开在 zijing 上；

但是 zijing 直接读取线上机器的数据并进行计算的话太慢了。

当前的解决方式是服务实际运行在线上机器，然后在 zijing 上做端口转发。

在 doc 里有两个在查错时可能有用的文档：

* 端口转发配置
* 线上访问 vpn 配置

## start service

配置文件：

```
vi /etc/supervisor/conf.d/label_tool.conf
```

查看及启动：

```
sudo supervisorctl status
sudo supervisorctl restart label_tool
```

## question_server

运行：

```
python question_server.py
```

然后访问 `question_server.py` 里的 `port` 端口，可以看到课程列表。

然后点开一个课程名，可以看到该课程 id 下的小木问答情况。

我们对问答做了一定的过滤，使得结果里尽量不包含点击数据等。

具体来说：

* flag 是以下几个：`null`, `more`, `try`,  `cached`, `chaced_more`
* question_source 不是以下几个：`wobudong`, `active_question`
* 去重
* 去掉包含 `[    ]` 的结果

然后 response 里的 `a_text`,`q_text` 就是对应好的问答结果。

## label

关于问题的标注：
* 0: 平台使用相关
* 1: 课程信息相关
* 2: 简单知识点解释
* 3: 复杂知识点讨论
* 4: 反馈及建议
* 5: 聊天及其他
* 8: 预置的服务请求

关于回答的标注：
* both good:  问题和答案都很好
* good question: 问题是应该回答的问题，但是答案不好
* bad question: 问题是我们不想回答的问题
