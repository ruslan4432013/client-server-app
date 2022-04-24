"""
Задание 4.

Преобразовать слова «разработка», «администрирование», «protocol»,
«standard» из строкового представления в байтовое и выполнить
обратное преобразование (используя методы encode и decode).

Подсказки:
--- используйте списки и циклы, не дублируйте функции
"""

words = ['разработка', 'администрирование', 'protocol', 'standard']

words_in_bytes = [word.encode('UTF-8') for word in words]
decoded_words = [word.decode('UTF-8') for word in words_in_bytes]

print('Закодированные слова:')
for word_in_byte in words_in_bytes:
    print(word_in_byte)

print('\nРаскодированные слова:')
for decoded_word in decoded_words:
    print(decoded_word)