import os
import re
from typing import Dict, List, Optional, Any
from src.lexer import lexer
from src.parser import parser, reset_parser
from src.qwen_api import QWENAPI
from src.executor import ASTExecutor


class DSLManager:
    def __init__(self, dsl_directory: str = "src/dsl"):
        self.dsl_directory = dsl_directory
        self.recognizer = QWENAPI()
        self.dsl_cache = {}
        self.sym_tbl = {}
        
        # 简化的产品目录 (数据层)
        self.product_catalog = [
            {"category": "手机", "brand": "小米", "model": "小米14", "budget": 4500, "performance": 9, "context_desc": "高性能、高性价比"},
            {"category": "手机", "brand": "苹果", "model": "iPhone 15 Pro", "budget": 8500, "performance": 10, "context_desc": "顶级性能、专业摄影"},
            {"category": "手机", "brand": "苹果", "model": "iPhone SE", "budget": 3500, "performance": 6, "context_desc": "小屏旗舰，性价比之选"}, # <-- 新增：确保预算匹配
            {"category": "手机", "brand": "华为", "model": "Pura 70", "budget": 6000, "performance": 8, "context_desc": "优秀设计、拍照强大"},
            
            {"category": "衣服", "brand": "优衣库", "model": "超轻羽绒服", "budget": 500, "material": "羽绒", "context_desc": "轻薄保暖，通勤必备"},
            {"category": "衣服", "brand": "耐克", "model": "运动T恤", "budget": 200, "material": "棉涤", "context_desc": "透气吸汗，适合运动"},
            
            {"category": "食物", "brand": "三只松鼠", "model": "坚果礼盒", "budget": 150, "flavor": "原味", "context_desc": "健康零食，送礼佳品"},
            {"category": "食物", "brand": "王小二", "model": "麻辣小龙虾", "budget": 120, "flavor": "麻辣", "context_desc": "夜宵爆款，口味浓郁"},

            {"category": "书籍", "brand": "人教版出版社", "model": "高中数学", "budget": 20, "flavor": "有趣", "context_desc": "令人爱不释手的数学读物"},
            {"category": "书籍", "brand": "人教版出版社", "model": "高中语文", "budget": 20, "flavor": "有趣", "context_desc": "令人爱不释手的语文读物"},
            {"category": "书籍", "brand": "人教版出版社", "model": "高中英语", "budget": 20, "flavor": "有趣", "context_desc": "令人爱不释手的英语读物"},
        ]

        # 意图到DSL文件的映射
        self.intent_to_dsl = {
            '商品推荐': 'generic_recommendation.dsl',
            '价格查询': 'price_query.dsl', 
            '库存查询': 'stock_query.dsl', 
            '自然沟通': 'natural_chat.dsl'
        }
        
        # 场景到DSL文件的映射
        self.scene_to_dsl = {
            # 不重要
        }

    #  搜索目录的辅助函数：必须依赖 LLM 识别的 category 进行筛选
    def search_catalog(self, category: str, sym_tbl: Dict) -> Optional[Dict]:
        """根据 LLM 识别的类别和参数搜索最佳匹配产品"""
        
        # 1. 筛选出与用户查询类别匹配的候选产品
        candidates = [p for p in self.product_catalog if p.get('category') == category]
        
        best_match = None
        min_diff = float('inf')
        
        user_budget = sym_tbl.get('预算')
        user_brand = sym_tbl.get('品牌')
        
        for product in candidates:
            # 检查品牌
            if user_brand and product['brand'] != user_brand:
                continue
            
            # 检查预算 (如果产品价格超过用户预算，则跳过)
            if user_budget and product['budget'] > user_budget:
                continue
            
            # 优先返回预算最接近用户预算的产品
            current_diff = (user_budget if user_budget is not None else product['budget']) - product['budget']
            if current_diff >= 0 and current_diff < min_diff:
                min_diff = current_diff
                best_match = product
                    
        return best_match
    #  查询目录函数（区别于推荐的搜索逻辑）
    def search_catalog_for_query(self, category: str, brand: Optional[str], model: Optional[str]) -> Optional[Dict]:
        """为价格/库存查询提供精确搜索，只返回第一个精确匹配项"""
        brand = brand.replace(' ', '').strip() if brand else None
        model = model.replace(' ', '').strip() if model else None
        
        for p in self.product_catalog:
            if p.get('category') != category:
                continue

            # 优先级 1: 精确型号匹配
            if model and p.get('model') == model:
                return p
            
            # 优先级 2: 仅品牌匹配 (返回该品牌下的第一个产品作为示例)
            if not model and brand and p.get('brand') == brand:
                return p
        
        return None
    # 模板处理函数
    def _process_recommendation(self, final_reply: str, intent_result: Dict) -> str:
        """
        处理DSL返回的推荐模板，查找产品目录，并填充模板。
        """
        
        # 1. 检查是否为模板回复 (我们约定模板以 "SEARCH_TEMPLATE:" 开头)
        if not final_reply.startswith("SEARCH_TEMPLATE:"):
            return final_reply

        # 2. 解析模板
        reply_template = final_reply.split("SEARCH_TEMPLATE:")[1].strip()
        
        # 提取 Category 用于目录搜索（优先用符号表中的scene）
        specific_category = self.sym_tbl.get('scene', intent_result.get('category', '手机'))
        general_category = self._get_general_category(specific_category)

        # 3. 搜索产品目录
        product = self.search_catalog(general_category, self.sym_tbl)
        
        if not product:
            # 如果未找到产品，返回默认失败提示
            return f"抱歉，没有找到符合您当前需求的 {specific_category} 产品。"
            
        # 4. 准备模板填充数据：将符号表和产品信息合并，供模板使用
        template_data = {**self.sym_tbl, **product} 
        
        # 5. 填充模板
        try:
            # 简单的模板替换
            filled_reply = reply_template
            for key, value in template_data.items():
                filled_reply = filled_reply.replace(f"{{{key}}}", str(value))
                
            # 清理剩余的占位符（防止用户看到 {key}）
            import re
            filled_reply = re.sub(r'\{.*?\}', '[信息缺失]', filled_reply)

            return filled_reply
        except Exception as e:
            print(f"模板填充错误: {e}")
            return "系统错误：无法生成最终推荐回复。"
    def _process_price_query(self, final_reply: str) -> str:
        """处理 PRICE_QUERY_TEMPLATE，执行价格查询"""
        if not final_reply.startswith("PRICE_QUERY_TEMPLATE:"):
            return final_reply
        
        # 从符号表获取参数
        category = self.sym_tbl.get('scene', '商品')
        brand = self.sym_tbl.get('品牌')
        model = self.sym_tbl.get('型号')

        product = self.search_catalog_for_query(category, brand, model) 
        
        if not product:
            return f"抱歉，产品目录中没有找到 {brand if brand else ''}{model if model else ''} 这款{category}。"

        price = product.get('budget')
        if price is not None:
            return f"您查询的 {product['brand']} {product['model']} 的当前价格是 {price} 元。"
        else:
            return f"抱歉，暂无 {product['model']} 的价格信息。"
    def _process_stock_query(self, final_reply: str) -> str:
        """处理 STOCK_QUERY_TEMPLATE，执行库存查询（模拟）"""
        if not final_reply.startswith("STOCK_QUERY_TEMPLATE:"):
            return final_reply
        
        category = self.sym_tbl.get('scene', '商品')
        brand = self.sym_tbl.get('品牌')
        model = self.sym_tbl.get('型号')

        product = self.search_catalog_for_query(category, brand, model) 
        
        if not product:
            return f"抱歉，产品目录中没有找到 {brand if brand else ''}{model if model else ''} 这款{category}。"

        # 模拟库存逻辑：高端机型（如 iPhone 15 Pro）或热门食物（如麻辣小龙虾）缺货
        is_high_demand = product.get('budget', 0) > 8000 or product.get('model') == '麻辣小龙虾'
        has_stock = not is_high_demand
        
        stock_status = "有充足现货，您可以立即下单" if has_stock else "暂时缺货，预计三天内到货"
        
        return f"{product['brand']} {product['model']} 的当前库存状态是：{stock_status}。"
    # ... (load_dsl_script 保持不变) ...
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
        
        print(f"正在根据意图[{intent}]选择脚本...") # 调试信息

        # 1. 优先根据意图映射选择 (包括 '自然沟通')
        if intent in self.intent_to_dsl:
            return self.load_dsl_script(self.intent_to_dsl[intent])
        
        # 2. 其次根据商品类别选择
        elif category in self.scene_to_dsl:
            return self.load_dsl_script(self.scene_to_dsl[category])
        
        # 3. 如果都匹配不到，默认使用自然沟通
        else:
            return self.load_dsl_script('natural_chat.dsl')
    
    def execute_dsl(self, user_input: str) -> str:
        """执行完整的DSL处理流程"""
        try:
            # 1. 重置状态
            reset_parser()
            self.sym_tbl.clear()
            
            # 2. 意图识别
            print("正在进行意图识别...")
            intent_result = self.recognizer.recognize_intent(user_input)        
            # 意图识别为空的兜底逻辑
            if not intent_result:
                print("意图识别为空，切换至默认自然沟通模式...")
                intent_result = {'intent': '自然沟通', 'category': '通用', 'params': {}}
            # 意图归一化：处理LLM的偏差，统一意图名称
            raw_intent = intent_result.get('intent', '')
            
            # 从原始结果中尝试获取问题参数
            # LLM有时会将问题类型识别到params中，例如：'params': {'问题': '库存'}
            params = intent_result.get('params', {})
            if not isinstance(params, dict):
                params = {} # 如果是字符串（如“无”）或其他非字典类型，设置为空字典

            # 从原始结果中尝试获取问题参数
            problem_type = params.get('问题', '')
            
            # 优先级 1: 明确的库存查询关键词 - 覆盖所有意图，包括错误的“价格查询”
            if '库存' in user_input or '还剩' in user_input or '有货' in user_input or '存货' in user_input or problem_type == '库存':
                 intent_result['intent'] = '库存查询'           
            # 优先级 2: 明确的价格查询关键词
            elif '多少钱' in user_input or '价格' in user_input or '价位' in user_input or problem_type == '价格':
                 intent_result['intent'] = '价格查询'
            # 优先级 3: 通用商品查询的兜底逻辑
            elif raw_intent in ['商品查询', '查询']:
                 # 如果是通用查询，默认还是价格查询
                 intent_result['intent'] = '价格查询'
                 
            # 3. 选择合适的DSL脚本
            dsl_content = self.select_dsl_script(intent_result)
            
            if not dsl_content:
                # ... (缺少DSL脚本的逻辑) ...
                return "抱歉，系统暂时无法处理您的请求。"
            

            # 4. 提取参数
            self.extract_parameters(intent_result)
            # 品牌兜底提取：如果LLM没识别，从用户输入中提取
            if '品牌' not in self.sym_tbl:
                self._extract_brand_from_raw_input(user_input)
            
            # 品牌兜底提取：
            if '品牌' not in self.sym_tbl:
                self._extract_brand_from_raw_input(user_input)
            
            #  商品识别兜底：推导缺失的 scene 和 model (必须在归一化之前)
            # 只有在 scene 缺失或型号缺失时才运行
            if self.sym_tbl.get('scene') in ['无', None] or self.sym_tbl.get('型号') is None:
                 self._identify_specific_product_fallback(user_input)

            #  类别归一化：将 '零食'/'三只松鼠' 映射为 '食物'
            raw_scene = self.sym_tbl.get('scene')
            if raw_scene:
                self.sym_tbl['scene'] = self._normalize_category(raw_scene)
            
            print(f"符号表参数: {self.sym_tbl}")


            # 5. 解析生成AST
            ast = parser.parse(dsl_content, lexer=lexer)
            
            # 6. 执行AST
            executor = ASTExecutor(self.sym_tbl)
            result = executor.execute(ast)          
            final_reply = result.get('reply', '抱歉，没有找到合适的结果')

            # 7. 处理模板
            intent = self.sym_tbl.get('intent')
            
            if intent == '价格查询':
                final_reply = self._process_price_query(final_reply)
            elif intent == '库存查询':
                final_reply = self._process_stock_query(final_reply)
            elif intent == '商品推荐':
                 final_reply = self._process_recommendation(final_reply, intent_result)# 8. 通用占位符替换（针对非 SEARCH_TEMPLATE 的纯文本回复）
         
             # 解决像 "请提供更多需求...{category}" 这种在 ELSE 块中出现的占位符
            if '{category}' in final_reply:
                # 尝试获取LLM识别的类别
                specific_category = self.sym_tbl.get('scene', '商品')
                
                # 尝试获取通用类别（如果存在 _get_general_category）
                try:
                    general_category = self._get_general_category(specific_category)
                except AttributeError:
                    general_category = specific_category
                    
                final_reply = final_reply.replace('{category}', general_category)

            return final_reply
            
            
        except Exception as e:
            # 🚨 临时修改，以便在测试运行时看到真正的错误堆栈
            import traceback
            print("\n" + "="*50)
            print("【致命错误】DSLManager.execute_dsl 中发生异常！")
            traceback.print_exc()
            print("="*50 + "\n")
            
            # 返回错误信息，但此时已经打印了堆栈
            return self.error_reply # '系统正忙，请稍后再试。'
            
        return self._process_reply_template(raw_reply)

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

        if '品牌' not in self.sym_tbl:
            self._extract_brand_from_scene(self.sym_tbl.get('scene', ''))

    def _add_to_symbol_table(self, key: str, value) -> None:
        if isinstance(value, (int, float)):
            self.sym_tbl[key] = value
        elif isinstance(value, str):
            # [关键修正] 移除字符串中的所有空白字符
            cleaned_value = value.replace(' ', '').strip() 
            
            if cleaned_value.replace('.', '').replace('-', '').isdigit():
                self.sym_tbl[key] = float(cleaned_value)
            else:
                self.sym_tbl[key] = cleaned_value # 使用清理后的值
        else:
            self.sym_tbl[key] = str(value)

    def _parse_params_from_string(self, params_str: str) -> None:

        budget_match = re.search(r'(\d+)元', params_str)
        if budget_match:
            self.sym_tbl['预算'] = float(budget_match.group(1))
            self.sym_tbl['价格'] = float(budget_match.group(1))

        
        features = ['轻薄', '游戏', '办公', '学习', '续航', '拍照', '性能']
        for feature in features:
            if feature in params_str:
                self.sym_tbl[feature] = True

    def _get_general_category(self, specific_category: str) -> str:
        """从具体类别（如'耐克衣服'）中解析出通用类别（如'衣服'）"""
        # 假设产品目录中的 category 列表是所有通用类别的权威来源
        all_categories = set(p['category'] for p in self.product_catalog)
        
        for category in all_categories:
            if category in specific_category:
                return category
        return specific_category # 兜底，如果找不到，就用原始的

    def _extract_brand_from_scene(self, scene_str: str) -> None:
        """从场景/类别字符串中提取品牌，作为符号表的兜底"""
        # 扩展品牌列表，使其包含所有类别的品牌
        brands = ['苹果', '华为', '小米', '三星', '联想', '戴尔', '耐克', 
                  '优衣库', '三只松鼠', '王小二']
        for brand in brands:
            if brand in scene_str:
                self.sym_tbl['品牌'] = brand
                return
            

    def _extract_brand_from_raw_input(self, text: str) -> None:
        """从原始输入中提取品牌，作为符号表的兜底"""
        all_brands = [p['brand'] for p in self.product_catalog] # 从产品目录中动态获取品牌
        unique_brands = list(set(all_brands))
        
        cleaned_text = text.replace(' ', '').lower()
        
        for brand in unique_brands:
            if brand.lower() in cleaned_text:
                self.sym_tbl['品牌'] = brand
                return
            
    def _identify_specific_product_fallback(self, user_input: str) -> None:
        """
        [兜底逻辑] 通过匹配品牌/型号来推导正确的 scene 和 model。
        """
        input_lower = user_input.lower().replace(' ', '')
        
        for p in self.product_catalog:
            # 优先级 1: 检查用户输入是否包含产品型号 (如：'高中数学'、'小米14')
            if p['model'].lower() in input_lower:
                self.sym_tbl['scene'] = p['category']
                self.sym_tbl['型号'] = p['model']
                self.sym_tbl['品牌'] = p['brand']
                return
            
            # 优先级 2: 检查用户输入是否包含品牌，且当前 scene 错误地设置为品牌名 (如：scene='三只松鼠')
            # 只要识别出品牌，并且当前符号表中的 scene 与其不一致，我们就用产品的 category 覆盖 scene。
            if p['brand'].lower() in input_lower:
                 # 修正错误的 scene：用产品的 category 覆盖错误的 scene/品牌名
                 if self.sym_tbl.get('scene') == self.sym_tbl.get('品牌'):
                     self.sym_tbl['scene'] = p['category'] # 修正为 '食物'
                     
                 # 补充型号：如果用户没说型号，就用该品牌最热门的型号（第一个匹配到的）
                 if '型号' not in self.sym_tbl:
                      self.sym_tbl['型号'] = p['model'] # 补充为 '坚果礼盒'
                 
                 # 如果找到了品牌，就可以停止了，让后续逻辑处理
                 return
            
    def _normalize_category(self, raw_category: str) -> str:
        """
        将LLM识别的原始类别名称映射到产品目录中的通用类别。
        """
        # 定义类别映射规则：LLM识别的类别 -> 产品目录中的通用类别
        category_map = {
            '零食': '食物',
            '小吃': '食物',
            '零食礼盒': '食物',
            '教材': '书籍',
            '课本': '书籍',
            '文学': '书籍',
            '服装': '衣服',
            '三只松鼠': '食物',
            '耐克': '运动鞋',
            '运动鞋': '运动鞋',
            '手机': '手机',
            '电脑': '电脑',
            '笔记本': '电脑',
            '电视': '电视',
            '电脑配件': '电脑',
            '电脑办公': '电脑',
            '电脑软件': '电脑',
            '电脑硬件': '电脑',
            '电脑游戏': '电脑',
            '电脑办公套装': '电脑',
            '电脑配件': '电脑',
            '外套': '衣服',
            '运动服': '衣服',
            '电子产品': '手机', # 广义的电子产品，默认映射到最常用的手机
            '智能手机': '手机'
        }
        
        # 如果 raw_category 是目录中已有的，直接返回
        all_catalog_categories = set(p['category'] for p in self.product_catalog)
        if raw_category in all_catalog_categories:
            return raw_category
            
        # 否则，尝试映射
        return category_map.get(raw_category, raw_category)