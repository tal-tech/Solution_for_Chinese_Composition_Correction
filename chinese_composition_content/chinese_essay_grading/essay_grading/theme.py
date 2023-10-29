import os
import sys
import time
import random
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(root,'module/topic_relevance'))
from baseline import TCRELEVANCE

class Theme(object):
    def __init__(self, segmentor=None, postagger=None):
        # 初始化
        LTP_DATA_DIR = os.path.join(root, 'model/ltp_data_v3.4.0')
        TC_MODEL_PATH = os.path.join(root, 'module/topic_relevance/model/gbdt_0.1_loss_deviance_nesti_250_maxdepth_6.pkl')
        STOPWORDS_DIR = os.path.join(root, 'module/topic_relevance/model/hit_stopwords.txt')
        self.tc_model = TCRELEVANCE(STOPWORDS_DIR, TC_MODEL_PATH, segmentor, postagger, LTP_DATA_DIR)
                
    def release(self):
        self.tc_model.release()

    def get_theme_info(self, content, answer_title):
        st = time.time()
        theme_info = {}
        if answer_title is not None:
            # content = ''.join(para_list)
            y_hat, y_proba, theme_word_list = self.tc_model.predict(answer_title, content)
            theme_info['theme_type'] = int(y_hat)   # 是否切合题意：0-跑题；1-切合题意
            theme_info['theme_word_list'] = theme_word_list  # 主题词信息（主题词+出现次数）
        return theme_info, y_proba, len(content), time.time()-st



class ThemeScorer(Theme):
    def __init__(self, segmentor=None, postagger=None):
        super(ThemeScorer, self).__init__(segmentor, postagger)
        # xiaoxue: 1分阈值0.027534652881791122, 2分阈值0.13929791167133176, 3分阈值0.7918429615999623, 4分阈值0.9852369979672942
        # chuhzong:1分阈值0.02445331546660714, 2分阈值0.06915703710357624, 3分阈值0.6247844539911823, 4分阈值0.978415088129828
        # gaozhong:1分阈值0.027595490918788934, 2分阈值0.07018864192757546, 3分阈值0.6730311048778673, 4分阈值0.9820095408865744
        self.xiaoxue_threshold_dict = {1 : 0.0275, 2 : 0.1393, 3 : 0.7918, 4 : 0.9852}
        self.chuzhong_threshold_dict = {1 : 0.0244, 2 : 0.0692, 3 : 0.625, 4 : 0.978}
        self.gaozhong_threshold_dict = {1 : 0.02759, 2 : 0.07018, 3 : 0.6730, 4 : 0.9820} 

        self.xiaoxue_grade_1_content_len = 100
        self.xiaoxue_grade_5_content_len = 200

        self.chuhzong_grade_1_content_len = 300
        self.chuzhong_grade_5_content_len = 500

        self.gaozhong_grade_1_content_len = 400
        self.gaozhong_grade_5_content_len = 550

        self.comments_dict = {  
            5 : ['主题很鲜明，直接凸显于内容之中，简明扼要，见解独到。', '主题明确，重点突出，给人留下了深刻的印象。'],
            4 : ['主题鲜明，重点突出，立意较新，语言灵动有质感，张弛有度，开合自如。', '主题深刻，立意较新，用词简洁。'],
            3 : ['符合题意，选材合理，文从字顺，继续练笔，你会更出色。', '主题明确，语言简练，使人一目了然。'],
            2 : ['中心不够明确，文句生涩，未能达意，再努力一把，优秀在向你招手。', '重点不够突出，可围绕主题重点展开描写。'],
            1 : ['中心不明确，内容过于简略，注意观察生活，积累素材，再努力一把，你的提升空间很大哦。', '内容与主题联系不够紧密。']
        }
    
    def score(self, probability, content_len, grade):
        '''
        args: grade: str, 0~12。0-6小学，7-9初中，10-12高中
        returns: 单项分数，0-5分
        '''
        if(grade<=6):
            score = self.inner_score(probability, self.xiaoxue_threshold_dict)
            if(score==1 or score==5):
                score = self.content_length_check(score, content_len, self.xiaoxue_grade_1_content_len, self.xiaoxue_grade_5_content_len)
        elif(grade<=9):
            score = self.inner_score(probability, self.chuzhong_threshold_dict)
            if(score==1 or score==5):
                score = self.content_length_check(score, content_len, self.chuhzong_grade_1_content_len, self.chuzhong_grade_5_content_len)
        elif(grade<=12):
            score = self.inner_score(probability, self.gaozhong_threshold_dict)
            if(score==1 or score==5):
                score = self.content_length_check(score, content_len, self.gaozhong_grade_1_content_len, self.gaozhong_grade_5_content_len)
        else:
            # raise ValueError('Invalid input for grade={}, must be integer between 0 and 12'.format(grade))
            score = -1
        comment_cands = self.comments_dict[score]
        return score, random.choice(comment_cands)

    def inner_score(self, probability, threshold_dict):
        grade_4_thres = threshold_dict[4]
        if(probability>grade_4_thres):
            return 5
        else:
            for k, v in threshold_dict.items():
                if(probability<=v):
                    return k
    
    def content_length_check(self, score, content_len, grade_1_max_len, grade_5_min_len):
        if(score==5):
            if(content_len>grade_5_min_len):
                return score
            else:
                return score-1
        elif(score==1):
            if(content_len<grade_1_max_len):
                return score
            else:
                return score+1
        else:
            raise ValueError('Invalid score={}, must be 1 or 5'.format(score))

    def get_theme_result(self, content, answer_title, grade):
        theme_result = {
            'code': 1,
            'msg': '批改成功',
            'data': {},
            'time': {}
        }
        try:
            st = time.time()
            if answer_title is not None:
                theme_info, theme_proba, content_len, relevance_time = self.get_theme_info(content, answer_title)
                theme_score, theme_comment = self.score(theme_proba, content_len, grade)
                theme_data = {
                    'theme_score': theme_score,
                    'theme_comment': theme_comment,
                    'theme_info': theme_info
                }
                theme_result['data'] = theme_data
                theme_result['time'] = {'theme_time':time.time()-st, 'relevance_time':relevance_time}
        except Exception as error:
            print('Exception: ', error)
            theme_result['msg'] = '主题维度批改出错，错误为：{}'.format(error)
            theme_result['code'] = 0
        return theme_result
        

if __name__ == "__main__":
    answer_title = '我的妈妈'
    # 全文内容
    content = '我亲爱的妈妈，您每天为我操碎了心，您是我最喜欢的人。妈妈，每次我向妈妈提出问题时，妈妈老是会跟我详细的讲解，每个难题总能迎刃而解，妈妈总是这样专心的的对我用着心。妈妈，您还记得吗，我每次学习不专心时，您老是用那泛着亮光的眼睛，看着我的一举一动。妈妈还每天为了我不那么晚睡觉，每次叮嘱我快点写作业。妈妈，我总是让您为了我伤透了心，您把我惩罚一顿后，我知道，您的心更痛。妈妈，还有“天使妈妈”的一面。上次，我听写连续得了100分，妈妈那开心的笑脸老是让我难以忘怀，您当晚还给我买了我最爱吃的薯条。啊，妈妈，您是我心中最喜欢的人，妈妈也是最关心我的人。妈妈，您有时对我“生气”也是对我的一种无私，又温暖的爱。每当我看到妈妈那悲伤的脸时，我心中总是有一股寒流“哗哗哗”地喷涌而出，心中老是有一股说不出来的伤心。啊，妈妈，我一定会用一个温暖的拥抱，一张满意的答卷，来修复妈妈那一颗牵累的心。我爱您，妈妈。'
    grade = 2
    scorer = ThemeScorer()
    theme_result = scorer.get_theme_result(content, answer_title, grade)
    # code=1为批改成功，code=0为批改出错
    print('code', theme_result['code'])
    print('msg', theme_result['msg'])
    print('data info')
    for k,v in theme_result['data'].items():
        print(k,v)
    print('use time')
    print(theme_result['time'])
    # 若测试用例全部批改完毕，则释放模型资源；否则不用释放，释放后要重新初始化才能继续批改
    scorer.release()
    