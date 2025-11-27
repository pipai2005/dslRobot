# src/test/stubs/qwen_stub.py

from typing import Dict, Optional

class QWENAPIStub:
    """模拟QWENAPI的意图识别返回结果，避免调用真实API"""
    
    def __init__(self, mock_result: Optional[Dict] = None):
        # 默认返回结果：用于兜底或商品推荐测试
        self.mock_result = mock_result or {
            "category": "手机",
            "intent": "商品推荐",
            "params": {"预算": 5000, "品牌": "小米"}
        }

    def recognize_intent(self, user_input: str) -> Dict:
        """根据用户输入动态返回不同结果（模拟LLM的意图识别逻辑）"""
        
        # 匹配单元测试中的输入
        if "价格" in user_input and "小米14" in user_input:
            return {
                "category": "手机",
                "intent": "价格查询",
                "params": {"品牌": "小米", "型号": "小米14"} 
            }
        elif "库存" in user_input and "麻辣小龙虾" in user_input:
            return {
                "category": "食物",
                "intent": "库存查询",
                "params": {"品牌": "王小二", "型号": "麻辣小龙虾"}
            }
        elif "聊天" in user_input or "你好" in user_input or "功能" in user_input:
            return {
                "category": "通用",
                "intent": "自然沟通",
                "params": "" # 无参数
            }
        elif "推荐" in user_input:
            # 匹配数据驱动测试：推荐3000元的华为手机
            if "华为手机" in user_input:
                 return {
                    "category": "手机",
                    "intent": "商品推荐",
                    "params": {"预算": 3000, "品牌": "华为"}
                }
            # 🚨 修复：匹配用户报告的“推荐一本书”的测试输入
            elif "本书" in user_input and "学习" in user_input:
                 return {
                    "category": "书籍",  # 匹配DSLManager中的 _normalize_category
                    "intent": "商品推荐",
                    "params": {"用途": "学习"}
                }
            # 兜底商品推荐
            return self.mock_result
        
        # 用于数据驱动测试的兜底逻辑
        else:
            # 简单地从 mock_result 提取意图，用于数据驱动测试
            return {
                "category": "手机",
                "intent": self.mock_result.get("intent", "商品推荐"),
                "params": self.mock_result.get("params", {})
            }