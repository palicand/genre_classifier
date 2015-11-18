#!/usr/bin/env python
import sys
import genre_classifier.log as log
import argparse
import essentia.standard as st
import numpy as np


__author__ = 'Andrej Palicka <andrej.palicka@merck.com>'

import genre_classifier.data_preprocessing as dp


def __parse_arguments(argv):
    parser = argparse.ArgumentParser(description="Something")
    parser.add_argument("data_location", type=str)
    parser.add_argument("output", type=str)
    parser.add_argument("--frame_size", type=int, default=1024)
    parser.add_argument("--hop_size", type=int, default=512)

    return parser.parse_args(argv)

def mfcc_wrapper(**kwargs):
    def wrapper(spectrum):
        _, coef = f(spectrum)
        return coef
    f = st.MFCC(**kwargs)

    return wrapper



def main(argv=None):
    if argv == None:
        argv = sys.argv[1:]
    args = __parse_arguments(argv)
    data = dp.import_from_dir(args.data_location)
    data.to_csv(args.output)


if __name__ == '__main__':
    main()
