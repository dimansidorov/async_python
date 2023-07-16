"""
2. Написать функцию host_range_ping() для перебора ip-адресов из заданного диапазона.
Меняться должен только последний октет каждого адреса.
По результатам проверки должно выводиться соответствующее сообщение.
"""
from ipaddress import ip_address
from socket import gethostbyname

from task_1 import host_ping


def host_range_ping(start_ip, end_ip):
    *start, s_last_octet = start_ip.split('.')
    *end, e_last_octet = end_ip.split('.')

    if start != end or int(e_last_octet) > 255 or int(s_last_octet) > 255:
        raise ValueError('Only the last octet changes')

    ip_addr = ip_address(gethostbyname(start_ip))
    hosts = [ip_addr + i for i in range(int(e_last_octet) - int(s_last_octet) + 1)]
    return host_ping(hosts)


if __name__ == '__main__':
    res = host_range_ping('178.248.232.209', '178.248.232.229')
    print(res)
