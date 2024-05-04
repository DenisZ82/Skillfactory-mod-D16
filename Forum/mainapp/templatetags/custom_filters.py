from django import template
import string

register = template.Library()

BAD_WORDS = ['собака', 'ученые', 'антиглобализм']


class StrException(Exception):
    def __str__(self):
        return 'Фильтр censor принимает только строковый тип данных'


@register.filter()
def censor(text):
    if not isinstance(text, str):
        raise StrException
    else:
        text_list = text.split()
        censor_list = []

        for word in text_list:
            clean_word = ''.join(c for c in word if c not in string.punctuation)
            if clean_word.lower() in BAD_WORDS:
                censor_word = clean_word[0] + (len(clean_word) - 1) * '*'
                censor_list.append(word.replace(clean_word, censor_word))
            else:
                censor_list.append(word)

    return ' '.join(censor_list)
