
__author__ = 'Andrej Palicka <andrej.palicka@merck.com>'
from flask import Flask, render_template, jsonify, abort, request
import sys
import os
import argparse
import re
import pandas as pd
import genre_classifier.classifier
import genre_classifier.data_preprocessing
import essentia.standard as st
app = Flask(__name__)
classifier = genre_classifier.classifier.load_classifier("../data/model.pkl")

HTML_REGEX = re.compile(r'.+?\.html')

@app.route("/api/process_file", methods=['POST'])
def process_files():
    app.logger.debug(request.files)
    for key, uploaded_file in request.files.viewitems():
        extension = os.path.splitext(key)[1]
        tmp_file_name = os.tempnam()
        tmp_file_name += extension
        uploaded_file[0].save(tmp_file_name)
        data = genre_classifier.data_preprocessing.import_file(tmp_file_name,
                                                               frame_size=1024,
                                                               hop_size=512,
                                                               sample_rate=44100)
        data = genre_classifier.data_preprocessing.pool_to_series(data)
        app.logger.debug(data)

        prediction = classifier.predict_proba(data)
        amplitude = st.MonoLoader(filename=tmp_file_name)()
        #amplitude = []
        return jsonify({"prediction": zip(classifier.classes_,
                                               prediction[0].tolist()),
                        "amplitude": amplitude[:-1:1000].tolist()})


@app.route('/', defaults={'path': 'index.html'})
@app.route('/static/<path:path>')
def catch_all(path):
    app.logger.debug(classifier.classes_)
    if HTML_REGEX.match(path) is not None:
        app.logger.debug("Loading %s", path)
        return render_template(path)
    else:
        app.logger.debug("Loading %s", path)
        try:
            with open(path) as server_file:
                return server_file.readall()
        except IOError:
            return abort(404)


def parse_args(argv):
    parser = argparse.ArgumentParser(description="Server")
    parser.add_argument("model_location", type=str, default="../data/model.pkl")
    return parser.parse_args(argv)


def main():
    global classifier
    args = parse_args(sys.argv[1:])
    classifier = genre_classifier.classifier.load_classifier(args.model_location)
    app.logger.debug(classifier.classes_)
    app.debug = True
    app.run()

if __name__ == '__main__':
    main()