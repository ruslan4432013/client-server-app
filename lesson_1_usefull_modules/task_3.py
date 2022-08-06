'''
3. Написать функцию host_range_ping_tab(), возможности которой основаны на функции из примера 2.
Но в данном случае результат должен быть итоговым по всем ip-адресам, представленным в табличном формате
(использовать модуль tabulate). Таблица должна состоять из двух колонок
'''
from task_2 import host_range_ping


def host_range_ping_tab():
    host_range_ping()


if __name__ == '__main__':
    host_range_ping_tab()
