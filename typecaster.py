from vartypes import DataTypeEnum, DataType
from abc import abstractmethod
from typing import Tuple


class TypeCaster:
    def __init__(self):
        pass

    @abstractmethod
    def cast(self, present_type: DataType):
        pass

    @abstractmethod
    def cast_in_real_time(self, value, present_type: DataType):
        pass

    @abstractmethod
    def get_type(self):
        pass


class IntCaster(TypeCaster):
    def __init__(self):
        super().__init__()

    def cast(self, pre):
        pass

    def cast_in_real_time(self, value, present_type: DataType)-> int:
        if present_type == DataTypeEnum.string:
            return None
        elif present_type == DataTypeEnum.bool:
            if value:
                return 1
            else:
                return 0
        return int(value)

    def get_type(self):
        return DataType(DataTypeEnum.int)


class FloatCaster(TypeCaster):
    def __init__(self):
        super().__init__()

    def cast(self, pre):
        pass

    def cast_in_real_time(self, value, present_type: DataType)->float:
        if present_type == DataTypeEnum.string:
            return None
        elif present_type == DataTypeEnum.bool:
            if value:
                return 1
            else:
                return 0
        return float(value)

    def get_type(self):
        return DataType(DataTypeEnum.float)


class BoolCaster(TypeCaster):
    def __init__(self):
        super().__init__()

    def cast(self, pre):
        pass

    def cast_in_real_time(self, value, present_type: DataType):
        if present_type == DataTypeEnum.string:
            if value == '':
                return False
            return True
        elif present_type == DataTypeEnum.bool:
            return value
        else:
            if value == 0:
                return False
            else:
                return True

    def get_type(self):
        return DataType(DataTypeEnum.bool)


class StringCaster(TypeCaster):
    def __init__(self):
        super().__init__()

    def cast(self, present_type: DataTypeEnum):
        pass

    def cast_in_real_time(self, value, present_type: DataType)->str:
        if present_type == DataTypeEnum.string:
            return value
        elif present_type == DataTypeEnum.bool:
            if value:
                return 'True'
            else:
                return 'False'

        return str(value)

    def get_type(self):
        return DataType(DataTypeEnum.string)


def get_caster_and_type(object_type: DataTypeEnum)->Tuple[TypeCaster, DataTypeEnum]:
    if object_type == DataTypeEnum.string:
        return StringCaster(), DataTypeEnum.string
    if object_type == DataTypeEnum.float:
        return FloatCaster(), DataTypeEnum.float
    if object_type == DataTypeEnum.int:
        return IntCaster(), DataTypeEnum.int
    if object_type == DataTypeEnum.bool:
        return BoolCaster(), DataTypeEnum.bool


def get_caster(object_type: DataTypeEnum):
    return get_caster_and_type(object_type)[0]


def get_priority_caster(type1: DataType, type2: DataType)->Tuple[TypeCaster, DataTypeEnum]:
    '''
    string -> float -> int -> bool
    string -> string
    '''
    priority = {DataTypeEnum.string: 4, DataTypeEnum.float: 3, DataTypeEnum.int: 2, DataTypeEnum.bool: 1}

    if type1 == DataTypeEnum.none or type2 == DataTypeEnum.none:  # это должно быть недостижимо
        return None, DataTypeEnum.none

    if type1 == type2:
        return None, type1

    if type(type1) is DataType and type(type2) is DataType:
        if priority[type2.dte] > priority[type1.dte]:
            type1, type2 = type2, type1

        return get_caster_and_type(type1.dte)

    return None, None
