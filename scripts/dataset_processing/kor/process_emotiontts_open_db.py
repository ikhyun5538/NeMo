import argparse
import glob
import json
import sys
import importlib
import librosa
import logging
import re
import sys
import numpy as np

from pathlib import Path
from sklearn.model_selection import train_test_split
from welford import Welford
from time import gmtime
from time import strftime


#import nltk
#nltk.download('punkt')

#MODULE_PATH = str(Path('emotiontts_open_db/Codeset/Transformer-ParallelWaveGAN-based-Korean-TTS-master/utils/').resolve())
#sys.path.insert(0, MODULE_PATH)

#import text

parser = argparse.ArgumentParser(description = "Emotion TTS OpenDB dataset processing")
parser.add_argument("-d", "--data_root", required = True, default = None, type = str)
parser.add_argument("-s", "--speakers", required = False, nargs = '+', default = None, type = str)
args = parser.parse_args()

DATA_ROOT = Path(args.data_root).resolve()
MODULE_PATH = str([path for path in Path(DATA_ROOT).glob("**/utils")][0])
sys.path.insert(0, MODULE_PATH)
from text import korean

#{'avd', 'pfb', 'pfl', 'pma', 'nee', 'pfo', 'pfc', 'lmy', 'pml', 'adb', 'pfi', 'pmc', 'pfp', 'pmd', 'emg', 'neo', 'pmb', 'ada', 'pmj', 'nen', 'pfa', 'nem', 'pfd', 'pfm', 'emh', 'avb', 'add', 'ned', 'ava', 'neb', 'nec', 'emb', 'kih', 'adc', 'nea', 'pmi', 'ema', 'nel', 'emf', 'avc', 'nek'}

def build_metadata(data_root, speakers = None):
    meta = {} # {<file name> : {"audio_filepath" : <path>, "duration" : <sec> , "text : <transcipt>}}

    #speaker_re = re.compile('^(' + speakers + ')\d*$')
    speaker_re = re.compile('^(\w{3})\d*$')
    for path in Path(data_root).glob('**/*.wav'):
        match  = speaker_re.match(path.stem)
        if not match : 
            logging.error("Error : Unexpected file name, please check speaker regex, filename", 
                  "\n - regex : " + speaker_re ,
                  "\n - filename : " + filename)
        speaker = match.group(1)
        if speakers != None and not speaker in speakers:
            continue

        meta[path.stem] = {"audio_filepath" : str(path),
                           "duration" : librosa.get_duration(filename = path),
                           "speaker" : speaker}

    for path in Path(data_root).glob('**/*.txt'):
        if not path.stem in meta:
            continue

        #with path.open(encoding = 'utf-8-sig') as f:
        with path.open(encoding = 'utf-8-sig') as f:
            script = f.readline()
            script = korean.normalize(script)
            if not script:
                continue
            meta[path.stem]["text"] = script

    return meta

def build_manifest(meta, manifest_path):
    # Write the metadata to the manifest
    #with open(manifest_path, 'w', encoding = 'utf-8-sig') as fout:
    with open(manifest_path, 'w') as fout:
        for data in meta:
            metadata = {
                "audio_filepath": data['audio_filepath'],
                "duration": data['duration'],
                "text": data['text']}
            json.dump(metadata, fout, ensure_ascii=False)
            fout.write('\n')

def split_dataset(meta, random_state):
    train, test= train_test_split([*meta.values()], train_size = 0.8, random_state = random_state)
    #todo
    return train, test

def summary(speakers, train_list, test_list) :
    test_wf = Welford(np.array(list(map(lambda x : [x['duration'], len(x['text'])], test_list))))
    train_wf = Welford(np.array(list(map(lambda x : [x['duration'], len(x['text'])], train_list))))
    def print_sum(set_name , du_total, du_mean, text_mean, count) :
        du_total = strftime('%Hhr %Mmin', gmtime(du_total))
        print(f'{set_name} set\n - duration(total, mean) : {du_total}, {du_mean:.2f}sec\n - text_len(mean) : {text_mean:.2f}\n - count(total) : {count}')


    print(f'Speakers : {speakers}')

    du_total = train_wf.mean[0]*train_wf.count
    du_mean = train_wf.mean[0]
    text_mean = train_wf.mean[1]
    count = train_wf.count
    print_sum('Train' , du_total, du_mean, text_mean, count)

    du_total = test_wf.mean[0]*test_wf.count
    du_mean = test_wf.mean[0]
    text_mean = test_wf.mean[1]
    count = test_wf.count
    print_sum('Test' , du_total, du_mean, text_mean, count)

    train_wf.merge(test_wf)
    du_total = train_wf.mean[0]*train_wf.count
    du_mean = train_wf.mean[0]
    text_mean = train_wf.mean[1]
    count = train_wf.count
    print_sum('Total' , du_total, du_mean, text_mean, count)
    


def main():
    speakers = args.speakers

    meta_dict = build_metadata(DATA_ROOT, speakers)
    train_list, test_list = split_dataset(meta_dict)
    
    summary(speakers, train_list, test_list)

    train_path = DATA_ROOT / 'train_manifest.json'
    test_path = DATA_ROOT / 'test_manifest.json'
    #build_manifest(train_list, train_path) 
    #build_manifest(test_list, test_path) 
    print(train_path)
    print(test_path)

def test_normalize(text):
    res = korean.normalize(text)
    if not res:
        print(text)
        print("=" * 30)

if __name__ == '__main__':
    main()
