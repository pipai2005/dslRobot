import ply.yacc as yacc
from .lexer import lexer, tokens
from .ast_nodes import *

# 移除全局变量，使用AST存储中间结果
precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('nonassoc', 'LE', 'GE', 'LT', 'GT', 'EQ', 'NE'),
)

def p_script(p):
    '''script : scene_stmt intent_stmt if_blocks'''
    p[0] = ScriptNode(p[1], p[2], p[3])

def p_scene_stmt(p):
    '''scene_stmt : SCENE IDENT'''
    p[0] = SceneNode(p[2])

def p_intent_stmt(p):
    '''intent_stmt : ON_INTENT IDENT'''
    valid_intents = ['商品推荐', '价格查询', '功能对比', '库存查询']
    if p[2] not in valid_intents:
        raise SyntaxError(f'不支持的意图: {p[2]}，支持的意图有: {valid_intents}')
    p[0] = IntentNode(p[2])

def p_if_blocks(p):
    '''if_blocks : if_block
                 | if_block else_if_blocks
                 | if_block else_if_blocks else_block
                 | if_block else_block'''
    if len(p) == 2:
        p[0] = IfBlocksNode(p[1])
    elif len(p) == 3 and isinstance(p[2], ElseBlockNode):
        p[0] = IfBlocksNode(p[1], else_block=p[2])
    elif len(p) == 3:
        p[0] = IfBlocksNode(p[1], else_if_blocks=p[2])
    else:
        p[0] = IfBlocksNode(p[1], p[2], p[3])

def p_else_if_blocks(p):
    '''else_if_blocks : else_if_block
                      | else_if_blocks else_if_block'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_if_block(p):
    '''if_block : IF expr REPLY STRING'''
    p[0] = IfBlockNode(p[2], p[4])

def p_else_if_block(p):
    '''else_if_block : ELSE IF expr REPLY STRING'''
    p[0] = ElseIfBlockNode(p[3], p[5])

def p_else_block(p):
    '''else_block : ELSE REPLY STRING'''
    p[0] = ElseBlockNode(p[3])

def p_expr_bin(p):
    '''expr : expr logical_op expr'''
    p[0] = BinaryOpNode(p[1], p[2], p[3])

def p_expr_group(p):
    '''expr : LPAREN expr RPAREN'''
    p[0] = p[2]

def p_expr_atom(p):
    '''expr : atom'''
    p[0] = p[1]

def p_atom_compare(p):
    '''atom : IDENT compare_op value'''
    p[0] = CompareNode(p[1], p[2], p[3])

def p_atom_exists(p):
    '''atom : IDENT'''
    p[0] = ExistsNode(p[1])

def p_value(p):
    '''value : NUMBER
             | STRING'''
    p[0] = p[1]

def p_logical_op(p):
    '''logical_op : AND 
                  | OR'''
    p[0] = p[1]

def p_compare_op(p):
    '''compare_op : LE 
                  | GE 
                  | LT 
                  | GT 
                  | EQ 
                  | NE'''
    p[0] = p[1]

def p_error(p):
    if p:
        print(f'Syntax error at token: {p.type} = "{p.value}" (line {p.lineno})')
        parser.errok()
    else:
        print('Syntax error: unexpected end of input')

parser = yacc.yacc(debug=False, write_tables=False)

def reset_parser():
    """重置解析器状态"""
    pass  # 不再需要重置全局变量