import os
import re
import time
import sys
import random
from essay_utils import map_grade, split_content
from base import Base
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(root, 'module/spell_correct'))
from spell import spellModel
sys.path.append(os.path.join(root, 'module/quote_recognition'))
from quote import Quote

# 输出content相关信息：内容引用、basic统计信息及纠错信息
class Content(object):
    def __init__(self):
        spell_model_path = os.path.join(root, 'model/spell_data_3635627.klm')
        self.spell_model = spellModel(spell_model_path)
        self.quote_ = Quote()

    def get_mistake_info(self, para_list, need_correct=True):
        st = time.time()
        _input = [split_content(x) for x in para_list]
        spell_res = self.spell_model.predict_paragraphs(_input, need_correct)
        spell_res['correction_result'] = [''.join(x) for x in spell_res['correction_result']]
        print('mistake correct={} use time: {}'.format(need_correct, time.time()-st))
        return spell_res

    def get_content_info(self, para_list, basic_info, need_correct=True):
        content_info = {}
        # 引用信息
        st = time.time()
        yinyong_info = self.quote_.get_quote_info(para_list)
        yinyong_time = time.time()-st
        # 纠错信息
        st = time.time()
        mistake_info = self.get_mistake_info(para_list, need_correct)
        mistake_time = time.time()-st
        print('mistake use time', mistake_time)
        # 更新 content info
        content_info.update(dict((k,v) for k,v in basic_info.items() if k not in ['adj_adv_info','conj_num']))
        content_info.update(yinyong_info)
        content_info.update(mistake_info)
        # time_res = {'basic_time':basic_time,'yinyong_time':yinyong_time,
        #     'mistake_correct_time':correct_time,'mistake_detect_time':detect_time,
        #     'content_time':basic_time+yinyong_time+correct_time
        # }
        return content_info, yinyong_time, mistake_time

class ContentScorer(Content):
    def __init__(self):
        super(ContentScorer, self).__init__()
    
    # grade='primary'or'junior'or'senior'
    def score(self, content_info, grade):
        adj_adv_num = content_info['term_type']['adj_num'] + content_info['term_type']['adv_num']
        idiom_num = content_info['idiom_num']
        quote_sy_num = content_info['quote_num'] + content_info['allegorical_num']
        grade_map = {
            'primary': {
                '1':{'adj_adv_num':12, 'idiom_num':0, 'quote_sy_num':0},
                '2':{'adj_adv_num':12, 'idiom_num':0, 'quote_sy_num':0},
                '3':{'adj_adv_num':20, 'idiom_num':0, 'quote_sy_num':0},
                '4':{'adj_adv_num':30, 'idiom_num':1, 'quote_sy_num':0},
                '5':{'adj_adv_num':50, 'idiom_num':3, 'quote_sy_num':0}
            },
            'junior': {
                '1':{'adj_adv_num':15, 'idiom_num':0, 'quote_sy_num':0},
                '2':{'adj_adv_num':15, 'idiom_num':0, 'quote_sy_num':0},
                '3':{'adj_adv_num':20, 'idiom_num':1, 'quote_sy_num':0},
                '4':{'adj_adv_num':30, 'idiom_num':3, 'quote_sy_num':0},
                '5':{'adj_adv_num':50, 'idiom_num':4, 'quote_sy_num':1}
            },
            'senior': {
                '1':{'adj_adv_num':15, 'idiom_num':0, 'quote_sy_num':0},
                '2':{'adj_adv_num':15, 'idiom_num':0, 'quote_sy_num':0},
                '3':{'adj_adv_num':20, 'idiom_num':1, 'quote_sy_num':0},
                '4':{'adj_adv_num':40, 'idiom_num':3, 'quote_sy_num':0},
                '5':{'adj_adv_num':55, 'idiom_num':4, 'quote_sy_num':1}
            }
        }
        score = 0
        grade_key = map_grade(grade)
        level_dict = grade_map[grade_key]
        if adj_adv_num>=level_dict['5']['adj_adv_num'] and idiom_num>=level_dict['5']['idiom_num'] and quote_sy_num>=level_dict['5']['quote_sy_num']:
            score = 5
        elif adj_adv_num>=level_dict['4']['adj_adv_num'] and idiom_num>=level_dict['4']['idiom_num'] and quote_sy_num>=level_dict['4']['quote_sy_num']:
            score = 4
        elif adj_adv_num>=level_dict['3']['adj_adv_num'] and idiom_num>=level_dict['3']['idiom_num'] and quote_sy_num>=level_dict['3']['quote_sy_num']:
            score = 3
        elif adj_adv_num>=level_dict['2']['adj_adv_num'] and idiom_num>=level_dict['2']['idiom_num'] and quote_sy_num>=level_dict['2']['quote_sy_num']:
            score = 2
        else:
            score = 1
        return score
        
    def comment(self, score, content_info, basic_info):
        one_quote, adj_adv_1, adj_adv_2 = '', '', ''
        if score >= 3:
            mingyan, suyu, idiom = [], [], []
            # print(content_info['quote_info'])
            for item in content_info['quote_info']:
                mingyan += [x['content'] for x in item['details']]
            for item in content_info['allegorical_info']:
                suyu += [x['content'] for x in item['details']]
            for item in content_info['idiom_info']:
                idiom += [x['content'] for x in item['details']]
            if len(mingyan) > 0:
                one_quote = mingyan[0]
            elif len(suyu) > 0:
                one_quote = suyu[0]
            elif len(idiom) > 0:
                one_quote = idiom[0]
        if one_quote == '' and score >= 2:
            adj_adv_info = basic_info['adj_adv_info']
            sorted_info = sorted(adj_adv_info.items(), key=lambda kv: kv[1], reverse=True)
            adj_adv_1 = sorted_info[0][0]
            adj_adv_2 = sorted_info[1][0]
            one_quote = adj_adv_1
        
        score_comment_map = {
            '1': ['运用了极少量的形容词和副词，描写不够生动形象，要注意积累并正确使用成语佳句，提升文章质量。',
                '情节平直，内容描写不够生动形象。'],
            '2': ['形容词、副词的使用，如“{}、{}”，使文章画面感增强，独有特点。'.format(adj_adv_1, adj_adv_2),
                '本文使用了一些修辞词，如“{}、{}”，描写具体，较生动。'.format(adj_adv_1, adj_adv_2)],
            '3': ['好词好句的使用，如“{}”，语约意丰、耐人寻味。'.format(one_quote),
                '修辞词的使用，如“{}”，让内容更生动，更立体。'.format(one_quote)],
            '4': ['巧用成语、佳句等，如“{}”，文笔练达，意境深远。'.format(one_quote),
                '好词好句的使用，如“{}”，为文章增彩添色。'.format(one_quote)],
            '5': ['妙用成语、佳句等，如“{}”。令文章语言更精炼，使表意更生动，准确。'.format(one_quote),
                '好词好句，如“{}”，为语言增添了生趣。'.format(one_quote)]
        }
        comment_cands = score_comment_map[str(score)]
        return random.choice(comment_cands)


    def get_content_result(self, para_list, basic_info, grade, need_correct=True):
        content_result = {
            'code': 1,
            'msg': '批改成功',
            'data': {},
            'time': {}
        }
        try:
            st = time.time()
            content_info, yinyong_time, mistake_time = self.get_content_info(para_list, basic_info, need_correct)
            content_score = self.score(content_info, grade)
            content_comment = self.comment(content_score,content_info,basic_info)
            content_data = {
                'content_score': content_score,
                'content_comment': content_comment,
                'content_info': content_info
            }
            content_result['data'] = content_data
            content_result['time'] = {
                'content_time':time.time()-st,
                'quote_time':yinyong_time,
                'mistake_time':mistake_time
            }
        except Exception as error:
            print('Exception: ', error)
            content_result['msg'] = '内容维度批改出错，错误为：{}'.format(error)
            content_result['code'] = 0
        
        return content_result


if __name__ == "__main__":
    para_list = [   # 段落列表
        '几次尝试下来，燕子风筝只是奋力向上跃了几下，很快就摇摇晃晃、无精打采地落了下来。',
        '生机勃勃的春天来到了，万物复苏，这正是放风筝的好时节。', 
        '五颜六色的风筝在天空中上下翻飞，看，那是“燕子”，那是“山鹰”，那是“大蜈蚣”，它们把天空点缀得特别美丽。',
        '草地上 传来他们一阵阵的欢呼声，如银铃般清脆,如驼铃般悠远，与这美好的 舂色融为了一体。',
        '小睿举着一只美丽的燕子风筝，小明在前面像一名百米冲刺的运动员，低着头只顾拼命地拉着线奔跑。'
    ]
    grade = 3
    base_ = Base()
    scorer = ContentScorer()
    answer_text, sentence_list, basic_info, base_time = base_.get_base_result(para_list)
    content_result = scorer.get_content_result(answer_text, basic_info, grade, need_correct=True)
    # code=1为批改成功，code=0为批改出错
    print('code', content_result['code'])
    print('msg', content_result['msg'])
    print('data info')
    for k,v in content_result['data'].items():
        print(k,v)
    print('use time')
    print(content_result['time'])
    # 若测试用例全部批改完毕，则释放模型资源；否则不用释放，释放后要重新初始化才能继续批改
    base_.release()
