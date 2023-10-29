import os
import time
from base import Base
from organization import OrganizationScorer
from content import ContentScorer
from expression import ExpressionScorer
from theme import ThemeScorer
from main_scorer import MainScorer
from essay_utils import read_text, save_json, is_exist_in_dict, is_Chinese
from pyltp import Segmentor, Postagger

class EssayGrading(object):
    def __init__(self):
        self.base_ = Base()
        self.main_scorer_ = MainScorer()
        self.theme_scorer = ThemeScorer(self.base_.segmentor, self.base_.postagger)
        self.org_scorer = OrganizationScorer()
        self.content_scorer = ContentScorer()
        self.exp_scorer = ExpressionScorer()

    def release(self):
        print('release LTP models....')
        self.base_.release()
        self.theme_scorer.release()
        
    def is_input_vaild(self, input_dict):
        # 检查必填项是否存在
        input_valid = True
        msg = ''
        if not is_exist_in_dict(input_dict, 'grade'):
            input_valid = False
            msg = 'Required input [grade] is not exist'
            return input_valid, msg
        if not is_exist_in_dict(input_dict, 'answer_text'):
            input_valid = False
            msg = 'Required input [answer_text] is not exist'
            return input_valid, msg
        if not is_exist_in_dict(input_dict, 'answer_title'):
            input_valid = False
            msg = 'Required input [answer_title] is not exist'
            return input_valid, msg
        
        # 检查必填项内容和类型是否正确
        grade = input_dict['grade']
        answer_text = input_dict['answer_text']
        answer_title = input_dict['answer_title']
        # grade
        if type(grade) is not int or grade < 0 or grade > 12:
            input_valid = False
            msg = 'Invalid input for grade={}, must be integer between 0 and 12'.format(grade)
            return input_valid, msg
        # answer_text
        if type(answer_text) is not list:
            input_valid = False
            msg = 'Invalid input for answer_text={}, must be list'.format(answer_text)
            return input_valid, msg
        have_chinese = False
        for text in answer_text:
            if is_Chinese(text):
                have_chinese = True
                break
        if have_chinese == False:
            input_valid = False
            msg = 'Invalid input for answer_text={}, answer_text must have chinese'.format(answer_text)
            return input_valid, msg
        # answer_title
        if type(answer_title) is not str:
            input_valid = False
            msg = 'Invalid input for answer_title={}, must be string'.format(answer_title)
            return input_valid, msg

        # 检查选填项类型和内容是否正确
        # min_text_length 和 max_text_length
        min_text_length, max_text_length = None, None
        if 'min_text_length' in input_dict:
            min_text_length = input_dict['min_text_length']
            if type(min_text_length) is not int or min_text_length < 0:
                input_valid = False
                msg = 'Invalid input for min_text_length={}, must be integer and bigger than 0'.format(min_text_length)
                return input_valid, msg
        if 'max_text_length' in input_dict:
            max_text_length = input_dict['max_text_length']
            if type(max_text_length) is not int or max_text_length < 0:
                input_valid = False
                msg = 'Invalid input for max_text_length={}, must be integer and bigger than 0'.format(max_text_length)
                return input_valid, msg
        if min_text_length is not None and max_text_length is not None:
            if min_text_length > max_text_length:
                input_valid = False
                msg = 'Invalid input for min_text_length={} and max_text_length={}, min_text_length must smaller than max_text_length'.format(min_text_length,max_text_length)
                return input_valid, msg
        # question
        if 'question' in input_dict and type(input_dict['question']) is not str:
            input_valid = False
            msg = 'Invalid input type={} for question, must be string'.format(type(input_dict['question']))
            return input_valid, msg
        # topic
        if 'topic' in input_dict:
            if type(input_dict['topic']) is not list or len(input_dict['topic'])==0:
                input_valid = False
                msg = 'Invalid input for topic={}, must be string'.format(input_dict['topic'])
                return input_valid, msg
        # title
        if 'title' in input_dict and type(input_dict['title']) is not str:
            input_valid = False
            msg = 'Invalid input type={} for title, must be string'.format(type(input_dict['title']))
            return input_valid, msg
        # question_type
        if 'question_type' in input_dict:
            question_types = [1,2,3,4]
            question_type = input_dict['question_type']
            if type(question_type) is not int or question_type not in question_types:
                input_valid = False
                msg = 'Invalid input for question_type={}, must be integer in {}'.format(question_type,question_types)
                return input_valid, msg
        # topic_type
        if 'topic_type' in input_dict:
            topic_types = [1,2,3]
            topic_type = input_dict['topic_type']
            if type(topic_type) is not int or topic_type not in topic_types:
                input_valid = False
                msg = 'Invalid input for topic_type={}, must be integer in {}'.format(topic_type,topic_types)
                return input_valid, msg
        # correction_type
        if 'correction_type' in input_dict:
            correction_type = input_dict['correction_type']
            correction_types = [0,1]
            if type(correction_type) is not int or correction_type not in correction_types:
                input_valid = False
                msg = 'Invalid input for correction_type={}, must be integer in {}'.format(correction_type,correction_types)
                return input_valid, msg

        return input_valid, msg


    def check_input_length(self, content, min_text_length):
        text_length = len(content)
        min_len = int(min_text_length*0.5)
        if text_length < min_len:
            print('学生作文字数太少！')
            return False
        return True

    def get_grading_result(self, input_dict, content, min_text_length):
        # 统一处理
        st = time.time()
        answer_text = input_dict['answer_text']
        grade = input_dict['grade']
        answer_title = input_dict['answer_title']
        content_len = len(content)
        if 'correction_type' in input_dict and input_dict['correction_type'] == 0:
            need_correct = False
        else:
            need_correct = True
        answer_text, sentence_list, basic_info, base_time = self.base_.get_base_result(answer_text)
        code = 1
        msg = '批改成功'
        grading_result = {}
        time_result = {}
        # 各个维度评分
        # 结构
        org_result = self.org_scorer.get_organization_result(answer_text, basic_info['conj_num'], min_text_length, grade)
        if org_result['code'] == 0:    # 批改出错，不继续批改
            code = 0
            msg = org_result['msg']
            return code, msg, grading_result, time_result
        # 主题
        theme_result = self.theme_scorer.get_theme_result(content, answer_title, grade)
        if theme_result['code'] == 0:    # 批改出错，不继续批改
            code = 0
            msg = theme_result['msg']
            return code, msg, grading_result, time_result
        # 表达
        exp_result = self.exp_scorer.get_expression_result(sentence_list, grade)
        if exp_result['code'] == 0:    # 批改出错，不继续批改
            code = 0
            msg = exp_result['msg']
            return code, msg, grading_result, time_result
        # 内容
        content_result = self.content_scorer.get_content_result(answer_text, basic_info, grade, need_correct=need_correct)
        if content_result['code'] == 0:    # 批改出错，不继续批改
            code = 0
            msg = content_result['msg']
            return code, msg, grading_result, time_result
        # 总体
        num_typos = sum(list(content_result['data']['content_info']['grammar_mistake_statistic'].values()))
        # 例如 score_dict = {'theme' : 5, 'organization' : 5, 'content' : 5,  'expression' : 4}
        score_dict = {
            'theme': theme_result['data']['theme_score'],
            'organization': org_result['data']['organization_score'],
            'content': content_result['data']['content_score'],
            'expression': exp_result['data']['expression_score']
        }
        main_result, main_score_time = self.main_scorer_.apply(score_dict, content_len, min_text_length, num_typos, True)
        grading_result.update(main_result)
        grading_result.update(org_result['data'])
        grading_result.update(theme_result['data'])
        grading_result.update(exp_result['data'])
        grading_result.update(content_result['data'])
        time_result = {
            'all_time': time.time()-st,
            'organization_time': org_result['time']['organization_time'],
            'theme_time': theme_result['time']['theme_time'],
            'expression_time': exp_result['time']['expression_time'],
            'content_time': content_result['time']['content_time'],
            'main_score_time': main_score_time,
            'base_time': base_time,
            'mistake_time': content_result['time']['mistake_time'],
            'rhetoric_time': exp_result['time']['rhetorical_time'],
            'description_time': exp_result['time']['description_time'],
            'quote_time': content_result['time']['quote_time'],
            'relevance_time': theme_result['time']['relevance_time']
        }
        return code, msg, grading_result, time_result

    
    def apply(self, input_dict):
        '''
        args: input_dict, dict, 用户输入 
            - required keys: 
                - 'grade': int, 0~12。0-6小学，7-9初中，10-12高中
                - 'answer_text': list, 学生作文
                - 'answer_title': str, 学生作文标题
            - optional keys:
                - 'question': str, 题干
                - 'topic': list, 主题，允许多个
                - 'title': str, 命题作文的题目
                - 'min_text_length': int, 作文要求的最小长度
                - 'max_text_length': int, 作文要求的最大长度
                - 'question_type': int, 作文题材，1-记叙文；2-说明文；3-议论文；4-应用文
                - 'topic_type': int, 作文类型，1-话题作文；2-命题作文；3-材料作文
                - 'answer_title': str, 学生作文的题目标题
                - 'correction_type': int, 是否需要纠错（默认为1）, 1-需要; 0-不需要
            若question、topic、title、answer_title四个参数均为空，则不返回和「主题」相关的批改结果

        returns: result_dict, dict, 处理结果
            code, int, 0-批改失败，1-批改成功，2-字数太短，不做批改
            msg, str, 与code对应的信息
            data, dict, 批改结果
        '''
        # 检测输入是否合法
        time_result = -1
        input_valid, msg = self.is_input_vaild(input_dict)
        if not input_valid:
            return {'code': 0, 'msg': msg, 'data': {}}, time_result
        answer_text = input_dict['answer_text']
        answer_content = ''.join(answer_text)
        grade = input_dict['grade']
        if 'min_text_length' in input_dict and type(input_dict['min_text_length']) is int:
            min_text_length = input_dict['min_text_length']
        else:
            min_text_length = 0
        # 检测学生作文字数是否达到批改要求
        if not self.check_input_length(answer_content, min_text_length):
            return {'code':2, 'msg':'学生作文字数太少，不符合批改要求', 'data':{}}, time_result
        # 进入正式批改    
        result = {
            'code': 1,
            'msg': '批改成功',
            'data': {}
        }
        try:
            code, msg, grading_result, time_result = self.get_grading_result(input_dict, answer_content, min_text_length)
            result['code'] = code
            result['msg'] = msg
            result['data'] = grading_result
        except Exception as error:
            print('Exception: ', error)
            result['code'] = 0
            result['msg'] = '总接口批改出错，错误为：{}'.format(error)
        return result, time_result


if __name__ == '__main__':
    # root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    grading_ = EssayGrading()
    input_dict = {
        'answer_text':['我家有一盆美丽的水仙花。',
            '虽然，水仙花是从跟大蒜一样的东西里长出来的，但样子却非凡。',
            '叶子从底下冒出来，长长的，绿绿的，紧紧地挨在一起。绿叶上，又钻出了几朵洁白洁白的水仙花，怒放的花朵里露出娇嫩的黄色花蕊，水仙花姿态各种各样，一朵美过一朵。',
            '我好像就是一朵娇嫩美丽的水仙花，身穿洁白无暇的衣裙，垂着头。阳光就是灯，春风就是一段动听的乐曲，伴随着阳光和春风，我跳起了优美的舞蹈，一刻也停不下来。跳完了舞，我还会其它水仙花聊天，听清水讲有趣的故事，和绿叶一起游戏……',
            '当水仙花真好。我一直沉浸在水仙花的世界里，想着它的美丽，想着它的可爱。四年级:李知烨'
        ],
        'grade':0,
        'answer_title':'水仙花'
    }
    # print(is_exist_in_dict(input_dict,'grade'))
    print('start grading ...')
    result, time_result = grading_.apply(input_dict)
    print('code', result['code'])
    print('msg', result['msg'])
    print('data info')
    data = result['data']
    if len(data.keys()) > 0:
        for k,v in data.items():
            print(k)
            print(v)
            print()
    # print(result)
    grading_.release()
    save_json(result, './result_sample.json')
