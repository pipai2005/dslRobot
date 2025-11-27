code/  # 项目根目录（你的工作目录）
├── main.py  # 项目入口文件（调用DSLManager、处理用户输入输出）
├── DSLManager.py  # DSL管理器（核心业务逻辑：加载DSL、调用意图识别、执行AST）
├── run_tests.py  # 自动化测试执行脚本（批量运行单元测试+数据驱动测试）
├── generate_test_report.py  # 测试报告生成脚本（生成HTML格式测试报告）
├── myenv/  # 虚拟环境目录（你当前激活的环境）
│   ├── ...（虚拟环境相关文件，如Scripts、Lib等，无需手动修改）
├── src/  # 核心业务模块目录
│   ├── dsl/  # DSL脚本目录（真实业务用的.dsl文件）
│   │   ├── natural_chat.dsl  # 自然沟通场景DSL（示例）
│   │   ├── price_query.dsl  # 价格查询场景DSL（示例）
│   │   ├── generic_recommendation.dsl  # 商品推荐场景DSL（示例）
│   │   └── stock_query.dsl  # 库存查询场景DSL（示例）
│   ├── ast_nodes.py  # AST节点定义（如CompareNode、ExistsNode、ReplyNode等）
│   ├── executor.py  # AST执行器（解析并执行AST节点逻辑）
│   ├── lexer.py  # DSL词法分析器（将DSL脚本拆分为token）
│   ├── parser.py  # DSL语法分析器（将token解析为AST树）
│   ├── qwen_api.py  # 通义千问API封装（真实调用LLM进行意图识别）
│   └── test/  # 测试目录
│       ├── stubs/  # 测试桩目录（模拟外部依赖）
│       │   ├── qwen_stub.py  # 模拟通义千问API（避免真实调用）
│       │   └── dsl_stub.py  # 模拟DSL文件加载（避免读取真实.dsl）
│       ├── data/  # 测试数据文件目录
│       │   ├── intent_test_data.json  # 意图识别测试数据（输入+预期输出）
│       │   └── dsl_test_scripts.json  # DSL脚本测试数据（脚本内容+预期回复）
│       └── test_driver.py  # 核心测试驱动文件（单元测试用例，基于unittest）
