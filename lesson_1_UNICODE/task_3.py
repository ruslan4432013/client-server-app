"""
Задание 3.

Определить, какие из слов «attribute», «класс», «функция», «type»
невозможно записать в байтовом типе с помощью маркировки b'' (без encode decode).

Подсказки:
--- используйте списки и циклы, не дублируйте функции
--- обязательно!!! усложните задачу, "отловив" и обработав исключение,
придумайте как это сделать
"""

words_to_bytes = ['attribute', 'класс', 'функция', 'type']

for word in words_to_bytes:
    try:
        byte_word = bytes(word, 'ascii')
        print(f"Слово '{word}' можно записать в байтовом типе с помощью маркировки b'")
    except UnicodeEncodeError:
        print(f"Слово '{word}' нельзя записать в байтовом типе с помощью маркировки b'")



