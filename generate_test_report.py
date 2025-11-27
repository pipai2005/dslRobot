import os
import datetime
import unittest
from htmltestrunner import HTMLTestRunner

# 定义测试报告保存路径
report_dir = "src/test/reports"
if not os.path.exists(report_dir):
    os.makedirs(report_dir)

# 生成报告文件名
report_name = f"test_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
report_path = os.path.join(report_dir, report_name)

# 构建测试套件
test_suite = unittest.TestLoader().discover("src/test", pattern="test_driver.py")

# 执行测试并生成HTML报告
with open(report_path, 'wb') as f:
    runner = HTMLTestRunner(
        stream=f,
        title="商品回复机器人测试报告",
        description="测试DSL解释器、意图识别、AST执行等核心模块"
    )
    runner.run(test_suite)

print(f"测试报告已生成：{report_path}")