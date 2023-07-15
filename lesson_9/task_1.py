"""
1. Написать функцию host_ping(), в которой с помощью утилиты ping
будет проверяться доступность сетевых узлов.
Аргументом функции является список, в котором каждый сетевой узел
должен быть представлен именем хоста или ip-адресом.
В функции необходимо перебирать ip-адреса и проверять
их доступность с выводом соответствующего сообщения
(«Узел доступен», «Узел недоступен»). При этом ip-адрес
сетевого узла должен создаваться с помощью функции ip_address().
"""
import os
from ipaddress import ip_address
from socket import gethostbyname


def host_ping(hosts):
    result = []

    for host in hosts:
        name = host
        if isinstance(host, str | bytes | bytearray):
            host = gethostbyname(host)

        param = '-n' if os.name == 'nt' else '-c'
        host = ip_address(host)
        response = os.system(f'ping {param} 1 {host} > ping.log')
        if response:
            result.append((name, 'unreachable'))
        else:
            result.append((name, 'reachable'))

    return result


if __name__ == '__main__':
    res = host_ping(['google.com', '10.0.0.1', 'yandex.com', '10.0.0.2', 'gb.ru'])
    print(res)
