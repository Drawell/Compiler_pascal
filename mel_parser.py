import ply.lex as lex
import ply.yacc as yacc
import mel_ast as ast
import os
from tester import ProgTester

tokens = [

    'ANYTHING',
    'PROGBEGIN',
    'WRITELN',
    'READLN',
    'NAME',

    'FLOAT_TYPE',
    'INT_TYPE',
    'STRING_TYPE',
    'BOOL_TYPE',
    'NONE_TYPE',

    'FLOAT',
    'INT',
    'STRING',
    'BOOL',

    'PLUS',
    'MINUS',
    'DIVIDE',
    'MULTIPLY',

    'EQUALS',
    'MORE',
    'LESS',
    'AND',
    'OR',

    'ASSIGNMENT',

    'OPEN_COMMENT',
    'CLOSE_COMMENT',

    'END_LINE',
    'COMMA',
    'COLON',
    'DOT',
    'BLOCK_OPEN',
    'BLOCK_CLOSE',
    'OPEN_ROUND_BKT',
    'CLOSE_ROUND_BKT',
    'OPEN_SQUARE_BKT',
    'CLOSE_SQUARE_BKT',

    'VAR_DEF',
    'FUNC_DEF',
    'RETURN',

    'IF',
    'ELSE',
    'THEN',

    'WHILE',
    'DO',
    'FOR',
    'TO',
    'REPEAT',
    'UNTIL',

    'ARRAY',
    'OF',
    'LENGTH'

]

ident = r'[a-zA-Z_][a-zA-z_1-9]*'

t_ignore = r' '

t_ANYTHING = r'(\\.|\n)+'
t_STRING = r'"(\\.|[^"])*"'

t_PLUS = r'\+'
t_MINUS = r'\-'
t_DIVIDE = r'\/'
t_MULTIPLY = r'\*'

t_EQUALS = r'\='
t_MORE = r'\>'
t_LESS = r'\<'

t_OPEN_COMMENT = r'\(\*(\\.|[^"])*\*\)'
t_CLOSE_COMMENT = r'\(\*(\\.|[^"])*\*\)'

t_COMMA = r','
t_COLON = r':'
t_DOT = r'\.'
t_END_LINE = r';'
t_OPEN_ROUND_BKT = r'\('
t_CLOSE_ROUND_BKT = r'\)'
t_OPEN_SQUARE_BKT = r'\['
t_CLOSE_SQUARE_BKT = r'\]'


def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")

def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

def t_PROGBEGIN(t):
    r'program'
    t.type = 'PROGBEGIN'
    return t

def t_WRITELN(t):
    r'writeln'
    t.type = 'WRITELN'
    return t

def t_READLN(t):
    r'readln'
    t.type = 'READLN'
    return t

def t_BLOCK_OPEN(t):
    r'begin'
    t.type = 'BLOCK_OPEN'
    return t

def t_BLOCK_CLOSE(t):
    r'end'
    t.type = 'BLOCK_CLOSE'
    return t

def t_FUNC_DEF(t):
    r'function'
    t.type = 'FUNC_DEF'
    return t

def t_RETURN(t):
    r'return'
    t.type = 'RETURN'
    return t

def t_FLOAT_TYPE(t):
    r'real'
    t.type = 'FLOAT_TYPE'
    return t

def t_INT_TYPE(t):
    r'integer'
    t.type = 'INT_TYPE'
    return t

def t_STRING_TYPE(t):
    r'string'
    t.type = 'STRING_TYPE'
    return t

def t_BOOL_TYPE(t):
    r'boolean'
    t.type = 'BOOL_TYPE'
    return t

def t_NONE_TYPE(t):
    r'none'
    t.type = 'NONE_TYPE'
    return t

def t_VAR_DEF(t):
    r'var'
    t.type = 'VAR_DEF'
    return t

def t_AND(t):
    r'and'
    t.type = 'AND'
    return t

def t_OR(t):
    r'or'
    t.type = 'OR'
    return t

def t_IF(t):
    r'if'
    t.type = 'IF'
    return t

def t_ELSE(t):
    r'else'
    t.type = 'ELSE'
    return t

def t_THEN(t):
    r'then'
    t.type = 'THEN'
    return t

def t_WHILE(t):
    r'while'
    t.type = 'WHILE'
    return t

def t_DO(t):
    r'do'
    t.type = 'DO'
    return t

def t_FOR(t):
    r'for'
    t.type = 'FOR'
    return t

def t_TO(t):
    r'to'
    t.type = 'TO'
    return t

def t_REPEAT(t):
    r'repeat'
    t.type = 'REPEAT'
    return t

def t_UNTIL(t):
    r'until'
    t.type = 'UNTIL'
    return t

def t_ARRAY(t):
    r'array'
    t.type = 'ARRAY'
    return t

def t_OF(t):
    r'of'
    t.type = 'OF'
    return t

def t_LENGTH(t):
    r'length'
    t.type = 'LENGTH'
    return t

def t_BOOL(t):
    r'true'
    t.value = True
    t.type = 'BOOL'
    return t

def t_BOOL_f(t):
    r'false'
    t.value = False
    t.type = 'BOOL'
    return t

def t_FLOAT(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t

def t_INT(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_NAME(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = 'NAME'
    return t

def t_ASSIGNMENT(t):
    r'\:='
    t.type = 'ASSIGNMENT'
    return t

lexer = lex.lex()

precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('left', 'EQUALS', 'MORE', 'LESS'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'MULTIPLY', 'DIVIDE')

)

def p_start(p):
    '''
    start : PROGBEGIN state_list DOT
          | PROGBEGIN NAME state_list DOT
    '''

    if len(p) == 1:
        p[0] = None
    elif len(p) == 4:
        p[0] = ast.ProgramNode(ast.StateListNode(p[2]))
    elif len(p) == 5:
        p[0] = ast.ProgramNode(ast.StateListNode(p[3]), p[2])

    return p[0]

def p_state_list_begin(p):
    '''
    state_list : BLOCK_OPEN state END_LINE state_list BLOCK_CLOSE
               | BLOCK_OPEN state END_LINE BLOCK_CLOSE
    '''
    if len(p) == 6:
        p[0] = [ast.StateListNode([p[2]] + p[4])]
    elif len(p) == 5:
        p[0] = [ast.StateListNode([p[2]])]

def p_state_list(p):
    '''
    state_list : state END_LINE state_list
               | state END_LINE
    '''
    if len(p) == 4:
        p[0] = [p[1]] + p[3]
    elif len(p) == 3:
        p[0] = [p[1]]

def p_state_body(p):
    '''
    state_body : BLOCK_OPEN state_list BLOCK_CLOSE
               | state
    '''

    if len(p) == 4:
        p[0] = p[2]
    else:
        p[0] = [p[1]]

def p_state_if(p):
    '''
    state : IF expression THEN state_body
          | IF expression THEN state_body ELSE state_body
    '''

    if len(p) == 5:
        p[0] = ast.IfNode(p[2], ast.StateListNode(p[4]))
    elif len(p) == 7:
        p[0] = ast.IfNode(p[2], ast.StateListNode(p[4]), ast.StateListNode(p[6]))

def p_state_for(p):
    '''
    state : FOR NAME ASSIGNMENT expression TO expression DO state_body
    '''
    p[0] = ast.ForNode(ast.IdentNode(p[2]), p[4], p[6], ast.StateListNode(p[8]))

def p_state_while(p):
    '''
    state : WHILE expression DO state_body
    '''
    p[0] = ast.WhileNode(p[2], ast.StateListNode(p[4]))

def p_state_func_def(p):
    '''
    state : FUNC_DEF NAME OPEN_ROUND_BKT argument_list CLOSE_ROUND_BKT COLON var_type END_LINE BLOCK_OPEN state_list BLOCK_CLOSE
          | FUNC_DEF NAME OPEN_ROUND_BKT argument_list CLOSE_ROUND_BKT COLON NONE_TYPE END_LINE BLOCK_OPEN state_list BLOCK_CLOSE
          | FUNC_DEF NAME OPEN_ROUND_BKT argument_list CLOSE_ROUND_BKT COLON ARRAY OPEN_SQUARE_BKT INT DOT DOT INT CLOSE_SQUARE_BKT OF var_type END_LINE BLOCK_OPEN state_list BLOCK_CLOSE
    '''
    if len(p) == 12:
        p[0] = ast.FuncDefNode(p[2], p[4], (p[7], ), ast.StateListNode(p[10]))
    else:
        p[0] = ast.FuncDefNode(p[2], p[4], (p[15], p[9], p[12]), ast.StateListNode(p[18]))

def p_argument_list(p):
    '''
    argument_list : NAME COLON var_type COMMA argument_list
                  | NAME COLON var_type
                  | NAME COLON ARRAY OPEN_SQUARE_BKT INT DOT DOT INT CLOSE_SQUARE_BKT OF var_type COMMA argument_list
                  | NAME COLON ARRAY OPEN_SQUARE_BKT INT DOT DOT INT CLOSE_SQUARE_BKT OF var_type
                  | empty
    '''
    if len(p) == 4:
        p[0] = [ast.Param(p[1], p[3])]
    elif len(p) == 6:
        p[0] = [ast.Param(p[1], p[3])] + p[5]
    elif len(p) == 12:
        p[0] = [ast.ParamArray(p[1], p[11], p[5], p[8])]
    elif len(p) == 14:
        p[0] = [ast.ParamArray(p[1], p[11], p[5], p[8])] + p[5]

def p_state_return(p):
    '''
    state : RETURN expression
    state : RETURN
    '''
    if len(p) == 3:
        p[0] = ast.ReturnNode(p[2])
    else:
        p[0] = ast.ReturnNode(ast.IntNode(0))

def p_state_var_def(p):
    '''
    state : VAR_DEF NAME COLON var_type
    state_var_def : VAR_DEF NAME COLON var_type
    '''
    p[0] = ast.VarDefNode(p[2], p[4])

def p_state_array_def(p):
    '''
    state : VAR_DEF NAME COLON ARRAY OPEN_SQUARE_BKT INT DOT DOT INT CLOSE_SQUARE_BKT OF var_type
    state_array_def : VAR_DEF NAME COLON ARRAY OPEN_SQUARE_BKT INT DOT DOT INT CLOSE_SQUARE_BKT OF var_type
    '''
    #| VAR_DEF NAME COLON ARRAY OPEN_SQUARE_BKT INT DOT DOT INT CLOSE_SQUARE_BKT OF var_type ASSIGNMENT OPEN_ROUND_BKT expr_list CLOSE_ROUND_BKT

    if len(p) == 13:
        p[0] = ast.ArrayDefNode(p[2], p[6], p[9], p[12])
    else:
        p[0] = ast.ArrayDefNode(p[2], p[6], p[9], p[12], p[15])

def p_state_writeln(p):
    '''
    state : WRITELN OPEN_ROUND_BKT expression CLOSE_ROUND_BKT
    '''
    p[0] = ast.WritelnNode(p[3])

def p_state_readln(p):
    '''
    state : READLN OPEN_ROUND_BKT NAME CLOSE_ROUND_BKT
    '''

    p[0] = ast.ReadlnNode(ast.IdentNode(p[3]))

'''
def p_state_readln(p):
    ''
    state : READLN OPEN_ROUND_BKT expression_array_call CLOSE_ROUND_BKT
    ''
    p[0] = ast.ReadlnNode(ast.IdentNode(p[3]))
'''

def p_state_var_assign(p):
    '''
    state : expression_name ASSIGNMENT expression
          | expression_array_call ASSIGNMENT expression
    '''
    if len(p) == 4:
        p[0] = ast.AssignNode(p[1], p[3])

def p_state_var_assign_def(p):
    '''
    state : state_var_def ASSIGNMENT expression
          | state_array_def ASSIGNMENT OPEN_ROUND_BKT expr_list CLOSE_ROUND_BKT
          | expression_name ASSIGNMENT OPEN_ROUND_BKT expr_list CLOSE_ROUND_BKT
    '''
    if len(p) == 4:
        p[0] = ast.AssignNode(p[1], p[3])
    elif len(p) == 6:
        p[0] = ast.AssignNode(p[1], ast.ExprListNode(p[4]))

def p_state_expression(p):
    '''
    state : expression
    '''
    p[0] = p[1]

def p_expr_list(p):
    '''
    expr_list : expression COMMA expr_list
              | expression
    '''
    if len(p) == 2:
        p[0] = [p[1]]
    elif len(p) == 4:
        p[0] = [p[1]] + p[3]

def p_expr_list_empty(p):
    '''
    expr_list : empty
    '''

def p_expression_func_call(p):
    '''
    expression : NAME OPEN_ROUND_BKT expr_list CLOSE_ROUND_BKT
    '''
    p[0] = ast.FuncCallNode(p[1], p[3])

def p_expression_array_call(p):
    '''
    expression : NAME OPEN_SQUARE_BKT expression CLOSE_SQUARE_BKT
    expression_array_call : NAME OPEN_SQUARE_BKT expression CLOSE_SQUARE_BKT
    '''
    p[0] = ast.ArrayCallNode(ast.IdentNode(p[1]), p[3])

def p_expression_math(p):
    '''
    expression : expression MULTIPLY expression
               | expression DIVIDE expression
               | expression PLUS expression
               | expression MINUS expression
    '''
    p[0] = ast.MathBinOpNode(p[2], p[1], p[3])

def p_expression_logic(p):
    '''
    expression : expression EQUALS expression
               | expression MORE expression
               | expression LESS expression
               | expression AND expression
               | expression OR expression
    '''
    p[0] = ast.LogicBinOpNode(p[2], p[1], p[3])

def p_expression_int(p):
    '''
    expression : INT
    '''
    p[0] = ast.IntNode(p[1])

def p_expression_float(p):
    '''
    expression : FLOAT
    '''
    p[0] = ast.FloatNode(p[1])

def p_expression_bool(p):
    '''
    expression : BOOL
    '''
    p[0] = ast.BoolNode(p[1])

def p_expression_length(p):
    '''
    expression : expression_name DOT LENGTH
    '''
    p[0] = ast.LengthNode(p[1])

def p_expression_string(p):
    '''
    expression : STRING
    '''
    p[0] = ast.StringNode(p[1])

def p_expression_name(p):
    '''
    expression : NAME
    expression_name : NAME
    '''
    p[0] = ast.IdentNode(p[1])


def p_var_type(p):
    '''
    var_type : FLOAT_TYPE
             | INT_TYPE
             | STRING_TYPE
             | BOOL_TYPE
    '''
    if len(p) == 2:
        p[0] = p[1]
    #else:


def p_empty(p):
    '''
    empty :
    '''
    p[0] = None

def p_error(p):
    if (p != None):
        print("Syntax error ", p.value)
        return "error", p
    else:
        print("Syntax error")
        return "error", None

def lexer_input(s):
    lexer.input(s)
    while True:
        tok = lexer.token()  # читаем следующий токен
        if not tok: break  # закончились печеньки
        print(tok)

s ='''
program tmp   
    function sort_str(arr: array[1..5] of string): none;
    begin
        var flag: boolean := true;        
        while flag do
        begin
            var i: integer;
            flag := false;
            for i:= 1 to arr.length - 1 do
            begin
                if arr[i] < arr[i + 1] then
                begin
                    var tmp: string := arr[i];
                    arr[i] := arr[i + 1];
                    arr[i + 1] := tmp;
                    flag := true;
                end;    
            end;
        end;                
    end;    
begin
    var a: integer := 0;
    var s: string := "hi";
    var as: array[1..5] of string;
    
    var i: integer;
    for i := 1 to 5 do
    begin
        readln(s);
        as[i] := s;
    end;
    
    sort_str(as);
    
    for i := 1 to 5 do
        writeln("\n" + as[i]);
        
end.
'''


'''

    if b or b and b then
        writeln("YEEEE");
program tmp
    function func(a: integer): integer;
    begin
        if a>3 then 
            return 9
        else
            return 0;
    end;  

begin
    var a: integer := 3;
    writeln(func(3));    
    
end.
'''






'''
    function f1(): none;
    begin
        writeln("hello\n");
    end;
    
    function f2(a: integer, b: integer): integer;
    begin
        return a + b;
    end;
        
    function f3(a: real, b: integer): real;
    begin
        return a + b;
    end;
    
    function f4(a: boolean, b: boolean): boolean;
    begin
        return a;
    end;
    
    function f5(a: string, b: string): string;
    begin
        return a + b;
    end;
    
    function f6(a: array[1..2] of string): array[1..2] of string;
    begin
        var tmp: string := a[1]; 
        a[1] := a[2];
        a[2] := tmp; 
        var i: integer;            
        for i := 1 to 2 do
            writeln("\n" + a[i]);
        return a;
    end;  


    f1();:= ("one", "two");
    a := f2(a, a);
    writeln(a);
    c := f3(c, a);
    writeln(c);
    b := f4(b, b);    
    s := f5(s, s);
    as := f6(as);
'''

'''

    

    
    begin
        var a: integer := 2;
        var c: real := 5;
        var b: boolean := true;
        var s: string := "hi";
        var as: array[1..2] of string := ("one", "two");
        f1();
        a := f2(a, a);
        c := f3(c, a);
        b := f4(b, b);
        s := f5(s, s);
        as := f6(as);
    end.

'''




'''
program tmp
var arr: array[1..3] of integer := (1, 2, 3);
begin
    var a: integer := 2;
    while a < 5 do
    begin
        writeln("\n");
        writeln(a);
        a := a + 1;
    end;
end.
'''

'''
program tmp
var arr: array[1..3] of integer := (1, 2, 3);
begin
    var t: array[1..5] of integer;
    var a: integer := 2;
    var b: integer := 0;
    var c: boolean := true;
    var d: boolean := false;
    
    if t.length > arr.length then
        writeln("YES")
    else
        writeln("NO!");
        
end.'''


'''program
    var res: real;
    function func(a: real): none;
    begin
        var i: integer;
        var j: integer;
        i := 1;
        j := 2;
        if j > a then
        begin
            var q: real;
            var w: real;
            q := 1;
            w := 2.2;
        end;
    end;
    begin
        var c: integer;
        func(c);
        var i: integer := 3;
        var j: integer;
        j := 2;
        if j > res then
        begin
            var q: real;
            var w: real;
            q := 1;
            w := 2.2;
        end;
    end.'''

#lexer_input(s)
parser = yacc.yacc()


def run_test():
    tester = ProgTester()
    test_errors = tester.run_test(parser)  # тестики по заветам Андрея)
    if test_errors is not None:
        for error in test_errors:
            print(error)


def code_generate(file_path):
    s = ''
    with open(file_path, 'r', encoding='utf-8') as file:
        s = file.read()

    a = parser.parse(s)
    error = a.semantic_analysis(None)
    #print(*a.tree1, sep=os.linesep)
    #print('OK!', error)
    code = []
    a.generate_code(code, [])
    no_indent = ['.meth', '.fiel', '.clas', '.supe', '.end ', '.sour', 'LABEL']
    with open(file_path + '.j', "tw", encoding='utf-8') as file:
        for s in code:
            if len(s) > 5 and s[0:5] in no_indent:
                file.write(s + '\n')
            else:
                file.write('   ' + s + '\n')
def main():
    s = '''    
program tmp   
    function func(arr: array[1..10] of integer): none;
    begin
        var flag_write: boolean := false;
        var flag_con: boolean := true;
        var i: integer := 1;
        
        for i := 1 to 10 do
        begin       
            if arr[i] = 0 then
            begin
                if flag_write then
                    return;
            
                flag_write := true;              
            end
            else
                writeln("\n" + arr[i]);
        end;   
    end;    
    
begin
    var a: integer := 0;
    var ar: array[1..10] of integer;
    
    var i: integer;
    for i := 1 to 10 do
    begin
        readln(a);
        ar[i] := a;
    end;
    
    func(ar);
        
end.
    '''
    a = parser.parse(s)
    error = a.semantic_analysis(None)
    #print(*a.tree1, sep=os.linesep)
    #print('OK!', error)
    file_name = r'C:\Users\HP\Desktop\JBC\tmp'
    code = []
    a.generate_code(code, [])
    no_indent = ['.meth', '.fiel', '.clas', '.supe', '.end ', '.sour', 'LABEL']
    with open(file_name + '.j', "tw", encoding='utf-8') as file:
        for s in code:
            if len(s) > 5 and s[0:5] in no_indent:
                file.write(s + '\n')
            else:
                file.write('   ' + s + '\n')
if __name__ == '__main__':
    main();