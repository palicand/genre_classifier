from sklearn.externals import joblib

__author__ = 'Andrej Palicka <andrej.palicka@merck.com>'


def load_classifier(path):
    return joblib.load(path)
