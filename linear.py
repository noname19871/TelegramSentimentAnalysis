from sklearn.feature_extraction.text import TfidfVectorizer

from sklearn.externals import joblib
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import GridSearchCV

from cleaner import text_cleaner
import pandas as pd

model_filename = 'model/classifier-linear.joblib.pkl'
features_filename = 'model/features-linear.joblib.pkl'


def train(train_csv):
    # считываем подготовленный датасет
    data = pd.read_csv(train_csv, index_col=0).dropna()

    # высчитываем веса слов по формуле TF_IDF
    word_weights = TfidfVectorizer(min_df=1, max_df=0.6, analyzer="word", ngram_range=[1,3])

    X = word_weights.fit_transform(data['text'])

    y = data['mark']

    parameters = {
        'loss': ('log', 'modified_huber'),
        'penalty': ['none', 'l1', 'l2', 'elasticnet'],
        'alpha': [0.001, 0.0001, 0.00001, 0.000001]
    }

    #
    clf = SGDClassifier(max_iter=1000)
    gs_clf = GridSearchCV(clf, parameters, cv=None, n_jobs=-1)
    gs_clf = gs_clf.fit(X, y)

    joblib.dump(gs_clf, model_filename, compress=3)
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
        return [[1, 1]]
    new_data = word_weights.transform(tmp_data)
    predicted = clf.predict_proba(new_data)
    return predicted
