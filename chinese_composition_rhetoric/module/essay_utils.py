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

def split_content(para):
    sents = re.split(r'(。”|！”|？”|\.”|!”|\?”|。"|！"|？"|。|！|!)', para)
    res = [sents[i]+sents[i+1] for i in range(0, len(sents)-1, 2)]
    if len(sents) % 2 == 1:
        res.append(sents[-1])
    res = [x.strip() for x in res if len(x.strip())>0]
    return res
    
def is_exist_in_dict(input_dict, key):
    is_exist = False
    if key in input_dict:
        value = input_dict[key]
        value_type = type(value)    
        # 对于 string and array
        if value_type is str or value_type is list:
            is_exist = True if len(value) > 0 else False
        # 对于 int
        elif value_type is int:
            is_exist = True
        else:
            raise ValueError('value type is not correct!')
    return is_exist

def map_grade(grade):
    grade_key =  ''
    if grade >= 0 and grade <= 6:
        grade_key = 'primary'
    elif grade >=7 and grade <= 9:
        grade_key = 'junior'
    elif grade >= 10 and grade <= 12:
        grade_key = 'senior'
    else:
        raise ValueError('Invalid input for grade={}, must be integer between 0 and 12'.format(grade))
    return grade_key

def is_Chinese(text):
    for ch in text:
        if '\u4e00' <= ch <= '\u9fff':
            return True
    return False
    