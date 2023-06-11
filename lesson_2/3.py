"""
Задание на закрепление знаний по модулю yaml. Написать скрипт, автоматизирующий
сохранение данных в файле YAML-формата. Для этого:
a. Подготовить данные для записи в виде словаря, в котором первому ключу
соответствует список, второму — целое число, третьему — вложенный словарь, где
значение каждого ключа — это целое число с юникод-символом, отсутствующим в
кодировке ASCII (например, €);
b. Реализовать сохранение данных в файл формата YAML — например, в файл file.yaml.
При этом обеспечить стилизацию файла с помощью параметра default_flow_style, а
также установить возможность работы с юникодом: allow_unicode = True;
c. Реализовать считывание данных из созданного файла и проверить, совпадают ли они
с исходными.
"""
import yaml



data = {
    'list': [
        'list',
        'list',
        'list'
    ],
    'int': 4,
    'dict': {
        'euro': '\u20ac',
        'ruble': '\u20bd',
    }
}

with open('file.yaml', 'w', encoding='utf-8') as f_in:
    yaml.dump(data, f_in, default_flow_style=False, allow_unicode=True, sort_keys=False)

with open("file.yaml", 'r', encoding='utf-8') as f_out:
    new_data = yaml.load(f_out, Loader=yaml.SafeLoader)

print(data == new_data)