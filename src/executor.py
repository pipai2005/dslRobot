from .ast_nodes import *
from typing import Dict, Union

class ASTExecutor:
    def __init__(self, symbol_table: Dict):
        self.sym_tbl = symbol_table
        self.reply = None

    def execute(self, node: ASTNode) -> Dict:
        """执行AST节点"""
        if isinstance(node, ScriptNode):
            return self._execute_script(node)
        elif isinstance(node, IfBlocksNode):
            return self._execute_if_blocks(node)
        elif isinstance(node, BinaryOpNode):
            return self._execute_binary_op(node)
        elif isinstance(node, CompareNode):
            return self._execute_compare(node)
        elif isinstance(node, ExistsNode):
            return self._execute_exists(node)
        else:
            raise ValueError(f"未知节点类型: {type(node)}")

    def _execute_script(self, node: ScriptNode) -> Dict:
        self.execute(node.if_blocks)
        return {
            'scene': node.scene.name,
            'intent': node.intent.name,
            'reply': self.reply
        }

    def _execute_if_blocks(self, node: IfBlocksNode) -> None:
        # 执行if块
        if self.execute(node.if_block.condition):
            self.reply = node.if_block.reply
            return

        # 执行else if块
        for else_if in node.else_if_blocks:
            if self.execute(else_if.condition):
                self.reply = else_if.reply
                return

        # 执行else块
        if node.else_block:
            self.reply = node.else_block.reply

    def _execute_binary_op(self, node: BinaryOpNode) -> bool:
        # left 和 right 都是ASTNode，需要递归执行, 保存着expression的值
        left_val = self.execute(node.left)
        right_val = self.execute(node.right)
        
        if node.op == 'AND':
            return left_val and right_val
        elif node.op == 'OR':
            return left_val or right_val
        return False

    def _execute_compare(self, node: CompareNode) -> bool:
        left = self.sym_tbl.get(node.ident)
        right = node.value
        
        if left is None:
            return False
            
        if node.op == '<=':
            return left <= right
        elif node.op == '>=':
            return left >= right
        elif node.op == '<':
            return left < right
        elif node.op == '>':
            return left > right
        elif node.op == '==':
            return left == right
        elif node.op == '!=':
            return left != right
        return False

    def _execute_exists(self, node: ExistsNode) -> bool:
        value = self.sym_tbl.get(node.ident)
        return value is not None and value != ""