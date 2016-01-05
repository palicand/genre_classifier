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
        leave_p_out = cv.LeavePOut(len(x), 4)
        model = grid_search.GridSearchCV(model_cls(),
                                         model_parameters,
                                         cv=3, n_jobs=4,
                                         scoring="f1_macro",
                                         )
        model.fit(x.values, y["class"].values)
        print("Ideal parameters {0}".format(model.best_params_))
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
    y = pd.DataFrame(y, columns=['class'])
    #encoder = prep.LabelEncoder()
    #y = pd.DataFrame(encoder.fit_transform(y), columns=["class"])
    #print("Classes %s", str(encoder.classes_))
    x_train, x_test, y_train, y_test = cv.train_test_split(x,
                                                           y,
                                                           test_size=0.3,
                                                           stratify=y.values)
    config = [
        {
            "C":[0.1, 0.5, 1, 2, 4, 8, 10, 100],
            "kernel": ["linear"],
            "probability": [True]
        },
        {
            "C":[0.1, 0.5, 1, 2, 4, 8, 10, 100],
            "kernel": ["poly"],
            "degree": [2, 3, 4, 5],
            "coef0": [0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 2, 4, 8, 16],
            "probability": [True],
        },
        {
            "C":[0.1, 0.5, 1, 2, 4, 8, 10, 100],
            "kernel": ["sigmoid"],
            "probability": [True],

        },
        {
            "C":[0.1, 0.5, 1, 2, 4, 8, 10, 100],
            "kernel": ["rbf"],
            "probability": [True],
        }
    ]
    logger.info("training")
    if args.config is not None:
        with open(args.config) as config_file:
            config = json.load(config_file)
    model = train_model(x_train, y_train, config)
    logger.info("trained")
    y_predict = model.predict(x_test)
    logger.info("true: %s predicted: %s", str(y_test["class"].values), str(y_predict))
    score = metrics.f1_score(y_test, y_predict,
                             average="macro")
    print("Simple score {0}".format(model.score(x_test, y_test)))
    print("F1 score {0}".format(score))
    model = train_model(x, y, model.best_params_)
    joblib.dump(model, args.output)



if __name__ == '__main__':
    main()
