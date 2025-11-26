from typing import List, Optional, Union

class ASTNode:
    """AST节点基类"""
    pass

class SceneNode(ASTNode):
    def __init__(self, name: str):
        self.name = name

class IntentNode(ASTNode):
    def __init__(self, name: str):
        self.name = name

class IfBlockNode(ASTNode):
    def __init__(self, condition: ASTNode, reply: str):
        self.condition = condition
        self.reply = reply

class ElseIfBlockNode(ASTNode):
    def __init__(self, condition: ASTNode, reply: str):
        self.condition = condition
        self.reply = reply

class ElseBlockNode(ASTNode):
    def __init__(self, reply: str):
        self.reply = reply

class IfBlocksNode(ASTNode):
    def __init__(self, if_block: IfBlockNode, 
                 else_if_blocks: List[ElseIfBlockNode] = None,
                 else_block: Optional[ElseBlockNode] = None):
        self.if_block = if_block
        self.else_if_blocks = else_if_blocks or []
        self.else_block = else_block

class BinaryOpNode(ASTNode):
    def __init__(self, left: ASTNode, op: str, right: ASTNode):
        self.left = left
        self.op = op
        self.right = right

class CompareNode(ASTNode):
    def __init__(self, ident: str, op: str, value: Union[str, int, float]):
        self.ident = ident
        self.op = op
        self.value = value

class ExistsNode(ASTNode):
    def __init__(self, ident: str):
        self.ident = ident

class ScriptNode(ASTNode):
    def __init__(self, scene: SceneNode, intent: IntentNode, if_blocks: IfBlocksNode):
        self.scene = scene
        self.intent = intent
        self.if_blocks = if_blocks