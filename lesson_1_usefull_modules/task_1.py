"""
1. Написать функцию host_ping(), в которой с помощью утилиты ping будет проверяться доступность сетевых узлов.
Аргументом функции является список, в котором каждый сетевой узел должен быть представлен именем хоста или ip-адресом.
В функции необходимо перебирать ip-адреса и проверять их доступность с выводом соответствующего сообщения
(«Узел доступен», «Узел недоступен»). При этом ip-адрес сетевого узла должен создаваться с помощью функции ip_address().
(Внимание! Аргументом сабпроцеса должен быть список, а не строка!!! Для уменьшения времени работы скрипта при проверке
нескольких ip-адресов, решение необходимо выполнить с помощью потоков)
"""
import locale
from ipaddress import ip_address
from itertools import zip_longest
from subprocess import Popen, PIPE
import platform
import re
from typing import List
from tabulate import tabulate

# Кодировка и список IP адресов
ENCODING = locale.getpreferredencoding()
lists = ['8.8.8.8', 'yandex.ru', 'a', '192.192.229.222', 'hh.ru', 'google.com']
ip_regexp = re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")


def host_ping(address_list: List[str]):
    processes: List[Popen] = []
    param = '-n' if platform.system().lower() == 'windows' else '-c'

    error_process = []
    success_process = []

    reachable_ip = []
    unreachable_ip = []

    columns = ['Узел доступен', 'Узел недоступен']

    # Запускаем процессы и заполняем ими список
    for addr in address_list:
        args = ['ping', param, '5', addr]
        process = Popen(args, stdout=PIPE, stderr=PIPE)
        processes.append(process)

    # Ожидаем окончания всех процессов
    while True:
        if all([proc.poll() == 0 or proc.poll() for proc in processes]):
            break

    # Разделяем процессы на успешные и не успешные
    for process in processes:
        success_process.append(process) if process.poll() == 0 else error_process.append(process)

    # Ищем ip адрес в успешных ответах и добавляем их в список
    for process in success_process:
        output_from_process = process.stdout.read().decode(ENCODING)
        ip_addr = re.search(ip_regexp, output_from_process).group()
        reachable_ip.append(ip_address(ip_addr))

    # Обработка неудачных ip
    for error_proc in error_process:
        unreachable_ip.append(error_proc.args[-1])

    # Вывод адресов
    print(tabulate([[success, error] for success, error in zip_longest(reachable_ip, unreachable_ip)], headers=columns,
                   tablefmt="pipe"))

if __name__ == '__main__':
    host_ping(lists)
