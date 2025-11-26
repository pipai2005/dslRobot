import os
import json
from openai import OpenAI  # OpenAI SDK v1.0+ 核心客户端
from typing import Optional, Dict

class QWENAPI:
    """
    基于OpenAI SDK的用户意图识别器（作业核心模块）
    功能：接收商品推荐场景的用户自然语言输入，输出结构化意图结果，为DSL解释器提供驱动数据
    """
    def __init__(self):
        # 1. 加载.env配置（作业“安全编码”要求：避免密钥硬编码）
        self._load_config()
        # 2. 初始化OpenAI客户端
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

    def _load_config(self) -> None:
        self.api_key = os.getenv("DASHSCOPE_API_KEY")
        self.base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        self.model = "qwen3-max"  # 在recongnize_intent()方法中指定具体模型
        
        # 验证配置是否缺失（避免后续调用失败）
        if not self.api_key:
            raise ValueError("配置DASHSCOPE_API_KEY失败")
        if not self.base_url:
            raise ValueError("配置DASHSCOPE_BASE_URL失败")
        if not self.model:
            raise ValueError("配置QWEN_MODEL失败")

    def recognize_intent(self, user_input: str) -> Optional[Dict]:
        """
        调用OpenAI模型识别用户意图（作业“LLM意图识别”核心需求）
        :param user_input: 用户自然语言输入（如“推荐1000元内学生用手机”）
        :return: 结构化意图结果（含intent-意图类型、category-商品类别、params-关键参数），失败返回None
        """
        # 1. 构造意图识别Prompt（作业“驱动DSL”关键：明确输出格式，便于后续解析）
        system_prompt = """
            你是商品推荐场景的意图识别工具，需对用户输入进行意图分析，并严格按照以下格式输出JSON结果（不添加任何解释文字）：
            {
            "category": "商品类别（如“手机”“无线耳机”，无则填“无”）",
            "intent": "意图类型（仅允许：“商品推荐”“商品查询”“自然沟通”“其他”）",
            "params": "关键参数（如{\"预算\": 1500, \"功能\": \"降噪\"， \"问题\": \"续航时间\", \"打招呼\": \"你好\"}）"}，无则填“无”）"
            }
        """
        
        user_prompt = f"用户输入：{user_input}"

        # 2. 调用OpenAI模型（按SDK v1.0+ 格式发起对话请求）
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1  # 降低随机性，确保意图识别结果稳定（作业场景需确定性输出）
            )

            # 3. 解析模型输出（提取结构化意图结果）
            llm_output = response.choices[0].message.content.strip()
            # 转换为JSON字典（适配DSL解释器的输入格式）
            intent_result = json.loads(llm_output)
            return intent_result

        # 4. 异常处理（作业“严谨验证”要求：覆盖常见错误场景）
        except json.JSONDecodeError as e:
            print(f"解析LLM输出失败（非标准JSON）：{llm_output}，错误：{str(e)}")
            return None
        except KeyError as e:
            print(f"模型输出缺失关键字段：{str(e)}，完整输出：{llm_output}")
            return None
        except Exception as e:
            print(f"OpenAI API调用异常：{str(e)}")
            return None

# 模块自测（直接运行文件验证基础功能，作业“调试验证”需求）
# 一问一答循环交互（核心新增逻辑）
if __name__ == "__main__":
    try:
        recognizer = QWENAPI()
        print("============= 商品推荐智能客服意图识别 ============")
        print("【提示】输入您的需求（如“推荐6000元轻薄本”），或输入“退出”可结束程序")
        print("=" * 50)
        
        # 循环交互逻辑
        while True:
            # 接收用户输入
            user_input = input("\n请输入您的需求 > ").strip()
            
            # 处理退出指令
            if user_input.lower() in ["退出", "quit", "exit","q"]:
                print("感谢使用，程序即将退出～")
                break
            
            # 空输入处理
            if not user_input:
                print("输入不能为空，请重新输入！")
                continue
            
            # 调用意图识别
            intent = recognizer.recognize_intent(user_input)
            
            # 输出结果
            print("\n【意图识别结果】")
            if intent:
                print(json.dumps(intent, indent=2, ensure_ascii=False))
            else:
                print("意图识别失败，请重试或更换输入内容～")
            print("=" * 50)
    
    except Exception as e:
        print(f"程序运行异常：{str(e)}")


"""
输出client.chat.completions.create()：
{
    "choices": [
        {
            "message": {
                "role": "assistant",
                "content": {
                    "category": "笔记本电脑",
                    "intent": "商品推荐",
                    "params": "适合大学生的笔记本电脑，预算6000元左右，要轻薄、续航时间长"
                }
            },
            "finish_reason": "stop",
            "index": 0,
            "logprobs": null
        }
    ],
    "object": "chat.completion",
    "usage": {
        "prompt_tokens": 3019,
        "completion_tokens": 104,
        "total_tokens": 3123,
        "prompt_tokens_details": {
            "cached_tokens": 2048
        }
    },
    "created": 1735120033,
    "system_fingerprint": null,
    "model": "qwen-plus",
    "id": "chatcmpl-6ada9ed2-7f33-9de2-8bb0-78bd4035025a"
}
"""