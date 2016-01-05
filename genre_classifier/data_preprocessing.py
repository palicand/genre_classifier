import os

import essentia
import essentia.standard as st
import pandas as pd
from sklearn.pipeline import Pipeline
import sklearn.preprocessing as prep
import sklearn.decomposition as decomp

import log

__author__ = 'Andrej Palicka <andrej.palicka@merck.com>'


def pca(data, components):
    print(data)
    pca = decomp.PCA(n_components=components)

    if 'class' in data:
        transformed = pca.fit_transform(data[data.columns[:-1]])
        transformed = pd.DataFrame(transformed)
        transformed.index = data.index
        transformed['class'] = data['class']
    else:
        transformed = pca.fit_transform(data)
        transformed = pd.DataFrame(transformed)
        transformed.index = data.index
    print(transformed)
    return transformed

def import_file(full_path, frame_size,
                hop_size, sample_rate):
    logger = log.get_logger(__name__)
    pool = essentia.Pool()

    def extract_from_range(start_sec, end_sec=None):
        if end_sec is not None:
            end = end_sec * sample_rate - frame_size
        else:
            end = len(audio) - frame_size
        for fstart in range(start_sec * sample_rate,
                            end,
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

        return pool

    loader = st.MonoLoader(filename=full_path)
    audio = loader()
    window = st.Windowing(type='hann', size=frame_size)
    spectrum = st.Spectrum(size=frame_size)
    # get the first 60 seconds of track
    extracted_fv = extract_from_range(0)
    dynamic__complexity, loudness = st.DynamicComplexity(frameSize=
                                                         float(frame_size) / float(sample_rate))(audio)
    pool.add("lowlevel.loudness", loudness)
    pool.add("lowlevel.dynamic__complexity", dynamic__complexity)

    logger.debug("at the end we have %s", str(extracted_fv))

    return extracted_fv

def pool_to_series(pool):
    agg = st.PoolAggregator()
    aggregate = agg(pool)
    series = pd.Series()
    for key in aggregate.descriptorNames():
        try:
            series = series.append(pd.Series(aggregate[key],
                                             ["{0}_{1}".format(key, idx)
                                              for idx, _
                                              in enumerate(
                                                     aggregate[key])]))
        except TypeError:
            series = series.append(pd.Series(aggregate[key], [key]))
    return series

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
    names = []
    for base_dir, dir_names, file_names in os.walk(path):
        count = 0
        filtered = [name for name in file_names if name.endswith(".mp3")]
        for file_name in filtered:
            _, ext = os.path.splitext(file_name)
            full_name = os.path.join(base_dir, file_name)
            head, tail = os.path.split(base_dir)
            if tail == '':
                raise ValueError("Missing genre dir")
            genre = tail.lower()
            classes.append(genre)
            logger.info("Genre %s", genre)
            logger.info("Importing file %s", full_name)
            series = pool_to_series(import_file(full_name,
                                       frame_size, hop_size,
                                       sample_rate))
            names.append(file_name)
            logger.debug(series)

            feature_vectors.append(series)
    df = pd.DataFrame(feature_vectors,index=names)
    logger.info("classes %s", str(classes))
    df.insert(loc=len(df.columns), column="class", value=classes)
    return df
