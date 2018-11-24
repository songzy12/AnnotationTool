这个工具是用来标注小木的问答情况的。

运行：

```
python server.py
```

然后访问 `server.py` 里的 `port` 端口，可以看到课程列表。

然后点开一个课程名，可以看到该课程 id 下的小木问答情况。

我们对问答做了一定的过滤，使得结果里尽量不包含点击数据等。

该部分逻辑具体可参考 `read_message.py` 里的 `get_message` 函数。

具体来说：

* flag 是以下几个：`null`, `more`, `try`,  `cached`, `chaced_more`
* question_source 不是以下几个：`wobudong`, `active_question`
* 去重
* 去掉包含 `[    ]` 的结果

然后 response 里的 `a_text`,`q_text` 就是对应好的问答结果。

## 标注

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
