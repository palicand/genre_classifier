# Genre Classifier

Done as a semestral Project for MI-VMW.

## Installation
This packages has the following requirements:
 * Python 2.7
 * node.js
 * Essentia

If you have these requirements, run `install.sh`.

## How to run
To build your dataset, run `./bin/extract_features.py <data_dir> <output_file>`.
The data dir should contain subdirs with the name of the genre and each
subdir should contain audio files.
The script will process them and output a CSV.

To train the model, execute `train_model.py <dataset> <model_loc>`. It will
load the previously extracted data set and train the model,
saving it to the model_loc.

To start the server, you can either execute directly `python server.py <path_to_model>`
to run a single-process Flask server, or execute `gunicorn -w n server:app`
to execute it with *n* workers. The server will be available on `localhost:5000`
if run in the former mode, or `localhost:8000` if run in the latter.

## How to use

After you succesfully execute the server, simply open the above-mentioned
location in your browser. There you can upload your desired audio files
and have them classified.