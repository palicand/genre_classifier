import logging
import logging.config
import os

import yaml

__author__ = 'Andrej Palicka <andrej.palicka@merck.com>'

def __static_vars(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func

    return decorate


def setup_logging(
        default_path='logging.yaml',
        default_level=logging.INFO,
        env_key='LOG_CFG'
):
    """Setup logging configuration

    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = yaml.load(f.read())
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


@__static_vars(setup_done=False)
def get_logger(name=None):
    if not get_logger.setup_done:
        setup_logging()
        get_logger.setup_done = True
    return logging.getLogger(name)

