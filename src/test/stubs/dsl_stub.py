# src/test/stubs/dsl_stub.py

from typing import Dict, List, Optional

# 模拟DSL文件内容，避免读取真实的.dsl文件
def load_mock_dsl(script_name: str) -> str:
    """根据脚本名返回预设的DSL脚本内容"""
    
    # === 1. 自然沟通 (natural_chat.dsl) ===
    if script_name == "natural_chat.dsl":
        return """
            SCENE 通用
            ON_INTENT 自然沟通
            IF intent == "自然沟通"
                REPLY "您好！我是智能商品助手，请问有什么可以帮您？"
            ELSE
                REPLY "我在听，请继续。"
        """.strip()
        
    # === 2. 价格查询 (price_query.dsl) ===
    # 模拟成功的回复模板。DSLManager.py 会处理 PRICE_QUERY_TEMPLATE
    elif script_name == "price_query.dsl":
        return """
            SCENE 通用
            ON_INTENT 价格查询
            IF 品牌 AND 型号
                REPLY "PRICE_QUERY_TEMPLATE:查询结果为{品牌}{型号}价格是{budget}元"
            ELSE
                REPLY "请提供具体的商品品牌和型号，我将为您查询价格。"
        """.strip()
        
    # === 3. 商品推荐 (product_recommendation.dsl) ===
    # 注意：使用项目结构中的正确文件名
    elif script_name == "generic_recommendation.dsl":
        return """
            SCENE 通用
            ON_INTENT 商品推荐
            IF 预算 <= 5000 AND 品牌 == "小米"
                REPLY "SEARCH_TEMPLATE:为您推荐{brand}{model}，{context_desc}，价格{budget}元"
            ELSE IF 预算 > 5000 AND 品牌 == "苹果"
                REPLY "SEARCH_TEMPLATE:为您推荐高端产品{brand}{model}，{context_desc}，价格{budget}元"
            ELSE
                REPLY "抱歉，没有找到符合您要求的产品。"
        """.strip()
        
    # === 4. 库存查询 (stock_query.dsl) ===
    # 模拟成功的回复模板。DSLManager.py 会处理 STOCK_QUERY_TEMPLATE
    elif script_name == "stock_query.dsl":
        return """
            SCENE 通用
            ON_INTENT 库存查询
            IF 品牌 AND 型号
                REPLY "STOCK_QUERY_TEMPLATE: {品牌}{型号}当前库存状态为{stock_status}"
            ELSE
                REPLY "请提供具体的商品品牌和型号，我将为您查询库存。"
        """.strip()
        
    else:
        # 兜底：防止因文件名不匹配导致系统忙
        return """
            SCENE 通用
            ON_INTENT 兜底
            ELSE
                REPLY "未找到对应脚本，请确认您的意图。"
        """.strip()