import ply.lex as lex

tokens = (
    # 关键字
    'SCENE','ON_INTENT','IF','REPLY','AND','OR','ELSE',
    # 运算符
    'LE','GE','LT','GT','EQ','NE',
    # 标识符
    'IDENT',
    # 字符串和数字
    'NUMBER','STRING',
    # 其他符号
    'LPAREN','RPAREN'
)

# 关键字表
reserved = {
    'SCENE': 'SCENE',
    'ON_INTENT': 'ON_INTENT', 
    'IF': 'IF',
    'REPLY': 'REPLY',
    'AND': 'AND',
    'OR': 'OR',
    'ELSE': 'ELSE'
}

# 正则规则
t_LE = r'<='
t_GE = r'>='
t_LT = r'<'
t_GT = r'>'
t_EQ = r'=='
t_NE = r'!='
t_LPAREN = r'\('
t_RPAREN = r'\)'

def t_IDENT(t):
    r'[a-zA-Z_\u4e00-\u9fa5][a-zA-Z0-9_\u4e00-\u9fa5]*'
    t.type = reserved.get(t.value, 'IDENT')
    return t

def t_STRING(t):
    r'\"([^\\\"]|\\.)*\"'
    t.value = t.value[1:-1]  # 去掉引号
    return t

def t_NUMBER(t):
    r'\d+\.?\d*'
    try:
        t.value = float(t.value)
    except ValueError:
        print(f"Float conversion error: {t.value}")
        t.value = 0.0
    return t

# 处理注释
def t_COMMENT(t):
    r'\#.*'
    pass  # 丢弃注释

t_ignore = ' \t\r\n'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f'Illegal character: {t.value[0]}')
    t.lexer.skip(1)

lexer = lex.lex()