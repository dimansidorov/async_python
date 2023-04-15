"""
Задание на закрепление знаний по модулю CSV. Написать скрипт, осуществляющий выборку
определенных данных из файлов info_1.txt, info_2.txt, info_3.txt и формирующий новый
«отчетный» файл в формате CSV. Для этого:
a. Создать функцию get_data(), в которой в цикле осуществляется перебор файлов с
данными, их открытие и считывание данных. В этой функции из считанных данных
необходимо с помощью регулярных выражений извлечь значения параметров
«Изготовитель системы», «Название ОС», «Код продукта», «Тип системы». Значения
каждого параметра поместить в соответствующий список. Должно получиться четыре
списка — например, os_prod_list, os_name_list, os_code_list, os_type_list. В этой же
функции создать главный список для хранения данных отчета — например, main_data
— и поместить в него названия столбцов отчета в виде списка: «Изготовитель
системы», «Название ОС», «Код продукта», «Тип системы». Значения для этих
© geekbrains.ru 16
столбцов также оформить в виде списка и поместить в файл main_data (также для
каждого файла);
b. Создать функцию write_to_csv(), в которую передавать ссылку на CSV-файл. В этой
функции реализовать получение данных через вызов функции get_data(), а также
сохранение подготовленных данных в соответствующий CSV-файл;
c. Проверить работу программы через вызов функции write_to_csv().
"""

import csv

from chardet.universaldetector import UniversalDetector


def get_encoding(filename: str) -> str:
    detector = UniversalDetector()
    with open(filename, 'rb') as f:
        for line in f:
            detector.feed(line)
            if detector.done:
                break
        detector.close()

    return detector.result['encoding']


ENCODING = get_encoding('info_1.txt')


def get_data(filenames: list[str]) -> \
        tuple[list[str], list[str], list[str], list[str]]:
    os_prod_list = []
    os_name_list = []
    os_code_list = []
    os_type_list = []

    for file in filenames:
        with open(file, 'r', encoding=ENCODING) as f:
            content = f.readlines()
            for line in content:
                try:
                    start, end = map(lambda x: x.strip(), line.split(':'))
                    match start:
                        case "Изготовитель системы":
                            os_prod_list.append(end)
                        case "Название ОС":
                            os_name_list.append(end)
                        case "Код продукта":
                            os_code_list.append(end)
                        case "Тип системы":
                            os_type_list.append(end)
                except ValueError:
                    pass

    return os_prod_list, os_name_list, os_code_list, os_type_list


def write_to_csv(filename: str) -> None:
    main_data = [["Изготовитель системы", "Название ОС", "Код продукта", "Тип системы"]]
    main_data.extend(get_data(['info_1.txt', 'info_2.txt', 'info_1.txt']))
    with open(filename, 'w', encoding='UTF-8') as file:
        writer = csv.writer(file, quoting=csv.QUOTE_NONNUMERIC)
        for row in main_data:
            writer.writerow(row)


write_to_csv('data_report.csv')
