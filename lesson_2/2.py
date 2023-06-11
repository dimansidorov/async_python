"""
Задание на закрепление знаний по модулю json. Есть файл orders в формате JSON с
информацией о заказах. Написать скрипт, автоматизирующий его заполнение данными. Для
этого:
a. Создать функцию write_order_to_json(), в которую передается 5 параметров — товар
(item), количество (quantity), цена (price), покупатель (buyer), дата (date). Функция
должна предусматривать запись данных в виде словаря в файл orders.json. При
записи данных указать величину отступа в 4 пробельных символа;
b. Проверить работу программы через вызов функции write_order_to_json() с передачей
в нее значений каждого параметра.
"""
import json


def write_order_to_json(item, quantity, price, buyer, date):
    with open('orders.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    with open('orders.json', 'w', encoding='utf-8') as file:
        orders = data['orders']
        good = {'item': item,
                'quantity': quantity,
                'price': price,
                'buyer': buyer,
                'date': date}
        orders.append(good)
        json.dump(data, file, indent=4, ensure_ascii=False)

write_order_to_json('iphone 14', '1', '116700', 'mr. Smith', '24.02.2022')
write_order_to_json('google pixel 5', '1', '100000', 'mrs. Wood', '21.09.2022')
