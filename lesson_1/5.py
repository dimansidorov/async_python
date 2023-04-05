"""
Выполнить пинг веб-ресурсов yandex.ru, youtube.com и преобразовать результаты
из байтовового в строковый тип на кириллице.
"""

import subprocess
import chardet

args = [('ping', 'yandex.ru'), ('ping', 'youtube.com')]
for item in args:
    pings = subprocess.Popen(item, stdout=subprocess.PIPE)
    for line in pings.stdout:
        result = chardet.detect(line)
        line = line.decode(result['encoding']).encode('utf-8')
        print(line.decode('utf-8'))
        break