from abc import ABC, abstractmethod
from typing import Callable, Tuple, List, Union
from enum import Enum
from vartypes import VarType, DataType, ArrayDataType, ValListDataType
from vartypes import DataTypeEnum as dte
from context import Context, GeneralContext, VarDescription, FuncDescription
from bytecode_instructors import JBC_instructor as JBCI
import typecaster as tc

CHAR1 = '├'
CHAR2 = '│'
CHAR3 = '└'

# leaf возвращает информацию о себе {value, type, const}, либо ошибку
# NOT leaf возвращет None, либо ошибку


class AstNode(ABC):

    @property
    def childs(self) -> Tuple['AstNode', ...]:
        return ()

    @property
    def tree1(self) -> [str, ...]:
        res = [str(self)]
        if type(self.childs) != tuple:
            print(str(self))
        childs_temp = self.childs

        for i, child in enumerate(childs_temp):
            ch0, ch = '├', '│'
            if i == len(childs_temp) - 1:
                ch0, ch = '└', ' '
            res.extend(((ch0 if j == 0 else ch) + ' ' + s for j, s in enumerate(child.tree1)))
        return res

    @abstractmethod
    def __str__(self)->str:
        pass

    def tree(self, addition: str)->str:
        return str(self)

    @abstractmethod
    def semantic_analysis(self, context: Context)->dict:
        pass

    @abstractmethod
    def generate_code(self, code: List[str], label_count: List[int]):
        pass

    @abstractmethod
    def run(self):
        pass


class ValueNode(AstNode):  # leaf or NOT leaf
    def __init__(self, value, data_type: DataType=None):
        super().__init__()
        self.value = value
        self.data_type = data_type
        self.const_val = None

    def __str__(self)->str:
        return str(self.value) + ':' + str(self.data_type)

    def semantic_analysis(self, context: Context)->dict:  # выполняется только для литералов
        if self.value is not None:
            self.const_val = self.value
        return {}

    def get_value(self):
        return self.value

    def set_value(self, value):
        self.value = value

    def generate_code(self, code: List[str], label_count: List[int]):
        code.append('ldc                   %s' % self.value)

    def run(self):
        return self.value


class CastNode(ValueNode):
    def __init__(self, caster: tc.TypeCaster, node: ValueNode, value=None):
        super().__init__(value, caster.get_type())
        self.caster = caster
        self.node = node
        if node.const_val is not None:
            self.const_val = self.caster.cast_in_real_time(node.const_val, self.node.data_type)

    @property
    def childs(self):
        return self.node, #self.node.childs

    def __str__(self)->str:
        return 'CastTo_' + str(self.data_type) + ('| const_val = ' + str(self.const_val) if self.const_val else '')
        # + '[' + str(self.node) + ']'

    def semantic_analysis(self, context: Context)->dict:
        return {}

    def generate_code(self, code: List[str], label_count: List[int]):
        if self.const_val is not None:
            code.append('ldc                   %s' % self.const_val)
            return
        else:
            self.node.generate_code(code, label_count)

        command = JBCI.get_cast_command(self.node.data_type, self.data_type)
        if command is not None:
            code.append(command)

    def run(self):
        pass


class ExprListNode(ValueNode):
    def __init__(self, values: List[ValueNode]):
        super().__init__(values, ValListDataType(dte.none, len(values)))

        #for i, val in enumerate(self.value):
        #    if val.data_type != self.data_type:
        #        self.value[i] = CastNode(tc.get_caster(self.data_type.dte), self.value[i], self.value[i].value)

    @property
    def childs(self):
        return tuple(self.value)

    def __str__(self) -> str:
        return 'expr_list ' + str(self.data_type)

    def semantic_analysis(self, context: Context) -> dict:
        for i, val in enumerate(self.value):
            messege = val.semantic_analysis(context)
            if 'error' in messege.keys():
                return messege

            if self.data_type.dte != val.data_type:
                if not val.data_type.can_casted_to(self.data_type.dte):
                    return {'error': 'can not cast ' + str(val.data_type) + ' to ' + str(self.data_type) +
                            'in pos ' + str(i)}
                caster = tc.get_caster(self.data_type.dte)
                self.value[i] = CastNode(caster, self.value[i])

        return {}

    def generate_code(self, code: List[str], label_count: List[int]):
        code.append('ldc                   %s' % self.data_type.length)
        if self.data_type.dte == dte.string:
            code.append('anewarray              %s' % JBCI.get_type_full(self.data_type.dte))
        else:
            code.append('newarray              %s' % JBCI.get_type_full(self.data_type.dte))

        for i, val in enumerate(self.value):
            code.append('dup')
            code.append('ldc                   %s' % i)  # idx
            val.generate_code(code, label_count)  # value
            code.append('%sastore               ' % JBCI.get_type_dte_lower(self.data_type.dte))

    def run(self):
        pass


class IntNode(ValueNode):  # leaf
    def __init__(self, value: int):
        super().__init__(value, DataType(dte.int))


class FloatNode(ValueNode):  # leaf
    def __init__(self, value: float):
        super().__init__(value, DataType(dte.float))


class BoolNode(ValueNode):  # leaf
    def __init__(self, value: bool):
        super().__init__(value, DataType(dte.bool))

    def generate_code(self, code: List[str], label_count: List[int]):
        if self.value:
            code.append('iconst_1')
        else:
            code.append('iconst_0')


class StringNode(ValueNode):
    def __init__(self, value: float):
        super().__init__(value, DataType(dte.string))

    def generate_code(self, code: List[str], label_count: List[int]):
        self.value = self.value.replace('\n', r'\012')
        code.append('ldc                   %s' % self.value)

class IdentNode(ValueNode):  # leaf
    def __init__(self, name: str, data_type: DataType=None):
        super().__init__(None, data_type)
        self.name = name
        self.var_type = VarType.NONE
        self.index = -1
        self.prog_name = 'prog'

    def __str__(self)->str:
        return self.name + '(' + str(self.index) + ', ' +  \
                str(self.data_type) + ', ' + str(self.var_type.value) + ')'

    def semantic_analysis(self, context: Context)->dict:
        var_dis = context.get_var(self.name)
        if var_dis is None:
            return {'error': 'Var is not defined: ' + self.name + ';\n'}
        else:
            self.get_description(var_dis)
            self.prog_name = context.general_context.get_prog_name()
            return {}

    def get_description(self, description: VarDescription):
        self.data_type = description.data_type
        self.var_type = description.var_type
        self.index = description.index

    def generate_code(self, code: List[str], label_count: List[int], get: bool=True):
        if self.var_type == VarType.GLOBAL:
            s = '%s/%s %s' % (self.prog_name, self.name, JBCI.get_type(self.data_type))
            if get:
                code.append('getstatic             %s' % s)
            else:
                code.append('putstatic             %s' % s)
            return

        if type(self.data_type) is ArrayDataType or self.data_type == dte.string:
            if get:
                code.append('aload                 %s' % self.index)
            else:
                code.append('astore                %s' % self.index)
            return

        if get:
            code.append('%sload                 %s' % (JBCI.get_type_lower(self.data_type), self.index))
        else:
            code.append('%sstore                %s' % (JBCI.get_type_lower(self.data_type), self.index))

    def run(self):
        pass


class LengthNode(ValueNode):
    def __init__(self, var: IdentNode):
        super().__init__(None, DataType(dte.string))
        self.var = var
        self.data_type = DataType(dte.int)

    @property
    def childs(self):
        return self.var,

    def __str__(self) -> str:
        return 'length'

    def semantic_analysis(self, context: Context) -> dict:
        message = self.var.semantic_analysis(context)
        if 'error' in message:
            return message

        if type(self.var.data_type) is ArrayDataType:
            self.const_val = self.var.data_type.length

        return {}

    def generate_code(self, code: List[str], label_count: List[int]):
        self.var.generate_code(code, label_count)
        if type(self.var.data_type) is ArrayDataType:
            code.append('arraylength')
        elif self.var.data_type.dte == dte.string:
            code.append('invokevirtual         java/lang/String/length()I')
        else:
            code.append('iconst_1')


class VarDefNode(AstNode):
    def __init__(self, name: str, data_type: str):
        super().__init__()
        self.name = name
        self.data_type = DataType(data_type)

    def __str__(self)->str:
        return 'var ' + str(self.name) + ': ' + str(self.data_type)

    def semantic_analysis(self, context: Context)->dict:
        # если текущий контекст глобальный или его родитель, т.е. переменные в основном коде программы глобальные
        var_type = VarType.GLOBAL if context.is_global else VarType.LOCAL

        s = context.add_var(self.name, self.data_type, var_type)
        if s is not None:
            return {'error': s + ': ' + self.name + ';\n'}
        return {}

    def generate_code(self, code: List[str], label_count: List[int]):
        pass

    def run(self):
        pass


class AssignNode(AstNode):   # NOT leaf
    def __init__(self, var: IdentNode, expr: ValueNode):
        super().__init__()
        self.var = var
        self.expr = expr

    @property
    def childs(self):
        return self.var, self.expr

    def __str__(self) -> str:
        return ':='#str(self.var) + ' := ' + str(self.expr)

    def semantic_analysis(self, context: Context)->dict:
        message1 = self.var.semantic_analysis(context)  # assignment

        #КОСТЫЛЬ!
        if type(self.expr) is ExprListNode:
            self.expr.data_type.dte = self.var.data_type.dte

        message2 = self.expr.semantic_analysis(context)  # assignment

        if 'error' in message1.keys():
            return message1
        elif 'error' in message2.keys():
            return message2

        # мб лучше запихать в VarDefNode
        if type(self.var) is VarDefNode or type(self.var) is ArrayDefNode:
            self.var = IdentNode(self.var.name, self.var.data_type)
            self.var.semantic_analysis(context)

        if self.var.data_type != self.expr.data_type:
            if not self.expr.data_type.can_casted_to(self.var.data_type):
                return {'error': 'can not cast ' + str(self.expr.data_type) + ' to ' + str(self.var.data_type)}

            caster = tc.get_caster(self.var.data_type)
            self.expr = CastNode(caster, self.expr)

        return {}

    def generate_code(self, code: List[str], label_count: List[int]):
        if type(self.var) is ArrayCallNode:
            self.var.generate_code(code, label_count, False)
            last_command = code.pop()
            self.expr.generate_code(code, label_count)
            code.append(last_command)
        else:
            self.expr.generate_code(code, label_count)
            self.var.generate_code(code, label_count, False)

    def run(self):
        pass


class BinOp(Enum):
    ADD = '+'
    SUB = '-'
    MUL = '*'
    DIV = '/'
    EQUAL = '='
    NOTEQUAL = '!='
    MORE = '>'
    LESS = '<'
    AND = 'and'
    OR = 'or'


class MathBinOpNode(ValueNode):
    def __init__(self, op: str, arg1: ValueNode, arg2: ValueNode):
        super().__init__(None)
        self.op = BinOp(op)
        self.arg1 = arg1
        self.arg2 = arg2

    @property
    def childs(self):
        return self.arg1, self.arg2

    def __str__(self)->str:
        return str(self.op.value) + (' | const_val = ' + str(self.const_val) if self.const_val else '')
        #str(self.arg1) + ' ' + str(self.op.value) + ' ' + str(self.arg2)

    def semantic_analysis(self, context: Context)->dict:
        message1 = self.arg1.semantic_analysis(context)  # math bin op
        message2 = self.arg2.semantic_analysis(context)  # math bin op

        # в одном из аргуметров произошла ошибка
        if 'error' in message1.keys():
            return message1
        elif 'error' in message2.keys():
            return message2

        # тип одного из аргументов none, такое может быть только при вызове функции, которая не возвращает значения
        if 'noneFunc' in message1.keys():
            return {'error': 'error noneFunc ' + message1['name'] + ' in binOp ' + str(self.op.value) + ';\n'}
        elif 'noneFunc' in message2.keys():
            return {'error': 'error noneFunc ' + message2['name'] + ' in binOp ' + str(self.op.value) + ';\n'}

        if self.arg1.data_type != self.arg2.data_type:
            caster, priority_type = tc.get_priority_caster(self.arg1.data_type, self.arg2.data_type)
            if caster is None:
                return {'error': 'Can not cast ' + str(self.arg1.data_type) + 'to' + str(self.arg2.data_type)}

            if self.arg1.data_type != priority_type:
                self.arg1 = CastNode(caster, self.arg1)
            elif self.arg2.data_type != priority_type:
                self.arg2 = CastNode(caster, self.arg2)

        self.data_type = DataType(self.arg1.data_type.dte)

        if self.data_type == dte.string and self.op != BinOp.ADD:
            return {'error': 'Operation %s is not allowed for string' % self.op.value}
        elif type(self.data_type) is ArrayDataType:
            return {'error': 'Operation %s is not allowed for arrays' % self.op.value}

        if self.arg1.const_val is not None and self.arg2.const_val is not None:  # оптимизируем
            self.optimize()

        return {}

    def optimize(self):
        if self.op == BinOp.ADD:
            self.const_val = self.arg1.const_val + self.arg2.const_val
        elif self.op == BinOp.SUB:
            self.const_val = self.arg1.const_val - self.arg2.const_val
        elif self.op == BinOp.MUL:
            self.const_val = self.arg1.const_val * self.arg2.const_val
        elif self.op == BinOp.DIV:
            self.const_val = self.arg1.const_val / self.arg2.const_val

    def generate_code(self, code: List[str], label_count: List[int]):
        if self.const_val is not None:
            code.append('ldc                   %s' % self.const_val)
            return

        if self.data_type == dte.string:
            code.append('new                   java/lang/StringBuilder')
            code.append('dup')
            code.append('invokespecial         java/lang/StringBuilder/<init>()V')
            self.arg1.generate_code(code, label_count)
            code.append(
                'invokevirtual         java/lang/StringBuilder/append(Ljava/lang/String;)Ljava/lang/StringBuilder;')
            self.arg2.generate_code(code, label_count)
            code.append(
                'invokevirtual         java/lang/StringBuilder/append(Ljava/lang/String;)Ljava/lang/StringBuilder;')
            code.append('invokevirtual         java/lang/StringBuilder/toString()Ljava/lang/String;')
            return

        self.arg1.generate_code(code, label_count)
        self.arg2.generate_code(code, label_count)
        if self.op == BinOp.ADD:
            code.append("%sadd" % JBCI.get_type_lower(self.data_type))
        elif self.op == BinOp.SUB:
            code.append("%ssub" % JBCI.get_type_lower(self.data_type))
        elif self.op == BinOp.MUL:
            code.append("%smul" % JBCI.get_type_lower(self.data_type))
        elif self.op == BinOp.DIV:
            code.append("%sdiv" % JBCI.get_type_lower(self.data_type))


class LogicBinOpNode(ValueNode):
    def __init__(self, op: BinOp, arg1: ValueNode, arg2: ValueNode):
        super().__init__(None)
        self.op = BinOp(op)
        self.arg1 = arg1
        self.arg2 = arg2
        self.data_type = DataType(dte.bool)

    @property
    def childs(self):
        return self.arg1, self.arg2

    def __str__(self)->str:
        return str(self.op.value) + (' | const_val = ' + str(self.const_val) if self.const_val else '')
        #str(self.arg1) + ' ' + str(self.op.value) + ' ' + str(self.arg2)

    def semantic_analysis(self, context: Context)->dict:
        message1 = self.arg1.semantic_analysis(context)  # Logic bin op
        message2 = self.arg2.semantic_analysis(context)  # Logic bin op

        # в одном из аргуметров произошла ошибка
        if 'error' in message1.keys():
            return message1
        elif 'error' in message2.keys():
            return message2

        # тип одного из аргументов none, такое может быть только при вызове функции, которая не возвращает значения
        if 'noneFunc' in message1.keys():
            return {'error': 'error noneFunc ' + message1['name'] + ' in binOp ' + str(self.op.value) + ';\n'}
        elif 'noneFunc' in message2.keys():
            return {'error': 'error noneFunc ' + message2['name'] + ' in binOp ' + str(self.op.value) + ';\n'}

        if self.op == BinOp.AND or self.op == BinOp.OR:
            caster = tc.BoolCaster()
            if self.arg1.data_type != dte.bool:
                self.arg1 = CastNode(caster, self.arg1)
            if self.arg2.data_type != dte.bool:
                self.arg2 = CastNode(caster, self.arg2)
        elif self.arg1.data_type != self.arg2.data_type:
            caster, priority_type = tc.get_priority_caster(self.arg1.data_type, self.arg2.data_type)
            if caster is None:
                return {'error': 'Can not cast ' + str(self.arg1.data_type) + ' to ' + str(self.arg2.data_type)}

            if self.arg1.data_type != priority_type:
                self.arg1 = CastNode(caster, self.arg1)
            elif self.arg2.data_type != priority_type:
                self.arg2 = CastNode(caster, self.arg2)

        if self.arg1.const_val is not None and self.arg2.const_val is not None:  # оптимизируем
            self.optimize(self.arg1.const_val, self.arg2.const_val)

        if type(self.arg1.data_type) is ArrayDataType and self.op != BinOp.AND and self.op != BinOp.OR:
            self.optimize(self.arg1.data_type.length, self.arg1.data_type.length)

        return {}

    def optimize(self, const_val_1, const_val_2):
        if self.op == BinOp.EQUAL:
            self.const_val = const_val_1 == const_val_2
        elif self.op == BinOp.NOTEQUAL:
            self.const_val = const_val_1 != const_val_2
        elif self.op == BinOp.MORE:
            self.const_val = const_val_1 > const_val_2
        elif self.op == BinOp.LESS:
            self.const_val = const_val_1 < const_val_2
        elif self.op == BinOp.AND:
            self.const_val = const_val_1 and const_val_2
        elif self.op == BinOp.OR:
            self.const_val = const_val_1 or const_val_2

        return {}

    def generate_code(self, code: List[str], label_count: List[int]):
        if self.const_val is not None:
            code.append('iconst_1' if self.const_val else 'iconst_0')
            return

        label_true = label_count[0]
        label_false = label_count[0] + 1
        label_out = label_count[0] + 2
        label_count[0] += 3

        # здесь можно как то улучшить, но я хз как
        if self.op == BinOp.AND:
            '''arg1
               ifeq                  LABEL_false
               arg2
               ifeq                  LABEL_false
               iconst_1              
               goto                  LABEL_out
            LABEL_false:
               iconst_0              
            LABEL_out:
            '''
            self.arg1.generate_code(code, label_count)
            code.append('ifeq                  LABEL_%s' % label_false)
            self.arg2.generate_code(code, label_count)
            code.append('ifeq                  LABEL_%s' % label_false)
            code.append('LABEL_%s:' % label_true)
            code.append('iconst_1')
            code.append('goto                  LABEL_%s' % label_out)
            code.append('LABEL_%s:' % label_false)
            code.append('iconst_0')
            code.append('LABEL_%s:' % label_out)
            return

        if self.op == BinOp.OR:
            '''arg1
               ifne                  LABEL_true // if not 0
               arg2
               ifeq                  LABEL_false // if 0
            LABEL_true:
               iconst_1              
               goto                  LABEL_out
            LABEL_fale:
               iconst_0              
            LABEL_out:'''
            self.arg1.generate_code(code, label_count)
            code.append('ifne                  LABEL_%s' % label_true)
            self.arg2.generate_code(code, label_count)
            code.append('ifeq                  LABEL_%s' % label_false)
            code.append('LABEL_%s:' % label_true)
            code.append('iconst_1')
            code.append('goto                  LABEL_%s' % label_out)
            code.append('LABEL_%s:' % label_false)
            code.append('iconst_0')
            code.append('LABEL_%s:' % label_out)
            return

        self.arg1.generate_code(code, label_count)
        if type(self.arg1.data_type) is ArrayDataType:
            code.append('arraylength')
        elif self.arg1.data_type == dte.string:
            code.append('invokevirtual         java/lang/String/length()I')

        self.arg2.generate_code(code, label_count)
        if type(self.arg2.data_type) is ArrayDataType:
            code.append('arraylength')
        elif self.arg2.data_type == dte.string:
            code.append('invokevirtual         java/lang/String/length()I')

        if self.op == BinOp.EQUAL:
            JBCI.get_equal_command(code, label_false, label_out, self.data_type)
        elif self.op == BinOp.NOTEQUAL:
            JBCI.get_notequal_command(code, label_false, label_out, self.data_type)
        elif self.op == BinOp.MORE:
            JBCI.get_more_command(code, label_false, label_out, self.data_type)
        elif self.op == BinOp.LESS:
            JBCI.get_less_command(code, label_false, label_out, self.data_type)


class StateListNode(AstNode):
    def __init__(self, states: List[AstNode]):
        super().__init__()
        self.states = states
        self.prog_name = 'prog'

    def __getitem__(self, item):
        return self.states[item]

    @property
    def childs(self):
        return tuple(self.states)

    def __str__(self)->str:
        return 'begin'

    def tree(self, addition: str)->str:
        new_addition = addition + CHAR2 + '  '
        s = addition + 'begin ' + '\n'
        for i, state in enumerate(self.states):
            if i == 0:
                s += addition + CHAR1 + ' ' + state.tree(new_addition) + '\n'
            else:
                s += addition + CHAR1 + ' ' + state.tree(new_addition) + '\n'
        s += addition + CHAR3 + 'end'
        return s

    def semantic_analysis(self, context: Context, local_context: Context=None)->dict:
        if local_context is not None:  # контекст не нужно создавать для блока if, for, while
            pass
        elif context is None:  # по идеи, невозможно
            return {'error': 'None context!'}
        else:
            local_context = Context(context)

        error = ''
        for s in self.states:
            message = s.semantic_analysis(local_context)  # state list
            if 'error' in message.keys():
                error += message['error'] + '. \n'

        if len(error) == 0:
            self.prog_name = context.get_prog_name()
            return {}

        return {'error': error}

    def generate_code(self, code: List[str], label_count: List[int]):
        for node in self.states:
            if type(node) is ArrayDefNode and node.var_type == VarType.GLOBAL:
                code.append('ldc                   %s' % node.data_type.length)
                code.append('%snewarray              %s' %
                    ('a' if node.data_type.dte == dte.string else '', JBCI.get_type_full(node.data_type.dte)))
                code.append('putstatic             %s/%s %s'
                              % (self.prog_name, node.name, JBCI.get_type(node.data_type)))
            node.generate_code(code, label_count)

    def run(self):
        pass


class WritelnNode(AstNode):
    def __init__(self, expr: ValueNode):
        super().__init__()
        self.expr = expr
        self.prog_name = 'prog'

    @property
    def childs(self):
        return self.expr,

    def __str__(self)->str:
        return 'writeln (' + str(self.expr) + ')'

    def semantic_analysis(self, context: Context)->dict:
        message = self.expr.semantic_analysis(context)  # writeln
        if 'error' in message.keys():
            return message
        self.prog_name = context.general_context.get_prog_name()

        return {}

    def generate_code(self, code: List[str], label_count: List[int]):
        if type(self.expr.data_type) is ArrayDataType:
            for i in range(self.expr.data_type.length):
                code.append('getstatic             java/lang/System/out Ljava/io/PrintStream;')
                self.expr.generate_code(code, label_count)
                code.append('ldc                   %s' % i)
                code.append('%saload' % JBCI.get_type_lower(self.expr.data_type))
                code.append('invokevirtual         java/io/PrintStream/print(%s)V' % JBCI.get_type(self.expr.data_type))
        else:
            code.append('getstatic             java/lang/System/out Ljava/io/PrintStream;')
            self.expr.generate_code(code, label_count)
            code.append('invokevirtual         java/io/PrintStream/print(%s)V' % JBCI.get_type(self.expr.data_type))

    def run(self):
        pass


class ReadlnNode(AstNode):
    def __init__(self, var: IdentNode):
        super().__init__()
        self.var = var

    @property
    def childs(self):
        return self.var,

    def __str__(self)->str:
        return 'readln (' + str(self.var) + ')'

    def semantic_analysis(self, context: Context)->dict:
        message = self.var.semantic_analysis(context)
        return message

    def generate_code(self, code: List[str], label_count: List[int]):
        s1 = 'getstatic             %s/SCANER Ljava/util/Scanner;' % self.var.prog_name
        s2 = ''
        if self.var.data_type.dte == dte.int:
            s2 = 'invokevirtual         java/util/Scanner/nextInt()I'
        elif self.var.data_type.dte == dte.float:
            s2 = 'invokevirtual         java/util/Scanner/nextFloat()F'
        elif self.var.data_type.dte == dte.bool:
            s2 = 'invokevirtual         java/util/Scanner/nextBoolean()Z'
        elif self.var.data_type.dte == dte.string:
            s2 = 'invokevirtual         java/util/Scanner/next()Ljava/lang/String;'

        if type(self.var.data_type) is ArrayDataType:
            for i in range(self.var.data_type.length):
                self.var.generate_code(code, label_count, False)
                code.append('ldc                   %s' % i)
                code.append(s1)
                code.append(s2)
                code.append('%sastore' % JBCI.get_type_lower(self.var.data_type))
        elif type(self.var) is ArrayCallNode:
            self.var.generate_code(code, label_count, False)
            code.insert(len(code) - 1, s1)
            code.insert(len(code) - 1, s2)
        else:
            code.append(s1)
            code.append(s2)
            self.var.generate_code(code, label_count, False)

    def run(self):
        pass


class IfNode(AstNode):  # Not leaf
    def __init__(self, condition: ValueNode, then_body: StateListNode, else_body: StateListNode = None):
        super().__init__()
        self.condition = condition
        self.then_body = then_body
        self.else_body = else_body

    @property
    def childs(self):
        return (self.condition, self.then_body) + ((self.else_body,) if self.else_body else tuple())

    def __str__(self)->str:
        return 'if'

    def tree(self, addition: str)->str:
        s = 'if ' + self.condition.tree(addition) + '\n' + self.then_body.tree(addition)
        if self.else_body is not None:
            s += '\nelse\n' + self.else_body.tree(addition)
        return s

    def semantic_analysis(self, context: Context)->dict:
        message = self.condition.semantic_analysis(context)  # if condition
        if 'error' in message.keys():
            return message

        if self.condition.data_type != dte.bool:
            self.condition = CastNode(tc.BoolCaster(), self.condition)

        local_context_then = Context(context)
        message = self.then_body.semantic_analysis(context, local_context_then)  # if then
        if 'error' in message.keys():
            return message

        if self.else_body is not None:
            local_context_else = Context(context)
            message = self.else_body.semantic_analysis(context, local_context_else)  # if else
            if 'error' in message.keys():
                return message

        return {}

    def generate_code(self, code: List[str], label_count: List[int]):
        '''
        IF body is:
        condition
        if !condition -> label_else
            then_body
            goto -> label_out
        label_else
            else_body
        label_out

        CONDITION body is:
        if !condition1 -> label_else
        if !condition1 -> label_else
        ...
        CONDITION returns only 1 or 0

        '''

        label_else = label_count[0]
        label_out = label_count[0] + 1
        label_count[0] += 2

        self.condition.generate_code(code, label_count)
        code.append('ifeq                  LABEL_%s' % label_else)
        self.then_body.generate_code(code, label_count)
        if code[len(code) - 1][1:] != 'return':
            code.append('goto                  LABEL_%s' % label_out)

        code.append('LABEL_%s:' % label_else)
        if self.else_body != None:
            self.else_body.generate_code(code, label_count)

        if code[len(code) - 1][1:] != 'return':
            code.append('LABEL_%s:' % label_out)

    def run(self):
        pass


class ForNode(AstNode):
    def __init__(self, var: IdentNode, start_value: ValueNode, end_value: ValueNode, loop_body: StateListNode):
        super().__init__()
        #self.var_assign = AssignNode(var, start_value)
        self.var = var
        self.start_value = start_value
        self.end_value = end_value
        self.loop_body = loop_body

    @property
    def childs(self):
        #return  self.var_assign, self.end_value, self.loop_body
        return self.var, self.start_value, self.end_value, self.loop_body

    def __str__(self) -> str:
        return 'for'

    def tree(self, addition: str)->str:
        s = 'for ' + str(self.var.name) + ' := ' + str(self.start_value)\
            + ' to ' + str(self.end_value) + 'do \n' + self.loop_body.tree(addition)
        return s

    def semantic_analysis(self, context: Context)->dict:

        message = self.var.semantic_analysis(context)  # for var
        if 'error' in message.keys():
            return message
        if self.var.data_type != dte.int:
            return {'error': 'Only int type'}

        message = self.start_value.semantic_analysis(context)  # for start
        if 'error' in message.keys():
            return message
        if self.start_value.data_type != dte.int:
            self.start_value = CastNode(tc.IntCaster(), self.start_value)

        message = self.end_value.semantic_analysis(context)  # for end
        if 'error' in message.keys():
            return message
        if self.end_value.data_type != dte.int:
            self.end_value = CastNode(tc.IntCaster(), self.end_value)

        local_context = Context(context)
        message = self.loop_body.semantic_analysis(context, local_context)  # for body
        if 'error' in message.keys():
            return message

        return {}

    def generate_code(self, code: List[str], label_count: List[int]):
        start_label = label_count[0]
        end_label = label_count[0] + 1
        label_count[0] += 2

        self.start_value.generate_code(code, label_count)
        self.var.generate_code(code, label_count, False)
        code.append('LABEL_%s:' % start_label)
        self.var.generate_code(code, label_count)
        self.end_value.generate_code(code, label_count)
        code.append('if_icmpgt             LABEL_%s' % end_label)
        self.loop_body.generate_code(code, label_count)
        self.var.generate_code(code, label_count)
        code.append('iconst_1')
        code.append('iadd')
        self.var.generate_code(code, label_count, False)
        code.append('goto                  LABEL_%s' % start_label)
        code.append('LABEL_%s:' % end_label)


    def run(self):
        pass


class WhileNode(AstNode):
    def __init__(self, condition: ValueNode, loop_body: StateListNode):
        super().__init__()
        self.condition = condition
        self.loop_body = loop_body

    @property
    def childs(self):
        return self.condition, self.loop_body

    def __str__(self) -> str:
        return 'while'

    def tree(self, addition: str)->str:
        return 'while ' + str(self.condition) + ' do \n' + self.loop_body.tree(addition)

    def semantic_analysis(self, context: Context):
        message = self.condition.semantic_analysis(context)  # while condition
        if 'error' in message.keys():
            return message

        self.condition = CastNode(tc.BoolCaster(), self.condition)

        local_context = Context(context)
        message = self.loop_body.semantic_analysis(context, local_context)  # while body
        if 'error' in message.keys():
            return message

        return {}

    def generate_code(self, code: List[str], label_count: List[int]):
        start_label = label_count[0]
        end_label = label_count[0] + 1
        label_count[0] += 2
        code.append('LABEL_%s:' % start_label)
        self.condition.generate_code(code, label_count)
        code.append('ifeq                  LABEL_%s' % end_label)
        self.loop_body.generate_code(code, label_count)
        code.append('goto                  LABEL_%s' % start_label)
        code.append('LABEL_%s:' % end_label)


    def run(self):
        pass


class Param:
    def __init__(self, name: str, data_type: Union[str, DataType]):
        super().__init__()
        if type(data_type) is str:
            self.data_type = DataType(data_type)
        elif type(data_type) is DataType:
            self.data_type = data_type
        self.name = name

    def __str__(self):
        return self.name + ':' + str(self.data_type)


class ParamArray(Param):
    def __init__(self, name: str, data_type: str, first_idx: int, last_idx: int):
        self.data_type = ArrayDataType(data_type, first_idx, last_idx)
        super().__init__(name, self.data_type)


class VarCounterNode(AstNode):
    def __init__(self, body: StateListNode, return_type: DataType=None):
        super().__init__()
        self.body = body
        self.return_type = return_type
        self.var_list = []

    @abstractmethod
    def semantic_analysis(self, context: Context):
        pass

    def add_var_dis(self, var_dis: VarDescription):
        self.var_list.append(var_dis)

    def generate_code(self, code: List[str], label_count: List[int]):
        pass

    def run(self):
        pass


class ProgramNode(VarCounterNode):  # должен хранить переменные
    def __init__(self, body: StateListNode, name: str='prog'):
        super().__init__(body, None)
        self.name = name

    @property
    def childs(self):
        return self.body.childs

    def __str__(self) -> str:
        return 'program ' + self.name

    def tree(self, addition: str)->str:
        s = 'program \n' + addition + str(list(map(str, self.var_list))) + '\n' + self.body.tree(addition)
        return s

    def semantic_analysis(self, context: Context):
        gloabal_context = GeneralContext(self, context)
        gloabal_context.prog_name = self.name
        gloabal_context.is_global = True

        message = self.body.semantic_analysis(gloabal_context)  # program
        if 'error' in message.keys():
            return message

        return {}

    def generate_code(self, code: List[str], label_count: List[int]):
        code.append('.source                  %s.java' % self.name)
        code.append('.class                   public %s' % self.name)
        code.append('.super                   java/lang/Object')
        code.append('')
        code.append('.field                   public static SCANER Ljava/util/Scanner;')
        # init method
        for var in self.var_list:
            code.append('.field                   public static %s %s' % (var.name, JBCI.get_type(var.data_type)))

        code.append('')
        code.append('.method                  public <init>()V')
        code.append('.limit stack          1')
        code.append('.limit locals         1')
        code.append('aload_0')
        code.append('invokespecial         java/lang/Object/<init>()V')
        code.append('return')
        code.append('.end method')
        code.append('')

        # special functions for convert int, float, str to bool
        JBCI.to_bool_func(code)

        # init global variables
        clinit = ['.method                  static <clinit>()V',
        '.limit stack          10',
        '.limit locals         0',
        'new                   java/util/Scanner',
        'dup',
        'getstatic             java/lang/System/in Ljava/io/InputStream;',
        'invokespecial         java/util/Scanner/<init>(Ljava/io/InputStream;)V',
        'putstatic             %s/SCANER Ljava/util/Scanner;' % self.name]

        local_var_count = 1
        for var in self.var_list:
            local_var_count += 1 if var.var_type == VarType.LOCAL else 0

        label_count = [7]
        for node in self.body:
            if type(node) is AssignNode:   # def and init global vars
                node.generate_code(clinit, [])
            elif type(node) is FuncDefNode:  # function
                node.generate_code(code, label_count)
            elif type(node) is StateListNode:  # main body
                code.append('.method                  public static main([Ljava/lang/String;)V')
                code.append('.limit stack          10')
                code.append('.limit locals         %s' % local_var_count)
                node.generate_code(code, label_count)
            else:  # def global
                if type(node) is ArrayDefNode:  # global array
                    clinit.append('ldc                   %s' % node.data_type.length)
                    clinit.append('newarray              %s' % JBCI.get_type_full(node.data_type))
                    clinit.append('putstatic             %s/%s %s'
                                  % (self.name, node.name, JBCI.get_type(node.data_type)))


        # end of init global vars
        clinit.append('return')
        clinit.append('.end method\n')
        clinit.append('')

        # end of program
        code.append('getstatic             %s/SCANER Ljava/util/Scanner;' % self.name)
        code.append('invokevirtual         java/util/Scanner/close()V')
        code.append('return')
        code.append('.end method')

        code.append('')
        code.extend(clinit)

    def run(self):
        pass


class FuncDefNode(VarCounterNode):  # должен хранить переменные
    def __init__(self, name: str, arguments: List[Param], return_type: Tuple, body: StateListNode):
        if len(return_type) > 1:
            super().__init__(body, ArrayDataType(return_type[0], return_type[1], return_type[2]))
        else:
            super().__init__(body, DataType(return_type[0]))
        self.name = name
        self.arguments = arguments if arguments is not None else []

    @property
    def childs(self):
        return self.body.childs

    def __str__(self) -> str:
        s = "func " + self.name + ' ('
        for arg in self.arguments:
            s += str(arg) + ', '
        s = s[:-2] + ' ): ' + str(self.return_type)# + ' \n' + str(self.body)
        return s

    def tree(self, addition: str)->str:
        s = "func " + self.name + ' ('
        for arg in self.arguments:
            s += str(arg) + ', '
        s = s[:-2] + ' ): ' + str(self.return_type) + ' \n' + \
            addition + str(list(map(str, self.var_list))) +\
            '\n' + self.body.tree(addition)
        s += '\n' + addition
        return s

    def semantic_analysis(self, context: Context):
        local_context = GeneralContext(self, context, True)
        params = []
        if self.arguments is not None:
            for arg in self.arguments:
                arg.var_type = VarType.PARAM
                local_context.add_var(arg.name, arg.data_type, arg.var_type)
                params.append(arg.data_type)

        context.add_func(self.name, self.return_type, params, local_context)

        message = self.body.semantic_analysis(local_context)  # func def
        if 'error' in message.keys():
            return message

        return {}

    def generate_code(self, code: List[str], label_count: List[int]):
        signature_str = ''
        for param in self.arguments:
            signature_str += JBCI.get_type(param.data_type)
        code.append('.method                  public static %s(%s)%s'
                    % (self.name, signature_str, JBCI.get_type(self.return_type)))

        code.append('.limit stack          10')
        code.append('.limit locals         %s' % len(self.var_list))

        self.body.generate_code(code, label_count)

        if self.return_type == dte.none and code[len(code) - 1] != 'return':
            code.append('return')
        #    code.append('ldc                   1')
        #    code.append('%sreturn' % JBCI.get_type_lower(self.return_type))

        '''
        if code[len(code) - 1][1:] != 'return':
            code.append("ldc %s" % JBCI.get_def_value(self.return_type.dte))
            code.append('%sreturn' % JBCI.get_type_lower(self.return_type))
        '''

        code.append('.end method')
        code.append('')

    def run(self):
        pass


class ReturnNode(AstNode):
    def __init__(self, expr: ValueNode):
        super().__init__()
        self.expr = expr
        self.data_type = None

    @property
    def childs(self):
        return self.expr,

    def __str__(self) -> str:
        return 'return ' + str(self.data_type)

    #def set_data_type(self, return_type: DataType):
    #    self.data_type = return_type

    def semantic_analysis(self, context: Context):
        self.data_type = context.general_context.node.return_type

        if self.data_type == dte.none:
            return {}#{'error': 'this function do not return anything'}

        message = self.expr.semantic_analysis(context)  # return
        if 'error' in message.keys():
            return message

        if self.data_type != self.expr.data_type and self.expr.data_type.can_casted_to(self.data_type):
            self.expr = CastNode(tc.get_caster(self.data_type), self.expr)

        return {}

    def generate_code(self, code: List[str], label_count: List[int]):
        if self.data_type != dte.none:
            self.expr.generate_code(code, label_count)
        code.append('%sreturn' % JBCI.get_type_lower(self.data_type))

    def run(self):
        pass


class FuncCallNode(ValueNode):
    def __init__(self, name: str, params: List[ValueNode]):
        super().__init__(None)
        self.name = name
        self.params = params
        self.prog_name = 'prog'
        if self.params is None:
            self.params = []

    @property
    def childs(self):
        return tuple(self.params) if len(self.params) else tuple()

    def __str__(self) -> str:
        return self.name + ' ' + str(self.data_type)

    def semantic_analysis(self, context: Context):
        func_dis = context.get_func(self.name)
        if func_dis is None:
            return {'error': 'function ' + self.name + 'is not defined'}

        self.data_type = func_dis.data_type

        if len(self.params) != func_dis.params_count:
            return {'error': str(self.name) + '() takes ' + str(func_dis.params_count)
                    + ' arguments but ' + str(len(self.params)) + 'were given'}

        for i, arg in enumerate(self.params):
            message = self.params[i].semantic_analysis(context)  # func call
            if 'error' in message.keys():
                return message

            if func_dis[i] != self.params[i].data_type:
                if func_dis[i].can_casted_to(arg.data_type):
                    self.params[i] = CastNode(tc.get_caster(func_dis[i]), self.params[i])
                else:
                    return {'error': 'cant cast argument ' + str(self.params[i].data_type) + 'to ' + func_dis[i]}

        self.prog_name = context.get_prog_name()
        return {}

    def generate_code(self, code: List[str], label_count: List[int]):
        signature_str = ''
        for param in self.params:
            param.generate_code(code, label_count)
            signature_str += JBCI.get_type(param.data_type)

        code.append('invokestatic          %s/%s(%s)%s'
                    % (self.prog_name, self.name, signature_str, JBCI.get_type(self.data_type)))

    def run(self):
        pass

class ArrayDefNode(AstNode):
    def __init__(self, name: str, first_idx: int, last_idx: int, data_type: str, values: List[ValueNode]=None):
        super().__init__()
        self.name = name
        self.data_type = ArrayDataType(data_type, first_idx, last_idx)
        self.first_index = first_idx
        self.last_index = last_idx
        self.values = values
        self.index = -1
        self.var_type = VarType.NONE

    @property
    def childs(self):
        return tuple(self.values) if self.values else ()

    def __str__(self) -> str:
        return self.name + ' ' + str(self.data_type)

    def semantic_analysis(self, context: Context):
        # если текущий контекст глобальный или его родитель, т.е. переменные в основном коде программы глобальные
        self.var_type = VarType.GLOBAL if context.is_global or context.parent.is_global else VarType.LOCAL
        if self.values is None:
            context.add_var(self.name, self.data_type, self.var_type)
            self.index = context.get_var(self.name).index
            return {}

        values = []
        for i, val in enumerate(self.values):
            message = val.semantic_analysis(context)  # array def
            if 'error' in message.keys():
                return message
            values.append(val.const_val)

        context.add_var(self.name, self.data_type, self.var_type, values)
        return {}

    def generate_code(self, code: List[str], label_count: List[int]):
        if self.var_type == VarType.GLOBAL:
            return

        code.append('ldc                   %s' % self.data_type.length)
        if self.data_type.dte == dte.string:
            code.append('anewarray              %s' % JBCI.get_type_full(self.data_type.dte))
        else:
            code.append('newarray              %s' % JBCI.get_type_full(self.data_type.dte))

        code.append('astore                %s' % self.index)

    def run(self):
        pass


class ArrayCallNode(ValueNode):
    def __init__(self, arr: IdentNode, arr_index: ValueNode):
        super().__init__(None)
        self.arr = arr
        self.name = arr.name
        self.arr_index = arr_index

    @property
    def childs(self):
        return self.arr_index,

    def __str__(self) -> str:
        return str(self.arr)#+ '[' + str(self.arr_index) + ']'

    def semantic_analysis(self, context: Context):
        message = self.arr.semantic_analysis(context)  # array call arr
        if 'error' in message.keys():
            return message
        message = self.arr_index.semantic_analysis(context)  # array call index
        if 'error' in message.keys():
            return message

        arr_dis = context.get_var(self.name)
        if type(arr_dis.data_type) != ArrayDataType:
            return {'error': '%s is not array' % arr_dis.name}

        self.data_type = DataType(arr_dis.data_type.dte)

        if self.arr_index.data_type != dte.int:
            self.arr_index = CastNode(tc.IntCaster(), self.arr_index)

        # optimize
        #if self.arr.const_val is not None and self.arr_index.const_val is not None:
        #    self.optimize(arr_dis)

        return {}

    def optimize(self, arr_dis: VarDescription):
            first_idx = arr_dis.data_type.first_index
            last_idx = arr_dis.data_type.last_index
            if self.arr_index.const_val < first_idx or self.arr_index.const_val > last_idx:
                return {'error': 'Index ' + self.arr_index.const_val + ' out of range ['
                                 + str(first_idx) + '..' + str(last_idx) + ']'}

            idx = self.arr_index.const_val - first_idx
            self.const_val = arr_dis.value[idx]

    def generate_code(self, code: List[str], label_count: List[int], get:bool=True):
        self.arr.generate_code(code, label_count)
        self.arr_index.generate_code(code, label_count)

        if self.arr.data_type.first_index != 0:
            code.append('ldc                   %s' % self.arr.data_type.first_index)
            code.append('isub')

        if get:
            code.append('%saload' % JBCI.get_type_lower(self.data_type))
        else:
            code.append('%sastore' % JBCI.get_type_lower(self.data_type))

    def run(self):
        pass
