import os
import unittest
import json
from src.test.test_driver import TestDSLManagerDriver, TestASTExecutorDriver
from DSLManager import DSLManager
from src.test.stubs.qwen_stub import QWENAPIStub
from src.test.stubs.dsl_stub import load_mock_dsl

def load_test_data(file_path: str) -> dict:
    """加载测试数据文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def run_unit_tests():
    """执行单元测试"""
    # 构建测试套件
    test_suite = unittest.TestSuite()
    # 添加测试用例（现代写法，兼容所有Python 3版本）
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestDSLManagerDriver))
    test_suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestASTExecutorDriver))
    # 执行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    # 返回测试结果
    return result.wasSuccessful()

def run_data_driven_tests():
    """执行数据驱动的测试（基于测试数据文件）"""
    intent_test_data = load_test_data("src/test/data/intent_test_data.json")
    dsl_manager = DSLManager()
    dsl_manager.recognizer = QWENAPIStub()
    dsl_manager.load_dsl_script = load_mock_dsl

    passed = 0
    failed = 0
    for case in intent_test_data["test_cases"]:
        user_input = case["user_input"]
        expected_intent = case["expected_intent"]
        # 执行DSL并验证意图
        result = dsl_manager.execute_dsl(user_input)
        try:
            # 简单验证：根据意图判断结果是否符合预期
            if expected_intent == "商品推荐":
                assert "推荐" in result
            elif expected_intent == "价格查询":
                assert "元" in result
            elif expected_intent == "库存查询":
                assert "库存" in result or "缺货" in result
            elif expected_intent == "自然沟通":
                assert "助手" in result
            passed += 1
        except AssertionError:
            print(f"测试失败：输入[{user_input}]，预期意图[{expected_intent}]，实际结果[{result}]")
            failed += 1

    print(f"\n数据驱动测试结果：通过{passed}个，失败{failed}个")
    return failed == 0

if __name__ == "__main__":
    print("===================== 开始执行商品回复机器人测试 ===================")
    # 执行单元测试
    print("\n1. 执行单元测试：")
    unit_test_success = run_unit_tests()
    # 执行数据驱动测试
    print("\n2. 执行数据驱动测试：")
    data_test_success = run_data_driven_tests()
    # 输出最终结果
    if unit_test_success and data_test_success:
        print("\n====================== 所有测试通过！========================")
        os._exit(0)
    else:
        print("\n====================== 部分测试失败！========================")
        os._exit(1)