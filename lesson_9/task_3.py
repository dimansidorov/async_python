"""
Написать функцию host_range_ping_tab(), возможности которой основаны на функции из примера 2.
Но в данном случае результат должен быть итоговым по всем ip-адресам, представленным в табличном формате
(использовать модуль tabulate). Таблица должна состоять из двух колонок
"""
from task_2 import host_range_ping
from tabulate import tabulate


def host_range_ping_tab(start_ip, end_ip):
    header = ('ip address', 'response')
    result = host_range_ping(start_ip, end_ip)
    print(tabulate(result, headers=header, stralign="center"))


if __name__ == '__main__':
    host_range_ping_tab('178.248.232.209', '178.248.232.229')
