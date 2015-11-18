#!/usr/bin/env python
import argparse
import json
import sys
import pandas as pd
from sklearn import metrics
from sklearn.externals import joblib
import sklearn.svm as svm
import sklearn.grid_search as grid_search
import sklearn.cross_validation as cv
import sklearn.preprocessing as prep
import genre_classifier.log as log

__author__ = 'Andrej Palicka <andrej.palicka@merck.com>'


def train_model(x, y, model_parameters, model_cls=svm.SVC):
    """Trains a model on a *training set*.
       Parameters:
       *training_set* should be a dataframe-like object
       *args* should either be a dict, or a list of dicts. If a dict is provided,
       it will be used for initializing a model. If a list is provided,
       the gridsearch will be run on those grids.
       *model_cls* should be a sklearn class for a desired classifier. Default
       is SVC.
       Returns a *sklearn* model."""
    logger = log.get_logger(__name__)
    if isinstance(model_parameters, list):

        model = grid_search.GridSearchCV(model_cls(),
                                         model_parameters,
                                         cv=2)
        model.fit(x.values, y["class"].values)
    else:
        model = model_cls(**model_parameters)
        model.fit(x.values, y["class"].values)
    return model


def __parse_arguments(argv):
    parser = argparse.ArgumentParser(description="Something")
    parser.add_argument("data_location", type=str)
    parser.add_argument("output", type=str)
    parser.add_argument("--config", type=str, default=None)
    return parser.parse_args(argv)

def main(argv=None):
    logger = log.get_logger(__name__)
    if argv == None:
        argv = sys.argv[1:]
    args = __parse_arguments(argv)
    df = pd.DataFrame.from_csv(args.data_location)
    x = df[df.columns[:-1]]
    y = df["class"]
    encoder = prep.LabelEncoder()
    y = pd.DataFrame(encoder.fit_transform(y), columns=["class"])
    x_train, x_test, y_train, y_test = cv.train_test_split(x,
                                                           y,
                                                           test_size=0.3)
    config = [
        {
            "C":[1, 2, 4, 8, 10, 100, 100],
            "kernel": ["linear"]
        },
        {
            "C":[1, 2, 4, 8, 10, 100, 100],
            "kernel": ["poly"],
            "degree": [2, 3, 4, 5],
            "coef0": [0.0, 0.2, 0.4, 0.6]
        },
        {
            "C":[1, 2, 4, 8, 10, 100, 100],
            "kernel": ["sigmoid"]
        },
        {
            "C":[1, 2, 4, 8, 10, 100, 100],
            "kernel": ["rbf"]
        }
    ]
    if args.config is not None:
        with open(args.config) as config_file:
            config = json.load(config_file)
    model = train_model(x_train, y_train, config)
    y_predict = model.predict(x_test)
    score = metrics.f1_score(y_test, y_predict, df["class"].unique(),
                             average="micro")
    print("F1 score {0}".format(score))
    print("Ideal parameters {0}".format(model.best_params_))
    model = train_model(x, y, model.best_params_)
    joblib.dump(model, args.output)



if __name__ == '__main__':
    main()
