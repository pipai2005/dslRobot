SCENE 通用
ON_INTENT 库存查询

# 规则 1: 同时有品牌和型号 (最精确查询)
IF 品牌 AND 型号
    REPLY "STOCK_QUERY_TEMPLATE: 好的，请稍等，我正在查询{品牌}{型号}的库存。"

# 规则 2: 仅有品牌（返回该品牌最热门/最低价产品的库存）
ELSE IF 品牌
    REPLY "STOCK_QUERY_TEMPLATE: 好的，我将为您查询{品牌}的{scene}产品的库存。"

# 规则 3: 仅有型号（型号通常和品牌关联，作为兜底）
ELSE IF 型号
    REPLY "STOCK_QUERY_TEMPLATE: 好的，我将为您查询{型号}的库存。"

# 规则 4: 仅有类别（返回该类别的通用信息）
ELSE IF scene
    REPLY "抱歉，您只提供了{scene}类别。请提供具体的型号或品牌，以便为您查询库存。"

# 规则 5: 最终回退
ELSE
    REPLY "请问您要查询哪个商品的库存？请提供品牌和型号。"