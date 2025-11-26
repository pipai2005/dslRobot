import re
from typing import Dict, List

class NLPPreprocessor:
    """自然语言到DSL的预处理转换"""
    
    def __init__(self):
        # 关键词映射规则
        self.intent_patterns = {
            '商品推荐': [r'推荐', r'介绍', r'哪个好', r'选什么'],
            '价格查询': [r'多少钱', r'价格', r'价位', r'多少米'],
            '功能对比': [r'对比', r'区别', r'差异', r'哪个好'],
            '库存查询': [r'有货吗', r'库存', r'现货', r'能买到']
        }
        
        self.category_patterns = {
            '手机': [r'手机', r'智能机', r'电话机'],
            '笔记本电脑': [r'笔记本', r'电脑', r'本本'],
            '无线耳机': [r'耳机', r'耳塞', r'蓝牙耳机'],
            '平板电脑': [r'平板', r'平板电脑', r'pad']
        }
        
        # 价格提取规则
        self.price_pattern = re.compile(r'(\d+)\s*元')
        # 品牌提取规则
        self.brand_patterns = {
            '苹果': [r'苹果', r'iPhone', r'Apple'],
            '华为': [r'华为', r'HUAWEI'],
            '小米': [r'小米', r'Xiaomi'],
            '三星': [r'三星', r'Samsung']
        }

    def preprocess(self, user_input: str) -> str:
        """将自然语言转换为DSL片段"""
        # 1. 识别意图和类别
        intent = self._detect_intent(user_input)
        category = self._detect_category(user_input)
        
        if not intent or not category:
            return ""
            
        # 2. 提取参数
        price = self._extract_price(user_input)
        brand = self._extract_brand(user_input)
        
        # 3. 生成DSL片段
        dsl = f"SCENE {category}\n"
        dsl += f"ON_INTENT {intent}\n"
        
        # 生成条件块
        conditions = []
        if price:
            conditions.append(f"预算 <= {price}")
        if brand:
            conditions.append(f"品牌 == \"{brand}\"")
            
        if conditions:
            condition_str = " AND ".join(conditions)
            dsl += f"IF {condition_str}\n"
            dsl += f"    REPLY \"为您推荐{category}，符合{condition_str}条件\"\n"
            dsl += f"ELSE\n"
            dsl += f"    REPLY \"暂无符合条件的{category}推荐\"\n"
        else:
            dsl += f"IF 1\n"
            dsl += f"    REPLY \"为您推荐热门{category}\"\n"
            
        return dsl

    def _detect_intent(self, text: str) -> str:
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    return intent
        return "商品推荐"  # 默认意图

    def _detect_category(self, text: str) -> str:
        for category, patterns in self.category_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    return category
        return "手机"  # 默认类别

    def _extract_price(self, text: str) -> int:
        match = self.price_pattern.search(text)
        return int(match.group(1)) if match else 0

    def _extract_brand(self, text: str) -> str:
        for brand, patterns in self.brand_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return brand
        return ""