"""
Создать текстовый файл test_file.txt, заполнить его тремя строками: «сетевое программирование», «сокет», «декоратор».
Проверить кодировку файла по умолчанию. Принудительно открыть файл в формате Unicode и вывести его содержимое.
"""
from chardet.universaldetector import UniversalDetector

words = ['сетевое программирование', 'сокет', 'декоратор']
with open('test_file.txt', 'w') as f:
    for word in words:
        f.write(f'{word}\n')

detector = UniversalDetector()
with open('test_file.txt', 'rb') as f:
    for line in f:
        detector.feed(line)
        if detector.done:
            break
    detector.close()

encoding = detector.result['encoding']
print(f'Кодировка - {encoding}\n')

with open('test_file.txt', 'r', encoding='utf-8') as f:
    text = f.read().split('\n')
    for word in text:
        print(word)

with open('test_file.txt', 'w', encoding=encoding) as f:
    f.write('')




