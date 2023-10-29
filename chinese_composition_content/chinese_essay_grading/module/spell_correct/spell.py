import sys 
import os
import logging 
logger = logging.getLogger(__name__)

pycorrector_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),"pycorrector")
sys.path.append(pycorrector_path)
from pycorrector import Corrector
from pycorrector import set_log_level
set_log_level()
para_key_temp = "paragraph_{}"
lm_model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),"model","people_chars_lm.klm")

class spellModel:
    def __init__(self, lm_model_path=lm_model_path):
        """
         lm_model_path: language model path, Default: abspath(__file__)/../model/people_chars_lm.klm
        """
        print('spell language model path', lm_model_path)
        self.lm_model_path = lm_model_path
        self.get_corrector()
    
    def get_corrector(self):
        logger.info("Loading model ...")
        self.corrector = Corrector(language_model_path=self.lm_model_path)

    def predict_correct(self, sent):
        corrected_sent, detail = self.corrector.correct(sent)
        return corrected_sent, detail
    
    def predict_detect(self, sent):
        detail = self.corrector.detect(sent)
        return detail

    def predict_paragraphs(self, paras, need_correct=True):
        """
         @params:
           paras: List, [ [p11,p12,p13], [p21, p22, p23] ], Texts needed to be checked and corrected. The notition pij represents a sentence whose sent id is j in paragraph i.
           need_correct: Bool,  If True, do the correction, otherwise, only check. Default True.
         @Return: 
           predict_result: Dict 
               {"misspelling_num": 错别字数量
                "grammar_mistake_sentence": 有语病的句子数量,
                "grammar_mistake_statistic":语病错误类型统计
                "grammar_mistake_info": 详细语病信息
                "correction_result":  整篇文章的纠错后结果  List, [ [p11,p12,p13], [p21, p22, p23] ]
                }
        """
        ret_dict = dict()
        if need_correct:
            ret_dict = self.predict_paragraphs_correct(paras)
        else:
            ret_dict = self.predict_paragraphs_detect(paras)
        return ret_dict
    def form_correct_detail_info(self, detail, offset):
        ret_dict = dict()
        ret_dict["type"] = "拼写错误"
        ret_dict["cor"] = detail[1]
        ret_dict["ori"] = detail[0]
        ret_dict["start"] = int(detail[2]+offset)
        ret_dict["end"] = int(detail[3]+offset)
        return ret_dict 
    
    def form_detect_detail_info(self, detail, offset):
        # detail ['因该', 4, 6, 'word']
        ret_dict = dict()
        ret_dict["type"] = "拼写错误"
        ret_dict["cor"] = "UNK"
        ret_dict["ori"] = detail[0]
        ret_dict["start"] = int(detail[1]+offset)
        ret_dict["end"] = int(detail[2]+offset)
        return ret_dict 

    def predict_paragraphs_correct(self, paras):
        ret_dict = dict()
        correct_para_list = []
        grammar_mistake_sentence = 0
        grammar_mistake_statistic = dict()
        grammar_mistake_info = []
        misspelling_num = 0
        
        for para_id, para in enumerate(paras):
            char_offset = 0
            correct_sents_list = []
            para_key = para_key_temp.format(para_id+1)
            for sent in para:
                corrected_sent, details = self.predict_correct(sent) # ('少先队员应该为老人让坐', [['因该', '应该', 4, 6]])
                correct_sents_list.append(corrected_sent)
                wrong_num_in_sent = len(details)
                grammar_mistake_sentence += 1 if wrong_num_in_sent>=1 else 0 
                misspelling_num += wrong_num_in_sent
                # detail 
                if wrong_num_in_sent>=1:
                    para_detail_info = {'paragraph':para_id+1, 'details':[]}
                    for detail in details:
                        tmp_detail_dict = self.form_correct_detail_info(detail, char_offset)
                        para_detail_info['details'].append(tmp_detail_dict)
                    grammar_mistake_info.append(para_detail_info)
                char_offset += len(sent)
            correct_para_list.append(correct_sents_list)
        # correction_result = "".join(correct_sents_list)
        grammar_mistake_statistic["spell_errors"] = misspelling_num
        ret_dict = dict(grammar_mistake_sentence = grammar_mistake_sentence,
                        grammar_mistake_statistic = grammar_mistake_statistic,
                        misspelling_num = misspelling_num,
                        grammar_mistake_info = grammar_mistake_info,
                        correction_result = correct_para_list)
        return ret_dict


    def predict_paragraphs_detect(self, paras):
        ret_dict = dict()
        # correct_sents_list = []
        grammar_mistake_sentence = 0
        grammar_mistake_statistic = dict()
        grammar_mistake_info = []
        misspelling_num = 0
        for para_id, para in enumerate(paras):
            char_offset = 0
            para_key = para_key_temp.format(para_id+1)
            for sent in para:
                details = self.predict_detect(sent) # [['因该', 4, 6, 'word']]
                # correct_sents_list.append(sent)
                wrong_num_in_sent = len(details)
                grammar_mistake_sentence += 1 if wrong_num_in_sent>=1 else 0 
                misspelling_num += wrong_num_in_sent
                # detail 
                if wrong_num_in_sent>=1:
                    para_detail_info = {'paragraph':para_id+1, 'details':[]}
                    for detail in details:
                        tmp_detail_dict = self.form_detect_detail_info(detail, char_offset)
                        para_detail_info['details'].append(tmp_detail_dict)
                    grammar_mistake_info.append(para_detail_info)
                char_offset += len(sent)
        #     correct_sents_list.append("\n")
        # else:
        #     correct_sents_list = correct_sents_list[:-1]
        # correction_result = "".join(correct_sents_list)
        grammar_mistake_statistic["spell_errors"] = misspelling_num
        ret_dict = dict(grammar_mistake_sentence = grammar_mistake_sentence,
                        grammar_mistake_statistic = grammar_mistake_statistic,
                        misspelling_num = misspelling_num,
                        grammar_mistake_info = grammar_mistake_info,
                        correction_result = paras)
        return ret_dict

        

if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    import json
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('[%(levelname)7s %(asctime)s %(module)s:%(lineno)4d] %(message)s',
                                    datefmt='%Y%m%d %I:%M:%S')
    handle = logging.StreamHandler()
    handle.setFormatter(formatter)
    logger.addHandler(handle)
    model = spellModel()
    sent = "少先队员应该为老人让座"
    print(model.predict_correct(sent))
    model.predict_detect(sent)
    sent = "少先队员因该为老人让坐"
    print(model.predict_correct(sent))
    model.predict_detect(sent)
    _input = [[sent, sent], [sent, sent]]
    print(json.dumps(model.predict_paragraphs_correct(_input)))
    print(model.predict_paragraphs_detect(_input))

