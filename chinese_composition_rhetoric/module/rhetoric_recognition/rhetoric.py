import os
import sys
import re
# root = os.path.split(os.path.abspath(__file__))[0]
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(root, 'text_classification'))
sys.path.append(os.path.join(root, 'rhetoric_recognition'))
from rhetoric_config import rhe_key_map, model_config, pattern_config
# from model.bert import BertForTextClassification
# from model.RCNN import RCNN
# from model.LSTM import LSTMClassifier
from inference import TextClassifier

class Rhetoric(object):
    def __init__(self, key_list=list(rhe_key_map.keys())):
        self.key_list = key_list
        # 模型初始化
        # embd_path = model_config['embd_path']
        # BERT_ROOT_PATH = model_config['BERT_ROOT_PATH']
        self.model_dict = {}
        print('Load rhetoric models...')
        for key in key_list:
            if key in model_config:
                config_ = model_config[key]
                # if 'embd_path' in config_:
                #     embd_path = config_['embd_path']
                # else:
                #     embd_path = model_config['embd_path']
                embd_path = config_['embd_path']
                if config_['use_bert']:
                    pretrained_model_path = config_['model_config_lst'][0]['pretrained_model_path']
                    model = TextClassifier(embd_path, config_['checkpoint_lst'], config_['model_config_lst'], pretrained_model_path)
                else:
                    model = TextClassifier(embd_path, config_['checkpoint_lst'], config_['model_config_lst'])
                self.model_dict[key] = model
        # 通用函数
    def match_pattern(self, text, pattern_list):
        for pat in pattern_list:
            if re.match(pat, text):
                return True
        return False

    # 分类
    def classify(self, sent_list, key):
        model = self.model_dict[key]
        max_seq_len = model_config[key]['max_seq_len'] if 'max_seq_len' in model_config[key] else 80
        need_mask = model_config[key]['need_mask'] if 'need_mask' in model_config[key] else False
        print('{}: max_seq_len={}, need_mask='.format(key, max_seq_len),need_mask)
        pred_list, proba_list = model.predict_all_mask(sent_list, max_seq_len=max_seq_len, max_batch_size=10, need_mask=need_mask)
        pos_sent_list = [sent_list[i] for i in range(len(pred_list)) if pred_list[i]==1]
        return pos_sent_list, pred_list, proba_list

    # # 反问
    # def get_fanwen(self, sent_list):
    #     pred_list, match_list = [], []
    #     for sent in sent_list:
    #         is_match = self.match_pattern(sent, pattern_config['fanwen'])
    #         if is_match:
    #             pred_list.append(1)
    #             match_list.append(sent)
    #         else:
    #             pred_list.append(0)
    #     return match_list, pred_list, len(match_list)

    # 反问
    def get_fanwen(self, sent_list):
        match_list, pred_list, proba_list = self.classify(sent_list, 'fanwen')
        return match_list, pred_list, len(match_list)

    # 设问
    def get_shewen(self, sent_list):
        match_list, pred_list, proba_list = self.classify(sent_list, 'shewen')
        return match_list, pred_list, len(match_list)

    # 比喻
    def get_analogy(self, sent_list):
        match_list, pred_list, proba_list = self.classify(sent_list, 'analogy')
        return match_list, pred_list, len(match_list)
    # 拟人
    def get_personification(self, sent_list):
        match_list, pred_list, proba_list = self.classify(sent_list, 'personification')
        return match_list, pred_list, len(match_list)
    # 排比
    def get_parallelism(self, sent_list):
        match_list, pred_list, proba_list = self.classify(sent_list, 'parallelism')
        return match_list, pred_list, len(match_list)

    def get_all_rhetorics(self, original_sent_list):
        sent_list = [x['original_text'] for x in original_sent_list]
        rhetoric_info = {
            'num': 0,
            'info': {}
        }
        for key in self.key_list:
            match_list, pred_list, match_num = [], [], 0
            if key == 'fanwen':
                match_list, pred_list, match_num = self.get_fanwen(sent_list)
            elif key == 'shewen':
                match_list, pred_list, match_num = self.get_shewen(sent_list)
            elif key == 'analogy':
                match_list, pred_list, match_num = self.get_analogy(sent_list)
            elif key == 'personification':
                match_list, pred_list, match_num = self.get_personification(sent_list)
            elif key == 'parallelism':
                match_list, pred_list, match_num = self.get_parallelism(sent_list)
            rhetoric_info['info'][key] = {'pred_result':pred_list,'match_result':match_list}
            rhetoric_info['num'] += match_num
        return rhetoric_info


if __name__ == "__main__":
    sent_list = [
        '告别了小学的生活，告别了我亲爱的母校，瞧，初中的大门正向我招手，步入中学的大门。', # niren 1
        '不知是怎么一回事，花儿们一朵朵都探出了小脑袋瓜子，看着天，开心的笑了。', # niren 1
        '老玫瑰颤颤巍巍地说：“快去吧，它毕竟是你以前的主人，它现在危在旦夕，你总不能见死不救吧！”' # niren 1
        '每当我回想起这件事时，总是想：如果一个人一直拿第一名，或者没有坚持到最后一刻，那他又会有什么成长和进步呢？', # fanwen 1
        '哎，考的不好本来就很难受，还要给家长签名，这不是雪上加霜吗？啊！', # fanwen 1
        '平日里他们在课上开小差，一到期末考试冲刺周，他们便会发疯似地学习，你看小武正在埋头苦啃书本呢，在这几天他们将会变得对什么都不闻不问，进入了“忘我”境界，缺点是，他们在这几天变得易暴易怒，谁打扰了他的复习进度他们将会大打出手，他们追人时像一头倔驴，跑遍整个教学楼也不会轻易放过他们，跟着那人一条路走到黑，什么也不怕，可这种“平日不烧香，急时抱佛脚”的做法，哪比得上平日就好好学习的同学呢？', # fanwen 0
        '五颜六色的风筝在天空中上下翻飞，看，那是“燕子”，那是“山鹰”，那是“大蜈蚣”，它们把天空点缀得特别美丽。',
        '五颜六色的风筝在天空中上下翻飞，看，那是“燕子”，那是“山鹰”，那是“大蜈蚣”，它们把天空点缀得特别美丽。',
        '五颜六色的风筝在天空中上下翻飞，看，那是“燕子”，那是“山鹰”，那是“大蜈蚣”，它们把天空点缀得特别美丽。',
        '五颜六色的风筝在天空中上下翻飞，看，那是“燕子”，那是“山鹰”，那是“大蜈蚣”，它们把天空点缀得特别美丽。',
        '五颜六色的风筝在天空中上下翻飞，看，那是“燕子”，那是“山鹰”，那是“大蜈蚣”，它们把天空点缀得特别美丽。',
        '五颜六色的风筝在天空中上下翻飞，看，那是“燕子”，那是“山鹰”，那是“大蜈蚣”，它们把天空点缀得特别美丽。',
        '五颜六色的风筝在天空中上下翻飞，看，那是“燕子”，那是“山鹰”，那是“大蜈蚣”，它们把天空点缀得特别美丽。',
        '五颜六色的风筝在天空中上下翻飞，看，那是“燕子”，那是“山鹰”，那是“大蜈蚣”，它们把天空点缀得特别美丽。',
        '五颜六色的风筝在天空中上下翻飞，看，那是“燕子”，那是“山鹰”，那是“大蜈蚣”，它们把天空点缀得特别美丽。',
        '五颜六色的风筝在天空中上下翻飞，看，那是“燕子”，那是“山鹰”，那是“大蜈蚣”，它们把天空点缀得特别美丽。',
        '五颜六色的风筝在天空中上下翻飞，看，那是“燕子”，那是“山鹰”，那是“大蜈蚣”，它们把天空点缀得特别美丽。'
    ]
    desc = Rhetoric()
    i = 0
    while i < 20:
        rhetoric_info = desc.get_all_rhetorics(sent_list)
        print('rhetoric num', rhetoric_info['num'])
        for k,v in rhetoric_info.items():
            print(k)
            print(v)
        i += 1
    print('success')
        