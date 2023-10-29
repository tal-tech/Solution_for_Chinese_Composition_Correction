import os
import re
from pyltp import Segmentor, Postagger
from essay_utils import split_content
import time

# 统一处理及基本统计特征
class Base(object):
    def __init__(self):
        self.init_ltp_model()
        
    def init_ltp_model(self):
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        LTP_DATA_DIR = os.path.join(root, 'model/ltp_data_v3.4.0')
        # LTP_DATA_DIR = '/share/作文批改/src/工程代码/v01/model/ltp_data_v3.4.0'
        print('Initialize LTP segmentor...')
        cws_model_path = os.path.join(LTP_DATA_DIR, 'cws.model')  # 分词模型路径，模型名称为`cws.model`
        self.segmentor = Segmentor()  # 初始化实例
        self.segmentor.load(cws_model_path)  # 加载模型

        print('Initialize LTP POS Tagger...')
        pos_model_path = os.path.join(LTP_DATA_DIR, 'pos.model')  # 词性标注模型路径，模型名称为`pos.model`
        self.postagger = Postagger() # 初始化实例
        self.postagger.load(pos_model_path)  # 加载模型

    def release(self):
        print('Release LTP models in Base...')
        self.segmentor.release()
        self.postagger.release()
    
    def union_symbol(self, s):
        dic = {
            ',':'，', 
            ';':'；',
            '!':'！',
            '?':'？',
            ':':'：',
            '[' : '【',
            ']' : '】',
            '(' : '（',
            ')' : '）'
        } 
        for d, d_ in dic.items():
            s = s.replace(d, d_)
        return s

    # 符号统一化
    def union_content(self, para_list):
        return [self.union_symbol(x) for x in para_list]

    # 将段落划分成句子
    def split_para_to_sent(self, para_list):
        sentence = []
        for para in para_list:
            sentence += split_content(para)
        self.sents = sentence
        return sentence

    #  # 将一个长句切分为短句
    # def split_sentence(self, sentence):
    #     short_sents = re.split(r'(、|，|；|,|;)', sentence)
    #     res = [short_sents[i]+short_sents[i+1] for i in range(0, len(short_sents)-1, 2)]
    #     if len(short_sents) % 2 == 1:
    #         res.append(short_sents[-1])
    #     res = [x.strip() for x in res if len(x.strip())>0]
    #     return res
    # # 素养课长短句定义
    # def get_long_short_sentence(self, sent_list):
    #     long_short_sentence = []
    #     long_short_sentence_count = 0
    #     for sent in sent_list:
    #         long_word_count = len(sent)
    #         short_sents = self.split_sentence(sent)
    #         short_word_count = 0 if len(short_sents)==0 else min([len(x) for x in short_sents])
    #         # 长句字数:短句字数≧2:1, 则判断为长短句
    #         if short_word_count > 0 and long_word_count/short_word_count >= 2:
    #             long_short_sentence.append(sent)
    #             long_short_sentence_count += 1
    #     return long_short_sentence, long_short_sentence_count

    def get_basic_info(self, sent_list):
        # st = time.time()
        conj_num = 0
        res_dict = {
            'total_char_num':0,
            'total_term_num':0,
            'term_type':{
                'noun_num':0,
                'verb_num':0,
                'adj_num':0,
                'adv_num':0
            },
            'conj_num':0,
            'adj_adv_info':{},
            'total_sentence_num':len(sent_list),
            # 'sentence_type':{
            #     'long_sentence_num':0,
            #     'short_sentence_num':0
            # }
        }
        symbols = [',','.',';','!','?','，','。','！','？','"','“','”',':','：']
        used_word = []
        for sent in sent_list:
            # # 句特征
            # sent_length = len(sent)
            # if sent_length >= 80:
            #     res_dict['sentence_type']['long_sentence_num'] += 1
            # elif sent_length < 10:
            #     res_dict['sentence_type']['short_sentence_num'] += 1
            # 词语特征
            res_dict['total_char_num'] += len(sent)
            words = self.segmentor.segment(sent)  # 分词
            postags = self.postagger.postag(words)     # postag
            for i in range(len(postags)):
                postag = postags[i]
                word = words[i]
                # 名词
                if postag == 'n':
                    res_dict['term_type']['noun_num'] += 1
                # 动词
                elif postag == 'v':
                    res_dict['term_type']['verb_num'] += 1
                # 形容词
                elif postag == 'a':
                    res_dict['term_type']['adj_num'] += 1
                    if word in res_dict['adj_adv_info']:
                        res_dict['adj_adv_info'][word] += 1
                    else:
                        res_dict['adj_adv_info'][word] = 1
                # 副词
                elif postag == 'd':
                    res_dict['term_type']['adv_num'] += 1
                    if word in res_dict['adj_adv_info']:
                        res_dict['adj_adv_info'][word] += 1
                    else:
                        res_dict['adj_adv_info'][word] = 1
                # 连词
                elif postag == 'c':
                    res_dict['conj_num'] += 1
                    # print('word',word)
                    # print('postag',postag)
                    # word_feature['连词'].append(word)
                if word not in symbols and word not in used_word:
                    res_dict['total_term_num'] += 1
                    used_word.append(word)
        return res_dict

    def get_base_result(self, para_list):
        st = time.time()
        para_list = self.union_content(para_list)
        sent_list = self.split_para_to_sent(para_list)
        basic_info = self.get_basic_info(sent_list)
        return para_list, sent_list, basic_info, time.time()-st
        
