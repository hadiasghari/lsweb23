# Script which applies our easy-German classifier on our Oscar subset (.de websites with Curlie categories)
# Author: Freya Hewett & Hadi Asghari
# Version: 2023.02

import argparse
import os
import subprocess
import json
import pickle
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.layers import TextVectorization
import textstat
textstat.set_lang("de")

os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

parser = argparse.ArgumentParser()
parser.add_argument(
    "--input_file", 
    help="path where input files are saved",
    default="./data/oscar-subset.jsonl"
)
parser.add_argument(
    "--output_file", 
    help="path to output csv file", 
    default="./data/oscar-classified.csv"
)
args = parser.parse_args()

# load model & its text-vectorization layer
model = keras.models.load_model('model/mbow-alldata')
pkl = pickle.load(open("model/mbow-alldata/textvectorizer.pickle", "rb"))
vectorize = TextVectorization.from_config(pkl['config'])
vectorize.set_weights(pkl['weights'])

s = subprocess.getoutput("wc -l " + args.output_file)
try:
    already_parsed = int(s.split(" ")[0])
except:
    already_parsed = 0
print(f"Skipping first {already_parsed} records", flush=True)

with open(args.input_file) as f:
    with open(args.output_file, 'a') as output_file:
        for n, line in enumerate(f):
            if n % 10000 == 0:
                print("*", flush=True, end="")
            if n < already_parsed:
                continue
            js = json.loads(line)
            text = js['content']
            v = vectorize([text])
            pp = model(v, training=False)  # call like this in loop (not with predict())
            classifier_score = np.round(float(pp), 3)
            assert 0 <= classifier_score <= 1  # sanity check
            readability = textstat.wiener_sachtextformel(text, 4)  # for statistics
            char_count = len(text)
            # (note, to save space, the url part after '?' can be removed) 
            # url = js['url'][0:js['url'].find('?')+1] if '?' in js['url'] else js['url']
            # output with tab separation-- since some urls have commas
            output_file.write(js['url']+'\t'+js['domain']+'\t'+js['domcat']+'\t'+str(readability)+'\t'+str(classifier_score)+'\t'+str(char_count)+'\n')

print("\nProcessed:", n + 1)

