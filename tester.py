from typing import List
import mel_ast as ast
import vartypes as vt


tests = {
    'test_writeln_1':
    '''
    program
    var c: integer;
    begin
        var a: integer;
        c:=4.2;
        a:=c;
        writeln(a);
    end.''',

    'test_for_1':
    '''
    program
    begin
        var a: integer;
        for a := 1 to 3 do
        begin
            var b: integer;
            writeln(a+b);
        end;
    end.''',

    'test_for_2':
    '''
    program
    begin
        var a: integer;
        for a := 1 to 3 do
            writeln(a);
    end.''',

    'test_while_1':
    '''
    program
    begin
        var a: integer;
        a:=0;
        while a < 5 do
            a := a + 1;
    end.
    ''',

    'test_while_2':
    '''
    program
    begin
        var a: integer;
        a:=0;
        while a < 5 do
        begin
            a := a + 1;
        end;
    end.
    ''',

    'test_if_1':
    '''
    program
    begin
        var b: integer;
        var a: integer;
        b:=4;
        a:=5;

        if a < b then
            writeln(b);

    end.
    ''',

    'test_if_2':
    '''
    program
    begin
        var b: integer;
        var a: integer;
        b:=4;
        a:=5;

        if a < b then
        begin
            writeln(b);
        end;
    end.
    ''',

    'test_if_else_1':
    '''
    program
    begin
        var b: integer;
        var a: integer;
        b:=4;
        a:=5;

        if a < b then
            writeln(b)
        else
            writeln(a);
    end.
    ''',

    'test_if_else_2':
    '''
    program
    begin
     var b: integer;
     var a: integer;
     b:=4;
     a:=5;

     if a < b then
     begin
         writeln(b);
     end
     else
         writeln(a);
    end.
    ''',

    'test_if_else_3':
    '''
    program
    begin
     var b: integer;
     var a: integer;
     b:=4;
     a:=5;

     if a < b then
         writeln(b)
     else
     begin
         writeln(a);
     end;
    end.
    ''',

    'test_if_else_4':
    '''
    program
    begin
        var b: integer;
        var a: integer;
        b:=4;
        a:=5;

        if a < b then
        begin
            writeln(b);
        end
        else
        begin
            writeln(a);
        end;
    end.
    ''',

    'test_func_1':
    '''
    program
    function Add(a:integer, b:integer): integer;
    begin
        var c: integer;
        c := a + b;
        return a;
    end;
    begin
        var x: integer;
        var y: integer;
        var z: integer;
        x := 1;
        y := 2;
        z := Add(x, y);
    end.
    ''',

    'test_func_2':
    '''
    program

    function print_hello(): none;
    begin
        writeln("hello");
    end;
    begin
        print_hello();
    end.
    ''',

    'test_array_1':
    '''
    program
    var a: array [1..5] of integer;
    begin
        a[1] := 1;
    end.
    ''',

    'test_array_2':
    '''
    program
    var a: array [1..3] of integer := (1, 2, 3);
    begin
        var i: integer;
        i := 3;
        a[3] := 5;
    end.
    ''',

    'test_array_3':
    '''
    program
    var a: array [1..3] of real := (1, 2, 3);
    begin
     var i: integer;
     i := 1;
     a[1] := a[i];
    end.
    ''',

    'test_func_array_1':
    '''program
        var res: real;
        function print_array(a: array [1..2] of integer): none;
        begin
            var i: integer;
            for i := 1 to 2 do
                writeln(a[i]);
        end;
        begin
            var c: array [1..2] of integer := (3, 4);
            print_array(c);
        end.
    '''

}


def sem_check_test_writeln_1(p: ast.ProgramNode)->List[int]:
    '''program
    var c: integer;
    begin
        var a: integer;
        c:=4.2;
        a:=c;
        writeln(a);
    end.'''

    result = []
    message = p.semantic_analysis(None)
    if 'error' in message:
        result.append(1)

    state_list = p.body[1]
    if type(state_list[1].expr) is not ast.CastNode:
        result.append(2)
    if state_list[1].expr.const_val != 4:
        result.append(3)
    if state_list[2].var.index != 1:
        result.append(4)
    if state_list[2].expr.index != 0:
        result.append(5)
    if type(state_list[3]) is not ast.WritelnNode:
        result.append(6)
    if type(state_list[3].expr) is not ast.CastNode:
        result.append(7)

    return result if len(result) != 0 else None

def sem_check_test_for_1(p: ast.ProgramNode)->List[int]:
    '''program
    begin
        var a: integer;
        for a := 1 to 3 do
        begin
            var b: integer;
            writeln(a+b);
        end;
    end.'''

    result = []
    message = p.semantic_analysis(None)
    if 'error' in message:
        result.append(1)

    state_list = p.body[0]
    if type(state_list[1]) is not ast.ForNode:
        result.append(2)
    if state_list[1].var.name != 'a':
        result.append(3)
    if state_list[1].start_value.const_val != 1:
        result.append(4)
    if state_list[1].end_value.const_val != 3:
        result.append(5)

    writeln_node = state_list[1].loop_body[1]
    if type(writeln_node.expr) is not ast.CastNode:
        result.append(6)

    a = writeln_node.expr.node.arg1
    if a.var_type != vt.VarType.GLOBAL:
        result.append(7)
    if a.index != 0:
        result.append(8)
    b = writeln_node.expr.node.arg2
    if b.var_type != vt.VarType.GLOBAL:
        result.append(9)
    if b.index != 1:
        result.append(10)



    return result if len(result) != 0 else None

def sem_check_test_for_2(p: ast.ProgramNode)->List[int]:
    '''program
    begin
        var a: integer;
        for a := 1 to 3 do
            writeln(a);
    end.'''
    result = []
    message = p.semantic_analysis(None)
    if 'error' in message:
        result.append(1)

    return result if len(result) != 0 else None

def sem_check_test_while_1(p: ast.ProgramNode)->List[int]:
    '''program
    begin
        var a: integer;
        a:=0;
        while a < 5 do
            a := a + 1;
    end.'''

    result = []
    message = p.semantic_analysis(None)
    if 'error' in message:
        result.append(1)
    return result if len(result) != 0 else None

def sem_check_test_while_2(p: ast.ProgramNode)->List[int]:
    result = []
    message = p.semantic_analysis(None)
    if 'error' in message:
        result.append(1)
    return result if len(result) != 0 else None

def sem_check_test_if_1(p: ast.ProgramNode)->List[int]:
    '''program
    begin
        var b: integer;
        var a: integer;
        b:=4;
        a:=5;

        if a < b then
            writeln(b);
    end.'''
    result = []
    message = p.semantic_analysis(None)
    if 'error' in message:
        result.append(1)
    return result if len(result) != 0 else None

def sem_check_test_if_2(p: ast.ProgramNode)->List[int]:
    result = []
    message = p.semantic_analysis(None)
    if 'error' in message:
        result.append(1)
    return result if len(result) != 0 else None

def sem_check_test_if_else_1(p: ast.ProgramNode)->List[int]:
    result = []
    message = p.semantic_analysis(None)
    if 'error' in message:
        result.append(1)
    return result if len(result) != 0 else None

def sem_check_test_if_else_2(p: ast.ProgramNode)->List[int]:
    result = []
    message = p.semantic_analysis(None)
    if 'error' in message:
        result.append(1)
    return result if len(result) != 0 else None

def sem_check_test_if_else_3(p: ast.ProgramNode)->List[int]:
    result = []
    message = p.semantic_analysis(None)
    if 'error' in message:
        result.append(1)
    return result if len(result) != 0 else None

def sem_check_test_if_else_4(p: ast.ProgramNode)->List[int]:
    result = []
    message = p.semantic_analysis(None)
    if 'error' in message:
        result.append(1)
    return result if len(result) != 0 else None

def sem_check_test_func_1(p: ast.ProgramNode)->List[int]:
    '''program
    function Add(a:integer, b:integer): integer;
    begin
        var c: integer;
        c := a + b;
        return a;
    end;
    begin
        var x: integer;
        var y: integer;
        var z: integer;
        x := 1;
        y := 2;
        z := Add(x, y);
    end.'''

    result = []
    message = p.semantic_analysis(None)
    if 'error' in message:
        result.append(1)
    return result if len(result) != 0 else None

def sem_check_test_func_2(p: ast.ProgramNode)->List[int]:
    '''program

    function print_hello(): none;
    begin
        writeln("hello");
    end;
    begin
        print_hello();
    end.'''
    result = []
    message = p.semantic_analysis(None)
    if 'error' in message:
        result.append(1)
    return result if len(result) != 0 else None

def sem_check_test_array_1(p: ast.ProgramNode)->List[int]:
    '''
    program
    var a: array [1..5] of integer;
    begin
        a[1] := 1;
    end.
    '''
    result = []
    message = p.semantic_analysis(None)
    if 'error' in message:
        result.append(1)
    return result if len(result) != 0 else None

def sem_check_test_array_2(p: ast.ProgramNode)->List[int]:
    '''program
    var a: array [1..3] of integer := (1, 2, 3);
    begin
        a[ 1 ] := 1;
    end.'''
    result = []
    message = p.semantic_analysis(None)
    if 'error' in message:
        result.append(1)
    return result if len(result) != 0 else None

def sem_check_test_array_3(p: ast.ProgramNode)->List[int]:
    '''program
    var a: array [1..3] of real := (1, 2, 3);
    begin
        var i: integer;
        i := 1;
        a[ 1 ] := a[ i ];
    end.'''
    result = []
    message = p.semantic_analysis(None)
    if 'error' in message:
        result.append(1)
    return result if len(result) != 0 else None

def sem_check_test_func_array_1(p: ast.ProgramNode)->List[int]:
    '''program
    var res: real;
    function print_array(a: array [1..2] of integer): none;
    begin
        var i: integer;
        for i := 1 to 2 do
            writeln(a[i]);
    end;
    begin
        var c: array [1..2] of integer := (3, 4);
        print_array(c);
    end.'''
    result = []
    message = p.semantic_analysis(None)
    if 'error' in message:
        result.append(1)

    func_body = p.body[1].body
    for_node = func_body[1]
    if for_node.var.var_type != vt.VarType.LOCAL:
        result.append(2)

    a_i = for_node.loop_body[0].expr.node
    if a_i.data_type != vt.DataTypeEnum.int:
        result.append(3)
    if a_i.arr.var_type != vt.VarType.PARAM:
        result.append(4)
    if a_i.arr_index.data_type != vt.DataTypeEnum.int:
        result.append(5)
    if a_i.arr_index.var_type != vt.VarType.LOCAL:
        result.append(6)

    state_list = p.body[2]
    var_c = state_list[1].params[0]
    if var_c.var_type != vt.VarType.GLOBAL:
        result.append(7)
    if var_c.index != 1:
        result.append(8)

    return result if len(result) != 0 else None


class ProgTester:
    def __init__(self):
        self.func_dict = {}
        self.fill_func_list()

    def run_test(self, parser):
        errors_log = []
        for key in tests.keys():
            p = parser.parse(tests[key])
            if p is None:
                errors_log.append("lex error in test " + key)
            elif key in self.func_dict:
                try:
                    l = self.func_dict[key](p)
                    if l is not None:
                        errors_log.append("semantic error in test " + key + ' in tests: ' + str(l))
                except all:
                    errors_log.append("semantic except error in test " + key)

        if len(errors_log) == 0:
            return None
        else:
            return errors_log

    def fill_func_list(self):
        self.func_dict['test_writeln_1']    = sem_check_test_writeln_1
        self.func_dict['test_for_1']        = sem_check_test_for_1
        self.func_dict['test_for_2']        = sem_check_test_for_2
        self.func_dict['test_while_1']      = sem_check_test_while_1
        self.func_dict['test_while_2']      = sem_check_test_while_2
        self.func_dict['test_if_1']         = sem_check_test_if_1
        self.func_dict['test_if_2']         = sem_check_test_if_2
        self.func_dict['test_if_else_1']    = sem_check_test_if_else_1
        self.func_dict['test_if_else_2']    = sem_check_test_if_else_2
        self.func_dict['test_if_else_3']    = sem_check_test_if_else_3
        self.func_dict['test_if_else_4']    = sem_check_test_if_else_4
        self.func_dict['test_func_1']       = sem_check_test_func_1
        self.func_dict['test_func_2']       = sem_check_test_func_2
        self.func_dict['test_array_1']      = sem_check_test_array_1
        self.func_dict['test_array_2']      = sem_check_test_array_2
        self.func_dict['test_array_3']      = sem_check_test_array_3
        self.func_dict['test_func_array_1'] = sem_check_test_func_array_1
