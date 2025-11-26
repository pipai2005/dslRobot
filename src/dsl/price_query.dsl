# 价格查询规则
SCENE 价格查询
ON_INTENT 价格查询

IF 产品型号
    REPLY "正在查询{产品型号}的最新价格..."
ELSE IF 品牌 AND 产品类型
    REPLY "正在查询{品牌}{产品类型}的价格范围..."
ELSE
    REPLY "请告诉我您想查询哪款产品的价格？"