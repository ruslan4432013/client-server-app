'''
2. Задание на закрепление знаний по модулю json. Есть файл orders в формате JSON с
информацией о заказах. Написать скрипт, автоматизирующий его заполнение данными. Для
этого:
    a) Создать функцию write_order_to_json(), в которую передается 5 параметров — товар
    (item), количество (quantity), цена (price), покупатель (buyer), дата (date). Функция
    должна предусматривать запись данных в виде словаря в файл orders.json. При
    записи данных указать величину отступа в 4 пробельных символа;
    b) Проверить работу программы через вызов функции write_order_to_json() с передачей
    в нее значений каждого параметра.
'''
import datetime
import json

from detect_encode import get_encoding


def write_order_to_json(item, quantity, price, buyer, date):
    with open('info/orders.json', 'r', encoding=get_encoding('info/orders.json')) as file:
        orders_data: dict = json.load(file)

        data_for_write = {
            'item': item,
            'quantity': quantity,
            'price': price,
            'buyer': buyer,
            'date': date
        }

        orders_data.get('orders', []).append(data_for_write)

    with open('info/orders.json', 'w', encoding='utf-8') as file:
        json.dump(orders_data, file, indent=4, ensure_ascii=False, default=str)


if __name__ == '__main__':
    write_order_to_json('Трансформер', 5, 333, 'ShopLyne', datetime.datetime.now())
