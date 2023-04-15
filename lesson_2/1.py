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
