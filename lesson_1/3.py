"""
3. Определить, какие из слов «attribute», «класс», «функция», «type» невозможно записать в байтовом типе.
"""

attr_word = 'attribute'
class_word = 'класс'
func_word = 'функция'
type_word = 'type'

for word in [attr_word, class_word, func_word, type_word]:
    try:
        _ = bytes(word, 'ascii')
    except UnicodeEncodeError:
        print(f'"{word}" невозможно преобразовать в байты')
