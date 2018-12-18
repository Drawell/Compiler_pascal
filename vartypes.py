from enum import Enum
from typing import TypeVar, Union


class VarType(Enum):
    LOCAL = 'LOCAL'
    GLOBAL = 'GLOBAL'
    PARAM = 'PARAM'
    NONE = 'NONE'


class DataTypeEnum(Enum):
    none = 'none'
    int = 'integer'
    float = 'real'
    bool = 'boolean'
    string = 'string'

    def __str__(self)->str:
        if self.int: return 'INT'
        elif self.float: return 'REAL'
        elif self.bool: return 'BOOL'
        elif self.string: return 'STRING'
        elif self.none: return 'NONE'


Str_or_dte_var_type = TypeVar('srt_or_dte', str, DataTypeEnum)


class DataType:
    def __init__(self, data_type: Union[str, DataTypeEnum]):
        if type(data_type) is str:
            self.dte = self.get_data_type_enum(data_type)
        elif type(data_type) is DataTypeEnum:
            self.dte = data_type
        elif type(data_type) is DataType:
            self.dte = data_type.data_type

    def __str__(self):
        return str(self.dte.value)

    def __eq__(self, other):
        if type(other) is DataType:
            return self.dte == other.data_type
        if type(other) is DataTypeEnum:
            return self.dte == other

        return False

    def __ne__(self, other):
        if type(other) is DataType:
            return self.dte != other.dte
        if type(other) is DataTypeEnum:
            return self.dte != other

        return True

    def can_casted_to(self, data_type):
        if data_type == DataTypeEnum.string and self.dte != data_type:
            return False
        else:
            return True

    @staticmethod
    def get_data_type_enum(data_type: str)->DataTypeEnum:
        if data_type == 'integer':
            return DataTypeEnum.int
        elif data_type == 'real':
            return DataTypeEnum.float
        elif data_type == 'boolean':
            return DataTypeEnum.bool
        elif data_type == 'string':
            return DataTypeEnum.string
        elif data_type == 'none':
            return DataTypeEnum.none
        else:
            return DataTypeEnum.none


class ArrayDataType(DataType):
    def __init__(self, data_type: Str_or_dte_var_type, first_index: int, last_index: int):
        super().__init__(data_type)
        self.first_index = first_index
        self.last_index = last_index

    def __str__(self):
        return 'array [' + str(self.first_index) + '..' + str(self.last_index) + '] of ' + str(self.dte)

    def __eq__(self, other: DataType):
        if self.dte == other.dte:
            if type(other) is ArrayDataType:
                if self.first_index == other.first_index and self.last_index == other.last_index:
                    return True
            elif type(other) is ValListDataType:
                if self.last_index - self.first_index + 1 == other.length:
                    return True
        return False

    def __ne__(self, other: DataType):
        if self.dte == other.dte:
            if type(other) is ArrayDataType:
                if self.first_index == other.first_index and self.last_index == other.last_index:
                    return False
            elif type(other) is ValListDataType:
                if self.last_index - self.first_index + 1 == other.length:
                    return False
        return True

    def can_casted_to(self, data_type):
        return False


class ValListDataType(DataType):
    def __init__(self, data_type: Str_or_dte_var_type, length: int):
        super().__init__(data_type)
        self.length = length

    def __str__(self):
        return 'val_list len = ' + str(self.length) + ' of ' + str(self.dte)

    def __eq__(self, other: DataType):
        if self.dte == other.dte:
            if type(other) is ValListDataType:
                if self.length == other.length:
                    return True
            elif type(other) is ArrayDataType:
                if self.length == other.last_index - other.first_index + 1:
                    return True
        return False

    def __ne__(self, other: DataType):
        if self.dte == other.dte:
            if type(other) is ValListDataType:
                if self.length == other.length:
                    return False
            elif type(other) is ArrayDataType:
                if self.length == other.last_index - other.first_index + 1:
                    return False
        return True

    def can_casted_to(self, data_type):
        return False