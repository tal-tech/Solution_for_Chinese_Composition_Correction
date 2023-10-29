import os
import json
import re


def load_json(path):
    with open(path, 'r') as f:
        js = json.load(f)
    return js

def save_json(data, path):
    with open(path, 'w') as f:
        json.dump(data, f)

def read_text(path):
    with open(path, 'r') as f:
        text = f.readlines()
    text = [x.replace('\n','') for x in text]
    text = [x for x in text if len(x.strip())!=0]
    return text

def save_text(text_list, save_path):
    with open(save_path, 'w') as f:
        text_list = [x+'\n' for x in text_list]
        f.writelines(text_list)
    