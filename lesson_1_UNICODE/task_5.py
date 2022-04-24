"""
Задание 5.

Выполнить пинг веб-ресурсов yandex.ru, youtube.com и
преобразовать результаты из байтовового в строковый тип на кириллице.

Подсказки:
--- используйте модуль chardet, иначе задание не засчитается!!!
"""
import subprocess
import chardet

YANDEX_ARGS = ['ping', 'yandex.ru']
YOUTUBE_ARGS = ['ping', 'youtube.com']
YANDEX_PING = subprocess.Popen(YANDEX_ARGS, stdout=subprocess.PIPE)
YOUTUBE_PING = subprocess.Popen(YOUTUBE_ARGS, stdout=subprocess.PIPE)



for line in YANDEX_PING.stdout:
    encode_config = chardet.detect(line)
    encoding = encode_config['encoding']
    line = line.decode(encoding)
    print(line)

for line in YOUTUBE_PING.stdout:
    encode_config = chardet.detect(line)
    encoding = encode_config['encoding']
    line = line.decode(encoding)
    print(line)
