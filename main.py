#!/usr/bin/env python3
import sys
import io
from DSLManager import DSLManager

def main():
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    print("===== 智能商品推荐系统 =====")
    print("支持：商品推荐、价格查询、库存查询、自然沟通")
    print("输入'退出'结束程序")
    print("=" * 40)
    
    dsl_manager = DSLManager()
    
    while True:
        user_input = input("\n请输入您的需求: ").strip()
        
        if user_input.lower() in ['退出', 'quit', 'exit', 'q']:
            print("感谢使用，再见！")
            break
            
        if not user_input:
            continue
            
        # 执行DSL处理流程
        result = dsl_manager.execute_dsl(user_input)
        print(f"\n【系统回复】: {result}")

if __name__ == "__main__":
    main()