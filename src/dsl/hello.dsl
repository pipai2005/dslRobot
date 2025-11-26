# 关键字
# SCENE      := 笔记本 | 手机 | 无
# ON_INTENT  := 商品推荐
# PARAMS     := 预算、重量、续航 等键值对
# REPLY      := 字符串

# 支持的最简语法
SCENE <scene>
ON_INTENT 自然沟通
IF 打招呼 == 你好
    REPLY "你好啊，我是商品推荐助手，可以为您推荐一些商品"