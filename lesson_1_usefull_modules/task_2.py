'''
Написать функцию host_range_ping() для перебора ip-адресов из заданного диапазона.
Меняться должен только последний октет каждого адреса.
По результатам проверки должно выводиться соответствующее сообщение.
'''
import time

from task_1 import ip_regexp
from task_1 import host_ping
from ipaddress import ip_address


def host_range_ping():
    while True:
        previous_addr = input('Введите первоначальный адрес:')
        try:
            if ip_regexp.match(previous_addr):
                ip_address(previous_addr)
                break
            print('Введите корректный IP адрес')
        except Exception as e:
            print('Введите корректный IP адрес')

    while True:
        length_addr = input('Сколько адресов проверить?: ')
        try:
            length = int(length_addr)

            last_oct = int(previous_addr.split('.')[-1])

            ip_list = [f"{'.'.join(previous_addr.split('.')[0:-1])}.{last_oct + i}" for i in range(length)]

            if int(ip_list[-1].split('.')[-1]) > 255:
                print('Последний октет не должен быть больше 255, давайте попробуем еще раз')
                continue

            host_ping(ip_list)

            break
        except Exception as e:
            print(e)
            continue


if __name__ == '__main__':
    host_range_ping()

