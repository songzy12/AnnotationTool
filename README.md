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