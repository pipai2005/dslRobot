SCENE 通用
ON_INTENT 商品推荐
# LLM 识别的 category/brand/budget 都会在符号表中

# 规则 1: 针对高预算需求
IF 预算 > 5000 
    REPLY "SEARCH_TEMPLATE: 您的预算较高，我们为您推荐
    高品质的{category}：{model}（{brand}），价格是{budget}元，{context_desc}，是高端之选。"

# 规则 2: 针对有品牌要求
ELSE IF 品牌
    REPLY "SEARCH_TEMPLATE: 针对您的{brand}品牌需求，我们为您推荐
    {category}：{model}，它是一款{context_desc}的产品。"
    
# 规则 3: 仅有预算要求
ELSE IF 预算
    REPLY "SEARCH_TEMPLATE: 在{预算}元预算范围内，我们为您推荐
    {category}：{model}，这款产品{context_desc}，性价比很高。"

# 规则 4: 通用推荐策略：只要类别（scene）存在就进行搜索
ELSE IF scene 
    REPLY "SEARCH_TEMPLATE: 好的，针对您提出的{category}需求，为您推荐
    一款热门商品：{model}（{brand}），它是一款{context_desc}的产品。"

# 规则 5: 最终回退
ELSE
    REPLY "请提供更多需求，例如预算或品牌，以便为您精准推荐您想要的{category}。"