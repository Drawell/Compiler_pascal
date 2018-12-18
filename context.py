from vartypes import DataTypeEnum as dte, DataType, ArrayDataType, VarType
from typing import List
#from mel_ast import VarCounterNode


class ObjectDescription:
    def __init__(self, name: str, object_type: DataType):
        self.name = name
        self.data_type = object_type


class VarDescription(ObjectDescription):
    def __init__(self, name: str, data_type: DataType, var_type: VarType, index: int, value):
        super().__init__(name, data_type)
        self.var_type = var_type
        self.index = index
        self.value = value

    def __str__(self):
        return '(' + str(self.index) + ', ' + self.name + ', '\
               + str(self.data_type) + ', ' + str(self.var_type.value) + ')'


class FuncDescription(ObjectDescription):
    # params LIST[DataType]
    def __init__(self, name: str, return_type: DataType, params: List[DataType], context):
        super().__init__(name, return_type)
        self.params = params
        self.params_count = len(params)
        self.func_context = context

    def __getitem__(self, item: int):
        if len(self.params) > item:
            return self.params[item]
        else:
            return None


class IndexCounter:
    def __init__(self):
        self.global_count = 0
        self.local_count = 0
        self.param_count = 0

    def get_new_idx(self, var_type: VarType):
        if var_type == VarType.GLOBAL:
            self.global_count += 1
            return self.global_count - 1
        elif var_type == VarType.LOCAL:
            self.local_count += 1
            return self.local_count - 1
        elif var_type == VarType.PARAM:
            self.param_count += 1
            return self.param_count - 1


class Context:
    def __init__(self, parent: 'Context'=None):
        self.variables = {}
        self.functions = {}
        self.parent = parent
        self.general_context = self
        if parent is not None:
            self.general_context = parent.general_context
            self.is_global = False

            if parent.parent is None:
                self.is_global = True  # основной блок программы
        else:
            self.is_global = True

    def add_var(self, name: str, data_type: DataType, var_type: VarType, value=None):
        if name in self.variables.keys():
            return 'error: variable is defined'

        index = self.general_context.get_index(var_type)

        # должны ли локальные переменные основного блока быть глобальными
        if var_type == VarType.LOCAL and not self.general_context.is_func:
            var_type = VarType.GLOBAL

        self.variables[name] = VarDescription(name, data_type, var_type, index, value)
        self.general_context.register_var_description(self.variables[name])
        return None

    def add_func(self, name: str, return_type: DataType, params: List[DataType], context):
        if name in self.functions.keys():
            return 'error: function is defined'
        self.functions[name] = FuncDescription(name, return_type, params, context)
        return None

    def get_var(self, name: str)->VarDescription:
        if name in self.variables.keys():
            return self.variables[name]
        if self.parent is None:
            return None
        return self.parent.get_var(name)

    def get_func(self, name: str)->FuncDescription:
        if name in self.functions.keys():
            return self.functions[name]
        if self.parent is None:
            return None
        return self.parent.get_func(name)


class GeneralContext(Context):
    def __init__(self, node, parent=None, is_func: bool =False):
        super().__init__(parent)
        self.node = node
        self.counter = IndexCounter()
        self.general_context = self
        self.is_func = is_func

    def get_index(self, var_type: VarType)-> int:
        if self.is_func:
            return self.counter.get_new_idx(var_type)
        else:
            return self.counter.get_new_idx(VarType.GLOBAL)

    def register_var_description(self, var_dis: VarDescription):
        self.node.add_var_dis(var_dis)
