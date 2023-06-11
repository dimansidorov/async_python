"""
Каждое из слов «class», «function», «method» записать в байтовом типе без преобразования в последовательность кодов
(не используя методы encode и decode) и определить тип, содержимое и длину соответствующих переменных.
"""

class_word = b'class'
func_word = b'function'
method_word = b'method'

for item in [class_word, func_word, method_word]:
    print(f'{type(item)} - {item} - {len(item)}')
