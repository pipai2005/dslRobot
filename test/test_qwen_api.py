import json
from src.qwen_api import QwenAPI

def test_qwen_api():
    """
    qwen-api测试桩（作业“测试桩设计”要求：覆盖多业务场景，验证核心功能）
    测试用例包含4类场景，与DSL脚本的多业务场景需求匹配
    """
    # 1. 初始化客户端（验证配置与认证）
    try:
        client = QwenAPI()
        print("✅ qwen3-max客户端初始化成功\n")
    except Exception as e:
        print(f"❌ 客户端初始化失败：{str(e)}")
        return

    # 2. 定义测试用例（作业“多业务场景”要求：覆盖客服机器人核心应答逻辑）
    test_cases = [
        {
            "case_id": 1,
            "user_input": "推荐1500元以内的无线耳机，要主动降噪、续航20小时以上",
            "expected": {"intent": "商品推荐", "category": "无线耳机"}
        },
        {
            "case_id": 2,
            "user_input": "查询华为Mate 60 Pro的当前售价、颜色选项和库存情况",
            "expected": {"intent": "商品查询", "category": "华为Mate 60 Pro"}
        },
        {
            "case_id": 3,
            "user_input": "我上周买的小米平板开不了机，在保修期内吗？能退换吗？",
            "expected": {"intent": "售后咨询", "category": "小米平板"}
        },
        {
            "case_id": 4,
            "user_input": "你好，今天北京的天气怎么样？",
            "expected": {"intent": "其他", "category": "无"}
        }
    ]

    # 3. 执行测试用例并记录结果（作业“测试报告”素材：包含用例、结果、分析）
    test_results = []
    for case in test_cases:
        print(f"=== 测试用例{case['case_id']} ===")
        print(f"用户输入：{case['user_input']}")
        # 调用意图识别
        intent_result = client.recognize_intent(case["user_input"])
        # 验证结果
        if not intent_result:
            result = "失败（未获取到意图结果）"
            status = "❌"
        else:
            # 对比预期意图和类别（核心验证点）
            intent_match = intent_result["intent"] == case["expected"]["intent"]
            category_match = intent_result["category"] == case["expected"]["category"]
            if intent_match and category_match:
                result = "通过（意图和类别均匹配）"
                status = "✅"
            else:
                result = f"失败（意图匹配：{intent_match}，类别匹配：{category_match}）"
                status = "❌"
        # 记录结果
        test_results.append({
            "case_id": case["case_id"],
            "user_input": case["user_input"],
            "intent_result": intent_result,
            "status": status,
            "result": result
        })
        # 输出当前用例结果
        print(f"意图识别结果：\n{json.dumps(intent_result, indent=2, ensure_ascii=False) if intent_result else '无'}")
        print(f"测试结果：{status} {result}\n")

    # 4. 输出测试总结（作业“测试报告”需包含此内容）
    print("=== 测试总结 ===")
    total = len(test_results)
    passed = sum(1 for res in test_results if res["status"] == "✅")
    failed = total - passed
    print(f"总用例数：{total}，通过数：{passed}，失败数：{failed}")
    if failed > 0:
        print("失败用例ID：", [res["case_id"] for res in test_results if res["status"] == "❌"])

# 执行测试
if __name__ == "__main__":
    test_qwen_api()