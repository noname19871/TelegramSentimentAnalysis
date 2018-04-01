import pandas as pd
import pymorphy2


def text_cleaner(text):
    # приводим весь текст к нижнему регистру
    text = text.lower()

    # оставляем только русские буквы и пробелы
    alphabet = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
    cleaned_text = ''
    for char in text:
        if (char[0] in alphabet) or (char == ' '):
            cleaned_text += char

    morph = pymorphy2.MorphAnalyzer()

    # лемматизируем
    result = []
    for word in cleaned_text.split():
        result.append(morph.parse(word)[0].normal_form)
    return ' '.join(result)


# Очищает датасет от мусора
# pos_csv - путь к файлу с позитивными примерами
# neg_csv - путь к файлу с негативными примерами
# out-csv - путь к файлу, куда нужно сохранить результат
def clean_csv(pos_csv, neg_csv, out_csv):

    # Считываем данные из файлов
    pos_data = pd.read_csv(pos_csv, sep=';', header=None)
    neg_data = pd.read_csv(neg_csv, sep=';', header=None)

    # Обьединяем данные в один датасет и оставляем только столбец с текстом и оценкой
    data = pd.concat([pos_data, neg_data])

    # присваиваем колонкам идентификаторы
    data.columns = ['text', 'mark']

    # очищаем данные в колонке с текстом от мусора
    data['text'] = data['text'].apply(text_cleaner)

    # сохраняем очищенную выборку в csv формат
    data.to_csv(out_csv)