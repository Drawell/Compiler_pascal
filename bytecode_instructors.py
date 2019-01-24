from vartypes import DataType as DT, ArrayDataType as ADT, ValListDataType, DataTypeEnum as DTE
from typing import Union, List
from typecaster import BoolCaster, IntCaster, StringCaster, FloatCaster

#                int   float  bool  str
__cast_map__ = [[None, 'f2i', None, None],  # to int
                ['i2f', None, 'i2f', None],  # to float
                ['invokestatic          Puppy/toBoolean(I)Z',  # to bool
                 'invokestatic          Puppy/toBoolean(F)Z',
                 None,
                 'invokestatic          Puppy/toBoolean(Ljava/lang/String;)Z'],
                ['invokestatic          java/lang/String/valueOf(I)Ljava/lang/String;',  # to string
                 'invokestatic          java/lang/String/valueOf(F)Ljava/lang/String;',
                 'invokestatic          java/lang/String/valueOf(I)Ljava/lang/String;',
                 None]
                ]
__type_map__ = {DTE.int: 0, DTE.float: 1, DTE.bool: 2, DTE.string: 3}


def __init__(self):
    pass

class JBC_instructor:

    @staticmethod
    def get_def_value(data_type: DTE) -> str:
        if data_type == DTE.none: return '0'
        elif data_type == DTE.int: return '0'
        elif data_type == DTE.float: return '0.0'
        elif data_type == DTE.bool: return '0'
        elif data_type == DTE.string: return '""'

    @staticmethod
    def get_type_dte(data_type: DTE) -> str:
        if data_type == DTE.none: return 'V'
        elif data_type == DTE.int: return 'I'
        elif data_type == DTE.float: return 'F'
        elif data_type == DTE.bool: return 'Z'
        elif data_type == DTE.string: return 'Ljava/lang/String;'

    @staticmethod
    def get_type_dte_lower(data_type: DTE) -> str:
        if data_type == DTE.none: return ''
        elif data_type == DTE.int: return 'i'
        elif data_type == DTE.float: return 'f'
        elif data_type == DTE.bool: return 'i'
        elif data_type == DTE.string: return 'a'

    @staticmethod
    def get_type(data_type: Union[DT, ADT])-> str:
        if type(data_type) is ADT:
            return '[' + JBC_instructor.get_type_dte(data_type.dte)
        return JBC_instructor.get_type_dte(data_type.dte)

    @staticmethod
    def get_type_lower(data_type: Union[DT, ADT, DTE])-> str:
        if type(data_type) is ADT:
            return 'a'
        elif type(data_type) is DT:
            return JBC_instructor.get_type_dte_lower(data_type.dte)

        return JBC_instructor.get_type_dte_lower(data_type)

    @staticmethod
    def get_type_full(data_type: DTE):
        if data_type == DTE.none: return ''
        elif data_type == DTE.int: return 'int'
        elif data_type == DTE.float: return 'float'
        elif data_type == DTE.bool: return 'boolean'
        elif data_type == DTE.string: return 'java/lang/String'

    @staticmethod
    def get_return(data_type: DT)-> str:
        return JBC_instructor.get_type_dte_lower(data_type.dte) + 'return'


    @staticmethod
    def get_cast_command(what: DT, to: DT)->str:
        to_int = __type_map__[to.dte]
        what_int = __type_map__[what.dte]
        return __cast_map__[to_int][what_int]

    @staticmethod
    def get_equal_command(code: List[str], label_false: int, label_out: int, data_type: Union[DT, ADT]):
        if type(data_type) is ADT or data_type.dte == DTE.string:
            code.append('if_acmpne             LABEL_%s' % label_false)
        elif data_type.dte == DTE.float:
            code.append('fcmpl')
            code.append('ifne                  LABEL_%s' % label_false)
        elif data_type.dte == DTE.int or data_type.dte == DTE.bool:
            code.append('if_icmpne             LABEL_%s' % label_false)

        JBC_instructor.__get_if_end_command__(code, label_false, label_out)

    @staticmethod
    def get_notequal_command(code: List[str], label_false: int, label_out: int, data_type: Union[DT, ADT]):
        if type(data_type) is ADT or data_type.dte == DTE.string:
            code.append('if_acmpeq             LABEL_%s' % label_false)
        elif data_type.dte == DTE.float:
            code.append('fcmpl')
            code.append('ifeq                  LABEL_%s' % label_false)
        elif data_type.dte == DTE.int or data_type.dte == DTE.bool:
            code.append('if_icmpeq             LABEL_%s' % label_false)

        JBC_instructor.__get_if_end_command__(code, label_false, label_out)

    @staticmethod
    def get_more_command(code: List[str], label_false: int, label_out: int, data_type: DT):
        if data_type.dte == DTE.float:
            code.append('fcmpl')
            code.append('ifle                  LABEL_%s' % label_false)
        elif data_type.dte == DTE.int or data_type.dte == DTE.bool:
            code.append('if_icmple             LABEL_%s' % label_false)

        JBC_instructor.__get_if_end_command__(code, label_false, label_out)

    @staticmethod
    def get_less_command(code: List[str], label_false: int, label_out: int, data_type: DT):
        if data_type.dte == DTE.float:
            code.append('fcmpg')
            code.append('ifge                  LABEL_%s' % label_false)
        elif data_type.dte == DTE.int or data_type.dte == DTE.bool:
            code.append('if_icmpge             LABEL_%s' % label_false)

        JBC_instructor.__get_if_end_command__(code, label_false, label_out)

    @staticmethod
    def __get_if_end_command__(code: List[str], label_false: int, label_out: int):
        code.append('iconst_1')
        code.append('goto                  LABEL_%s' % label_out)
        code.append('LABEL_%s:' % label_false)
        code.append('iconst_0')
        code.append('LABEL_%s:' % label_out)

    @staticmethod
    def to_bool_func(list: List[str]):
        list.append('.method                  public static toBoolean(I)Z')
        list.append('.limit stack          1')
        list.append('.limit locals         1')
        list.append('iload_0')
        list.append('ifeq                  LABEL1')
        list.append('iconst_1')
        list.append('goto                  LABEL2')
        list.append('LABEL1:')
        list.append('iconst_0              ')
        list.append('LABEL2:')
        list.append('ireturn               ')
        list.append('.end method\n')

        list.append('.method                  public static toBoolean(F)Z')
        list.append('.limit stack          2')
        list.append('.limit locals         1')
        list.append('fload_0')
        list.append('fconst_0')
        list.append('fcmpl')
        list.append('ifeq                  LABEL3')
        list.append('iconst_1')
        list.append('goto                  LABEL4')
        list.append('LABEL3:')
        list.append('iconst_0')
        list.append('LABEL4:')
        list.append('ireturn')
        list.append('.end method\n')

        list.append('.method                  public static toBoolean(Ljava/lang/String;)Z')
        list.append('.limit stack          2')
        list.append('.limit locals         1')
        list.append('aload_0')
        list.append('ldc                   ""')
        list.append('if_acmpeq             LABEL5')
        list.append('iconst_1')
        list.append('goto                  LABEL6')
        list.append('LABEL5:')
        list.append('iconst_0 ')
        list.append('LABEL6:')
        list.append('ireturn')
        list.append('.end method\n')