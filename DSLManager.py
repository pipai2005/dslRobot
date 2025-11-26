import os
import re
from typing import Dict, List, Optional
from src.lexer import lexer
from src.parser import parser, reset_parser
from src.qwen_api import QWENAPI
from src.executor import ASTExecutor
from src.preprocessor import NLPPreprocessor  # 新增导入

class DSLManager:
    def __init__(self, dsl_directory: str = "src/dsl"):
        self.dsl_directory = dsl_directory
        self.recognizer = QWENAPI()
        self.preprocessor = NLPPreprocessor()  # 初始化预处理层
        self.dsl_cache = {}
        self.sym_tbl = {}  # 移至实例变量
        
        # 意图到DSL文件的映射（保持不变）
        self.intent_to_dsl = {
            '商品推荐': 'product_recommend.dsl',
            '价格查询': 'price_query.dsl', 
            '功能对比': 'feature_compare.dsl',
            '库存查询': 'stock_query.dsl',
            '自然沟通': 'natural_chat.dsl'
        }
        
        # 场景到DSL文件的映射（保持不变）
        self.scene_to_dsl = {
            '手机': 'phone.dsl',
            '笔记本电脑': 'laptop.dsl',
            '无线耳机': 'earphone.dsl',
            '平板电脑': 'tablet.dsl',
            '智能手表': 'smartwatch.dsl'
        }
    

    def load_dsl_script(self, script_name: str) -> Optional[str]:
        """加载DSL脚本文件"""
        if script_name in self.dsl_cache:
            return self.dsl_cache[script_name]
            
        script_path = os.path.join(self.dsl_directory, script_name)
        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.dsl_cache[script_name] = content
                return content
        except FileNotFoundError:
            print(f"DSL脚本文件不存在: {script_path}")
            return None

    def select_dsl_script(self, intent_result: Dict) -> Optional[str]:
        """根据意图识别结果选择合适的DSL脚本"""
        intent = intent_result.get('intent', '')
        category = intent_result.get('category', '')
        
        # 优先根据意图选择脚本
        if intent in self.intent_to_dsl:
            script_name = self.intent_to_dsl[intent]
            return self.load_dsl_script(script_name)
        
        # 其次根据商品类别选择
        elif category in self.scene_to_dsl:
            script_name = self.scene_to_dsl[category]
            return self.load_dsl_script(script_name)
        
        # 默认脚本
        else:
            return self.load_dsl_script('hello.dsl')
    
    def execute_dsl(self, user_input: str) -> str:
        """执行完整的DSL处理流程"""
        try:
            # 1. 重置状态
            reset_parser()
            self.sym_tbl.clear()
            
            # 2. 意图识别与预处理
            print("正在进行意图识别...")
            intent_result = self.recognizer.recognize_intent(user_input)
            
            # 3. 预处理模糊输入
            dsl_content = None
            if not intent_result or intent_result.get('intent') == '自然沟通':
                print("进行自然语言预处理...")
                dsl_content = self.preprocessor.preprocess(user_input)
                if not dsl_content:
                    return "抱歉，未能理解您的需求，请重新表述"
            else:
                # 4. 选择合适的DSL脚本
                dsl_content = self.select_dsl_script(intent_result)
                if not dsl_content:
                    return "抱歉，暂时无法处理您的请求"
            
            print(f"处理后的DSL脚本:\n{dsl_content}")
            
            # 5. 提取参数
            if intent_result:
                self.extract_parameters(intent_result)
            print(f"符号表参数: {self.sym_tbl}")
            
            # 6. 解析生成AST
            ast = parser.parse(dsl_content, lexer=lexer)
            if not ast:
                return "脚本解析失败"
            
            # 7. 执行AST
            executor = ASTExecutor(self.sym_tbl)
            result = executor.execute(ast)
            return result.get('reply', '抱歉，没有找到合适的结果')
            
        except Exception as e:
            print(f"DSL执行错误: {e}")
            return "系统处理出现错误，请稍后重试"

    # 修改参数提取方法使用实例变量
    def extract_parameters(self, intent_result: Dict) -> None:
        self.sym_tbl.clear()
        self.sym_tbl['scene'] = intent_result.get('category', '')
        self.sym_tbl['intent'] = intent_result.get('intent', '')
        
        params = intent_result.get('params', {})
        if isinstance(params, dict):
            for key, value in params.items():
                self._add_to_symbol_table(key, value)
        elif isinstance(params, str) and params != "无":
            self._parse_params_from_string(params)

    def _add_to_symbol_table(self, key: str, value) -> None:
        # 实现保持不变，使用self.sym_tbl
        if isinstance(value, (int, float)):
            self.sym_tbl[key] = value
        elif isinstance(value, str):
            if value.replace('.', '').replace('-', '').isdigit():
                self.sym_tbl[key] = float(value)
            else:
                self.sym_tbl[key] = value
        else:
            self.sym_tbl[key] = str(value)

    def _parse_params_from_string(self, params_str: str) -> None:
        # 实现保持不变，使用self.sym_tbl
        budget_match = re.search(r'(\d+)元', params_str)
        if budget_match:
            self.sym_tbl['预算'] = float(budget_match.group(1))
            self.sym_tbl['价格'] = float(budget_match.group(1))
        
        weight_match = re.search(r'(\d+\.?\d*)kg', params_str)
        if weight_match:
            self.sym_tbl['重量'] = float(weight_match.group(1))
        
        brands = ['苹果', '华为', '小米', '三星', '联想', '戴尔']
        for brand in brands:
            if brand in params_str:
                self.sym_tbl['品牌'] = brand
                break
        
        features = ['轻薄', '游戏', '办公', '学习', '续航', '拍照', '性能']
        for feature in features:
            if feature in params_str:
                self.sym_tbl[feature] = True