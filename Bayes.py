from sklearn.feature_extraction.text import TfidfVectorizer

from sklearn.externals import joblib
from sklearn.naive_bayes import MultinomialNB
from cleaner import text_cleaner
import pandas as pd

model_filename = 'model/classifier.joblib.pkl'
features_filename = 'model/features.joblib.pkl'


def train(train_csv):
    # считываем подготовленный датасет
    data = pd.read_csv(train_csv, index_col=0).dropna()

    # высчитываем веса слов по формуле TF_IDF
    word_weights = TfidfVectorizer(min_df = 2, max_df = 0.8, analyzer="word", ngram_range=[1,3])

    X = word_weights.fit_transform(data['text'])

    y = data['mark']

    # наивный байес
    clf = MultinomialNB()
    clf.fit(X,y)

    joblib.dump(clf, model_filename, compress=3)
    joblib.dump(word_weights,features_filename,compress=3)


def predict(in_data):
    word_weights = joblib.load(features_filename)
    clf = joblib.load(model_filename)

    tmp_data = []
    for sentence in in_data:
        new_sentence = text_cleaner(sentence)
        if new_sentence != '':
            tmp_data.append(text_cleaner(sentence))

    if len(tmp_data) == 0:
        return [[0, 0]]
    new_data = word_weights.transform(tmp_data)
    predicted = clf.predict_proba(new_data)
    return predicted

