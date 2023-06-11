"""
Каждое из слов «разработка», «сокет», «декоратор» представить в строковом формате и проверить тип и
содержание соответствующих переменных. Затем с помощью онлайн-конвертера преобразовать строковые представление в
формат Unicode и также проверить тип и содержимое переменных.
"""

dev = 'разработка'
socket = 'сокет'
wrapper = 'декоратор'


for word in [dev, socket, wrapper]:
    print(f'{type(word)} - {word}')


unicode_dev = '\u0440\u0430\u0437\u0440\u0430\u0431\u043e\u0442\u043a\u0430'
unicode_socket = '\u0441\u043e\u043a\u0435\u0442'
unicode_wrapper = '\u0434\u0435\u043a\u043e\u0440\u0430\u0442\u043e\u0440'


for word in [unicode_dev, unicode_socket, unicode_wrapper]:
    print(f'{type(word)} - {word}')
