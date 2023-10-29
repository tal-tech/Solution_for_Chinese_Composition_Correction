import os
import re
import time
import random
from essay_utils import map_grade

class Organization(object):
    def __init__(self):
        pass

    def get_para_num(self, para_list):
        return len(para_list)

    def get_text_length_type(self, para_list, min_text_length):
        text_length = sum([len(x) for x in para_list])
        text_length_type = 1 if text_length>=min_text_length else 0
        return text_length_type

    def get_organization_info(self, para_list, conj_num, min_text_length):
        org_info = {
            # conj_num 通过调用 Base 类中的get_basic_info可以得到
            'conjunction_num': conj_num,
            'paragraph_num':self.get_para_num(para_list),
            'text_length_type':self.get_text_length_type(para_list,min_text_length)
        }
        return org_info

class OrganizationScorer(Organization):
    def __init__(self):
        super(OrganizationScorer, self).__init__()
    
    def score(self, org_info, grade):
        para_num = org_info['paragraph_num']
        conj_num = org_info['conjunction_num']
        # print(para_num,conj_num)
        grade_map = {
            'primary': {
                '1':{'para_num':1, 'conj_num':1},
                '2':{'para_num':1, 'conj_num':1},
                '3':{'para_num':2, 'conj_num':2},
                '4':{'para_num':3, 'conj_num':4},
                '5':{'para_num':3, 'conj_num':10}
            },
            'junior': {
                '1':{'para_num':2, 'conj_num':2},
                '2':{'para_num':2, 'conj_num':2},
                '3':{'para_num':3, 'conj_num':4},
                '4':{'para_num':4, 'conj_num':8},
                '5':{'para_num':5, 'conj_num':15}
            },
            'senior': {
                '1':{'para_num':2, 'conj_num':2},
                '2':{'para_num':2, 'conj_num':2},
                '3':{'para_num':4, 'conj_num':3},
                '4':{'para_num':5, 'conj_num':9},
                '5':{'para_num':6, 'conj_num':18}
            }
        }
        score = 0
        grade_key = map_grade(grade)
        level_dict = grade_map[grade_key]
        if para_num >= level_dict['5']['para_num'] and conj_num >= level_dict['5']['conj_num']:
            score = 5
        elif para_num >= level_dict['4']['para_num'] and conj_num >= level_dict['4']['conj_num']:
            score = 4
        elif para_num >= level_dict['3']['para_num'] and conj_num >= level_dict['3']['conj_num']:
            score = 3
        elif para_num >= level_dict['2']['para_num'] and conj_num >= level_dict['2']['conj_num']:
            score = 2
        else:
            score = 1
        return score
        
    def comment(self, score):
        score_comment_map = {
            '1': ['结构不清晰，未能达意。', '结构不紧凑，衔接不自然连贯。'],
            '2': ['结构不够清晰，层次不够分明。', '层次不够清晰，逻辑性较弱。'],
            '3': ['布局得当，但前后连贯性较弱。', '层次分明，衔接自然。'],
            '4': ['脉络分明，详略得当，不落俗套。', '结构合理，首尾呼应，让人一目了然。'],
            '5': ['层次感强，布局新颖，首尾呼应，恰到好处。','结构完整，层次清晰，前后连贯。']
        }
        comment_cands = score_comment_map[str(score)]
        return random.choice(comment_cands)

    def get_organization_result(self, para_list, conj_num, min_text_length, grade):
        org_result = {
            'code': 1,
            'msg': '批改成功',
            'data': {},
            'time': {}
        }
        try:
            st = time.time()
            org_info = self.get_organization_info(para_list,conj_num,min_text_length)
            org_score = self.score(org_info, grade)
            org_comment = self.comment(org_score)
            org_data = {
                'organization_score': org_score,
                'organization_comment': org_comment,
                'organization_info': org_info
            }
            org_result['data'] = org_data
            org_result['time'] = {'organization_time':time.time()-st}
        except Exception as error:
            print('Exception: ', error)
            org_result['msg'] = '结构维度批改出错，错误为：{}'.format(error)
            org_result['code'] = 0
        
        return org_result

if __name__ == "__main__":
    para_list = [    # 段落列表
        '几次尝试下来，燕子风筝只是奋力向上跃了几下，很快就摇摇晃晃、无精打采地落了下来。',
        '生机勃勃的春天来到了，万物复苏，这正是放风筝的好时节。', 
        '五颜六色的风筝在天空中上下翻飞，看，那是“燕子”，那是“山鹰”，那是“大蜈蚣”，它们把天空点缀得特别美丽。',
        '草地上 传来他们一阵阵的欢呼声，如银铃般清脆,如驼铃般悠远，与这美好的 舂色融为了一体。',
        '小睿举着一只美丽的燕子风筝，小明在前面像一名百米冲刺的运动员，低着头只顾拼命地拉着线奔跑。'
    ]
    conj_num = 3
    min_text_length = 0
    grade = 3
    scorer = OrganizationScorer()
    org_result = scorer.get_organization_result(para_list, conj_num, min_text_length, grade)        
    # code=1为批改成功，code=0为批改出错
    print('code', org_result['code'])
    print('msg', org_result['msg'])
    print('data info')
    for k,v in org_result['data'].items():
        print(k,v)
    print('use time')
    print(org_result['time'])
