"""
Преобразовать слова «разработка», «администрирование», «protocol», «standard» из строкового представления
в байтовое и выполнить обратное преобразование (используя методы encode и decode).
"""

dev = 'разработка'
admin = 'администрирование'
protocol = 'protocol'
standard = 'standard'

words_list = [dev, admin, protocol, standard]
encoded_list = []
for word in words_list:
    e_word = word.encode('utf-8')
    print(f'{word} -> {e_word}')
    encoded_list.append(e_word)

print()

for item in encoded_list:
    word = item.decode('utf-8')
    print(f'{item} -> {word}')

