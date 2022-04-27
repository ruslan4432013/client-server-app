"""
1. Задание на закрепление знаний по модулю CSV. Написать скрипт, осуществляющий выборку
определенных данных из файлов info_1.txt, info_2.txt, info_3.txt и формирующий новый
«отчетный» файл в формате CSV. Для этого:
      a)Создать функцию get_data(), в которой в цикле осуществляется перебор файлов с
        данными, их открытие и считывание данных. В этой функции из считанных данных
        необходимо с помощью регулярных выражений извлечь значения параметров
        «Изготовитель системы», «Название ОС», «Код продукта», «Тип системы». Значения
        каждого параметра поместить в соответствующий список. Должно получиться четыре
        списка — например, os_prod_list, os_name_list, os_code_list, os_type_list. В этой же
        функции создать главный список для хранения данных отчета — например, main_data
        — и поместить в него названия столбцов отчета в виде списка: «Изготовитель
        системы», «Название ОС», «Код продукта», «Тип системы». Значения для этих
        столбцов также оформить в виде списка и поместить в файл main_data (также для
        каждого файла);
      b)Создать функцию write_to_csv(), в которую передавать ссылку на CSV-файл. В этой
        функции реализовать получение данных через вызов функции get_data(), а также
        сохранение подготовленных данных в соответствующий CSV-файл;
      c)Проверить работу программы через вызов функции write_to_csv().
"""
import re
import csv
from detect_encode import get_encoding

def get_data():
    path_to_files = ['info/info_1.txt', 'info/info_2.txt', 'info/info_3.txt']
    os_prod_list = []
    os_name_list = []
    os_code_list = []
    os_type_list = []
    for path in path_to_files:
        with open(path, 'r', encoding=get_encoding(path)) as file:
            file_text = file.read()
            os_prod_list.extend(re.findall(r'Изготовитель системы:\s+(.+)', file_text))
            os_name_list.extend(re.findall(r'Название ОС:\s+(.+)', file_text))
            os_code_list.extend(re.findall(r'Код продукта:\s+(.+)', file_text))
            os_type_list.extend(re.findall(r'Тип системы:\s+(.+)', file_text))

    main_data = [["Изготовитель системы", "Название ОС", "Код продукта", "Тип системы"]]
    for os_prod, os_name, os_code, os_type in zip(os_prod_list, os_name_list, os_code_list, os_type_list):
        main_data.append([os_prod, os_name, os_code, os_type])
    return main_data


def write_to_csv(path_to_csv):
    data_for_write = get_data()
    with open(f'report/{path_to_csv}', 'w+', encoding='UTF-8') as file:
        file_writer = csv.writer(file, quoting=csv.QUOTE_NONNUMERIC)
        file_writer.writerows(data_for_write)


if __name__ == '__main__':
    write_to_csv('os_report_data.csv')
