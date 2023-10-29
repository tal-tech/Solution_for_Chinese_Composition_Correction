import os
import re
import sys
import time
import random
from essay_utils import map_grade
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(root,'module/rhetoric_recognition'))
from rhetoric import Rhetoric
from rhetoric_config import rhe_key_map
sys.path.append(os.path.join(root,'module/description_recognition'))
from description import Description
from desc_config import desc_key_map

class Expression(object):
    def __init__(self):
        # rhe_key = ['analogy','personification','parallelism','fanwen','shewen']
        # desc_key = ['psychology','appearance','shentai','language','action','enviroment',
        #     'taste','smell','hearing']
        self.rhe_ = Rhetoric()
        self.desc_ = Description()

    def get_expression_info(self, sent_list):
        exp_info = {}
        st = time.time()
        rhetoric_info = self.rhe_.get_rhetoric_info(sent_list)
        rhe_time = time.time()-st
        st = time.time()
        desc_info = self.desc_.get_description_info(sent_list)
        desc_time = time.time()-st
        # 更新 expression info
        exp_info.update(rhetoric_info)
        exp_info.update(desc_info)
        return exp_info, rhe_time, desc_time


class ExpressionScorer(Expression):
    def __init__(self):
        super(ExpressionScorer, self).__init__()
        self.expression_map = rhe_key_map
        self.expression_map.update(desc_key_map)
    
    # grade='primary'or'junior'or'senior'
    def score(self, exp_info, grade):
        desc_type_num, rhe_type_num = 0, 0
        for k,v in exp_info['description_info'].items():
            desc_type_num += 1 if len(v)>0 else 0
        for k,v in exp_info['rhetorical_info'].items():
            rhe_type_num += 1 if len(v)>0 else 0
        exp_type_num = desc_type_num + rhe_type_num
        grade_map = {
            'primary': {
                '1':{'exp_type_num':1},   # 小于
                '2':{'exp_type_num':1},   # 大于等于
                '3':{'exp_type_num':2},   # 大于等于
                '4':{'exp_type_num':3},   # 大于等于
                '5':{'exp_type_num':5}    # 大于等于
            },
            'junior': {
                '1':{'exp_type_num':2},   # 小于
                '2':{'exp_type_num':2},   # 大于等于
                '3':{'exp_type_num':3},   # 大于等于
                '4':{'exp_type_num':4},   # 大于等于
                '5':{'exp_type_num':6}    # 大于等于
            },
            'senior': {
                '1':{'exp_type_num':1},   # 小于
                '2':{'exp_type_num':1},   # 大于等于
                '3':{'exp_type_num':2},   # 大于等于
                '4':{'exp_type_num':3},   # 大于等于
                '5':{'exp_type_num':5}    # 大于等于
            }
        }
        score = 0
        grade_key = map_grade(grade)
        level_dict = grade_map[grade_key]
        if exp_type_num >= level_dict['5']['exp_type_num']:
            score = 5
        elif exp_type_num >= level_dict['4']['exp_type_num']:
            score = 4
        elif exp_type_num >= level_dict['3']['exp_type_num']:
            score = 3
        elif exp_type_num >= level_dict['2']['exp_type_num']:
            score = 2
        else:
            score = 1
        return score

    def comment(self, exp_info, score):
        exp_1, exp_2 = '', ''
        if score >= 3:
            # 统计修辞/描写类型的频次
            rhe_des_num = {}
            for k,v in exp_info['description_info'].items():
                if k in rhe_des_num:
                    rhe_des_num[k] += len(v)
                else:
                    rhe_des_num[k] = len(v)
            for k,v in exp_info['rhetorical_info'].items():
                if k in rhe_des_num:
                    rhe_des_num[k] += len(v)
                else:
                    rhe_des_num[k] = len(v)
            rhe_des_sort = sorted(rhe_des_num.items(), key=lambda kv: kv[1], reverse=True)
            exp_1 = self.expression_map[rhe_des_sort[0][0]]
            exp_2 = self.expression_map[rhe_des_sort[1][0]]

        score_comment_map = {
            '1': ['只是用一些简单的手法进行套路性的写作，语言表达很单一。', '表达过于简单，缺少语言的锤炼，注意摘抄积累一些好词好句。'],
            '2': ['表达方式单一，平铺直叙，语言基本流畅。', '表达方式较为单一，语言不够丰富，注意摘抄积累一些好词好句。'],
            '3': ['使用了{}、{}表达手法，描写不够生动形象。'.format(exp_1, exp_2),
                '{}、{}表达手法的使用，让文章易读。'.format(exp_1, exp_2)],
            '4': ['巧用了{}、{}等表达手法，发人深思，描写较为细腻，深入浅出，语言生动形象。'.format(exp_1, exp_2),
                '巧用了{}、{}等表达手法，语言生动形象，比较生动。'.format(exp_1, exp_2)],
            '5': ['巧用了{}、{}等多种表达手法，读来让人印象深刻，情真意切，描写也很细腻，刻画入微，情思悠远。'.format(exp_1, exp_2),
                '运用多种表达方式，如{}、{}，让事物形象更突出，表达更生动。'.format(exp_1, exp_2)]
        }
        comment_cands = score_comment_map[str(score)]
        return random.choice(comment_cands)

   
    def get_expression_result(self, sent_list, grade):
        exp_result = {
            'code': 1,
            'msg': '批改成功',
            'data': {},
            'time': {}
        }
        try:
            st = time.time()
            exp_info, rhe_time, desc_time = self.get_expression_info(sent_list)
            exp_score = self.score(exp_info, grade)
            exp_comment = self.comment(exp_info, exp_score)
            exp_data = {
                'expression_score': exp_score,
                'expression_comment': exp_comment,
                'expression_info': exp_info
            }
            exp_result['data'] = exp_data
            exp_result['time'] = {
                'expression_time': time.time()-st,
                'rhetorical_time': rhe_time,
                'description_time': desc_time
            }
        except Exception as error:
            print('Exception: ', error)
            exp_result['msg'] = '表达维度批改出错，错误为：{}'.format(error)
            exp_result['code'] = 0
        
        return exp_result

        
if __name__ == "__main__":
    sent_list = [    # 句子列表，如果传入段落，需先切句
        '几次尝试下来，燕子风筝只是奋力向上跃了几下，很快就摇摇晃晃、无精打采地落了下来。',
        '生机勃勃的春天来到了，万物复苏，这正是放风筝的好时节。', 
        '五颜六色的风筝在天空中上下翻飞，看，那是“燕子”，那是“山鹰”，那是“大蜈蚣”，它们把天空点缀得特别美丽。',
        '草地上 传来他们一阵阵的欢呼声，如银铃般清脆,如驼铃般悠远，与这美好的 舂色融为了一体。',
        '小睿举着一只美丽的燕子风筝，小明在前面像一名百米冲刺的运动员，低着头只顾拼命地拉着线奔跑。'
    ]
    grade = 3
    scorer = ExpressionScorer()
    exp_result = scorer.get_expression_result(sent_list, grade)
    # code=1为批改成功，code=0为批改出错
    print('code', exp_result['code'])
    print('msg', exp_result['msg'])
    print('data info')
    for k,v in exp_result['data'].items():
        print(k,v)
    print('use time')
    print(exp_result['time'])
