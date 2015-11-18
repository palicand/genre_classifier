import os
import essentia

import essentia.standard as st
import numpy as np
import pandas as pd
import log

__author__ = 'Andrej Palicka <andrej.palicka@merck.com>'



def __import_file(full_path, frame_size,
                  hop_size, sample_rate):
    logger = log.get_logger(__name__)
    pool = essentia.Pool()

    def extract_from_range(start_sec, end_sec):
        for fstart in range(start_sec * sample_rate,
                            end_sec * sample_rate - frame_size,
                            hop_size
                            ):
            frame = audio[fstart:fstart + frame_size]
            s = spectrum(window(frame))

            # features
            mfcc = st.MFCC(inputSize=frame_size / 2 + 1)
            bands, coefs = mfcc(s)
            pool.add("lowlevel.mfcc", coefs)
            pool.add("lowlevel.mfcc_bands", bands)

            envelope = st.Envelope()
            envel = envelope(s)
            pool.add("lowlevel.envelope", envel)

            loudness = st.Loudness()
            pool.add("lowlevel.loudness", loudness(s))
        return pool


    loader = st.MonoLoader(filename=full_path)
    audio = loader()
    window = st.Windowing(type='hann', size=frame_size)
    spectrum = st.Spectrum(size=frame_size)
    # get the first 60 seconds of track
    extracted_fv = extract_from_range(0, 60)
    logger.debug("at the end we have %s", str(extracted_fv))
    return pool


def import_from_dir(path, frame_size=1024,
                    hop_size=512, sample_rate=44100
                    ):
    """Imports audio files residing on a given *path* as a data set . The input
    path should contain directories named after genres and each genre directory
    should contain audio files of that given genre."""
    logger = log.get_logger(__name__)
    print(logger)
    print(logger.parent)
    print(logger.propagate)
    logger.info("Starting import")
    logger.info("pd version %s", pd.__version__)
    feature_vectors = []
    classes = []
    agg = st.PoolAggregator()
    for base_dir, dir_names, file_names in os.walk(path):
        for file_name in file_names:
            _, ext = os.path.splitext(file_name)
            if ext != '.mp3':
                continue
            full_name = os.path.join(base_dir, file_name)
            head, tail = os.path.split(base_dir)
            if tail == '':
                raise ValueError("Missing genre dir")
            genre = tail.lower()
            classes.append(genre)
            logger.info("Genre %s", genre)
            logger.info("Importing file %s", full_name)
            aggregate = agg(__import_file(full_name,
                                          frame_size, hop_size,
                                          sample_rate))
            series = pd.Series()
            for key in aggregate.descriptorNames():
                try:
                    series = series.append(pd.Series(aggregate[key],
                                           ["{0}_{1}".format(key, idx)
                                              for idx,_
                                              in enumerate(aggregate[key])]))
                except TypeError:
                    series = series.append(pd.Series(aggregate[key], [key]))
            logger.debug(series)

            feature_vectors.append(series)
    df = pd.DataFrame(data=feature_vectors)
    logger.info("classes %s", str(classes))
    df.insert(loc=len(df.columns), column="class", value=classes)

    return df
