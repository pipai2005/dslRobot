SCENE 手机
ON_INTENT 商品推荐
IF 预算 <= 3000 AND 品牌 == "小米"
    REPLY "推荐小米13，性价比高"
ELSE IF 预算 > 3000 OR 品牌 == "苹果"
    REPLY "推荐iPhone 15，性能强劲"
ELSE
    REPLY "请提供更多需求，以便精准推荐"