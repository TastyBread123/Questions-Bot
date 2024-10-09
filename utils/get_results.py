def get_results(dop_texts: dict[str, str], percent: int):
    """
    Получает результат по принципу: если процент прохождения больше или равен текущему результату в цикле и меньше следующего, то он считается верным.
    При дохождении до конца списка (то есть отсутствие следующего элемента), последний результат считается правильным

    dop_texts: Словарь с результатами
    percent: Процент прохождения викторины
    """

    dop_texts = dict(sorted(dop_texts.items()))

    if not dop_texts.get('-1') is None:
        return dop_texts['-1']

    dop_texts_keys = list(dop_texts.keys())

    for dop_text in range(len(dop_texts_keys)):
        dop_text_key = dop_texts_keys[dop_text]
        if dop_text - (len(dop_texts_keys) - 1) == 0:
            return dop_texts[dop_text_key]

        elif percent >= int(dop_texts_keys[dop_text]) and percent < int(dop_texts_keys[dop_text + 1]):
            return dop_texts[dop_text_key]

    return "-"