import dis
from abc import ABC
from pprint import pprint


class ServerMaker(type):
    def __init__(cls, name, bases, cls_attrs):
        # name - экземпляр метакласса - Server
        # bases - кортеж базовых классов - ()
        # cls_attrs - словарь атрибутов и методов экземпляра метакласса

        # Список методов, которые используются в функциях класса:
        methods = []  # получаем с помощью 'LOAD_GLOBAL'
        # Обычно методы, обёрнутые декораторами попадают
        # не в 'LOAD_GLOBAL', а в 'LOAD_METHOD'
        methods_2 = []  # получаем с помощью 'LOAD_METHOD'
        # Атрибуты, используемые в функциях классов
        attrs = []  # получаем с помощью 'LOAD_ATTR'
        # перебираем ключи
        # перебираем ключи
        for func in cls_attrs:
            # Пробуем
            try:
                # Возвращает итератор по инструкциям в предоставленной функции
                # , методе, строке исходного кода или объекте кода.
                ret = dis.get_instructions(cls_attrs[func])
                # ret - <generator object _get_instructions_bytes at 0x00000062EAEAD7C8>
                # ret - <generator object _get_instructions_bytes at 0x00000062EAEADF48>
                # ...
                # Если не функция то ловим исключение
                # (если порт)
            except TypeError:
                pass
            else:
                # Раз функция разбираем код, получая используемые методы и атрибуты.
                for i in ret:
                    # i - Instruction(opname='LOAD_GLOBAL', opcode=116, arg=9, argval='send_message',
                    # argrepr='send_message', offset=308, starts_line=201, is_jump_target=False)
                    # opname - имя для операции
                    if i.opname == 'LOAD_GLOBAL':
                        if i.argval not in methods:
                            # заполняем список методами, использующимися в функциях класса
                            methods.append(i.argval)
                    elif i.opname == 'LOAD_METHOD':
                        if i.argval not in methods_2:
                            # заполняем список атрибутами, использующимися в функциях класса
                            methods_2.append(i.argval)
                    elif i.opname == 'LOAD_ATTR':
                        if i.argval not in attrs:
                            # заполняем список атрибутами, использующимися в функциях класса
                            attrs.append(i.argval)

        if 'connect' in methods:
            raise TypeError('Использование метода connect недопустимо в серверном классе')
        # Если сокет не инициализировался константами websockets и обработчика ws_handler, тоже исключение.
        if not ('websockets' in methods and 'ws_handler' in attrs):
            raise TypeError('Некорректная инициализация сокета.')
        # Обязательно вызываем конструктор предка:
        super().__init__(name, bases, cls_attrs)


class ClientMaker(type):
    def __init__(cls, name, bases, cls_attrs):
        # Список методов, которые используются в функциях класса:
        methods = []
        for func in cls_attrs:
            # Пробуем
            try:
                ret = dis.get_instructions(cls_attrs[func])
                # Если не функция то ловим исключение
            except TypeError:
                pass
            else:
                # Раз функция разбираем код, получая используемые методы.
                for i in ret:
                    if i.opname == 'LOAD_GLOBAL':
                        if i.argval not in methods:
                            methods.append(i.argval)
        # Если обнаружено использование недопустимого метода accept, listen, socket бросаем исключение:
        for command in ('accept', 'listen', 'socket'):
            if command in methods:
                raise TypeError('В классе обнаружено использование запрещённого метода')
        # Вызов get_message или send_message из utils считаем корректным использованием сокетов
        if 'get_message' in methods or 'send_message' in methods:
            pass
        else:
            raise TypeError('Отсутствуют вызовы функций, работающих с сокетами.')

        super().__init__(name, bases, cls_attrs)
