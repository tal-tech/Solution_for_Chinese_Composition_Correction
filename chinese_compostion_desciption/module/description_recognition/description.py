"""
@author: hufei6
@date: 2021-12-21
@versions: v3.1
@doc: 描写模块: 相对于上个版本，其它描写功能使用一个多分类模型实现
"""
import os
import re
import time
import sys

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# sys.path.append(os.path.join(root, 'text_classification'))
sys.path.append(os.path.join(root, 'multi_task'))

from desc_kernel import MultClassifier
from multi_model import Bert4KearsMultiTask, SinusoidalInitializer
from desc_config import desc_key_map, model_config, sense_config
from desc_utils import read_text


class Description(object):

    def __init__(self):
        self.id2label = ["language", "scenery", "shentai", "environment", "action", "appearance", "psychology"]
        self.label2id = {}
        for i in range(len(self.id2label)):
            self.label2id[self.id2label[i]] = i

    def init(self, key_list=list(desc_key_map.keys())):
        """
        key_list: 需要识别的描写手法列表
        """
        if len(key_list) == 0 or not isinstance(key_list, list):
            return -1011001, '描写对象初始化错误:描写手法的key list输入为空 或者不是list!'
        
        for x in key_list:
            if not isinstance(x, str):
                return -1011002, '描写对象初始化错误:描写手法 key 为非字符串元素!'
            if x not in desc_key_map:
                return -1011003, '描写对象初始化错误:描写手法 key 不是描述手法!'

        self.key_list = key_list

        # 初始化五感模型
        print('Load sense model...')
        try:
            sense_multi = Bert4KearsMultiTask(sense_config['multi_config'])
            custom_objects = {"sinusoidal":SinusoidalInitializer}
            sense_multi.load_model(sense_config['multi_config']['model_path'], custom_objects)
            self.sense_multi = sense_multi
        except:
            return -1011004, '描写对象初始化错误:五感模型初始化错误'
        print('Sense model loaded!')

        # 初始化其它描写模型
        print('Load description model...')
        try:
            self.thresholds = model_config['thresholds']
            self.labelnumb = model_config['num_labels']
            self.model_multi = MultClassifier(model_config)
        except:
            return -1011005, '描写对象初始化错误:描写七分类模型初始化错误'
        print('Description model loaded!')

        # 加载配置文件
        try:
            root1 = os.path.split(os.path.abspath(__file__))[0]
            self.language = {
                'keyword': read_text(os.path.join(root1, 'lib/lang_desc_keyword.txt')), # 语言描写 确认 关键字
                'except': read_text(os.path.join(root1, 'lib/lang_desc_except.txt')) # 语言描写 排除 关键字
            }
            self.language_pyscho_reg = re.compile('((心里.*(说|想|默念))|心想|生气地想|内心)')
            self.language_as_if_reg = re.compile('((好|就)?像(都|是)?在.*(问|说)?)|(仿?佛(对|在).*说)')
        except:
            return -1011006, '描写对象初始化错误:规则部分加载错误'
        
        return 0, "描写对象初始化:Successful initialization!"

    def get_all_descriptions(self, sent_list, essay_type='common'):
        """
        对外总接口
        sent_list:句子列表
        essay_type:体裁
        """
        description_info = {
            'num': 0,    # 描写的数量
            'info': {}
        }

        if not isinstance(sent_list, list):
            description_info['description'] = "描写模块批处理:输入不是list类型!"
            return -1012001, description_info

        if len(sent_list) == 0:
            description_info['description'] = "描写模块批处理:Successful!"
            return 0, description_info

        for sent in sent_list:
            if not isinstance(sent, str):
                description_info['description'] = "描写模块批处理:输入list中存在非字符串元素!"
                return -1012002, description_info

        # todo 五感识别
        try:
            sense_dict, sense_time = self.get_sense(sent_list)
            for k,v in sense_dict.items(): # 循环五感
                description_info['info'][k] = {'pred_result':v['pred_result'],'match_result':v['match_result']}
                description_info['num'] += v['match_num']
        except:
            description_info['description'] = "描写模块批处理:五感子模块处理错误!"
            return -1012003, description_info
        
        # todo 其它描写
        try:
            labelis_list = self.get_description(sent_list, essay_type)
            info = {}
            for label in self.label2id:
                info[label] = {'pred_result': [], 'match_result': []}
        
            for index in range(len(sent_list)):
                labelis = labelis_list[index]
                for i in range(self.labelnumb):
                    info[self.id2label[i]]['pred_result'].append(labelis[i])
                    if labelis[i]:
                        description_info['num'] += 1
                        info[self.id2label[i]]['match_result'].append(sent_list[index])
            for label in info:
                description_info['info'][label] = info[label]
        except:
            description_info['description'] = "描写模块批处理:七分类子模块处理错误!"
            return -1012004, description_info

        description_info['description'] = "描写模块批处理:Successful!"

        return 0, description_info

    def get_sense(self, sent_list):
        """ 五感识别 """
        st = time.time()
        pred_list, pred_sample_list = self.sense_multi.demo_text_list_batch(sent_list)
        # print('self.sense_multi.batch_size', self.sense_multi.batch_size)
        key_name_map = {v:k for k,v in sense_config['name_map'].items()}
        name_key_map = sense_config['name_map']
        sense_dict = {k:{} for k in key_name_map.keys()}
        for item in pred_list:
            key = name_key_map[item['name']]
            # label_num = [x for x in self.tasks
            #              if x['name'] == name][0]['label_num']
            y_pred = item['pred']
            y_pred = y_pred > 0.5
            y_pred = [1 if x==True else 0 for x in y_pred]
            match_list = []
            match_num = 0
            for i in range(len(y_pred)):
                if y_pred[i] == 1:
                    match_list.append(sent_list[i])
                    match_num += 1
            sense_dict[key] = {
                'match_num': match_num,
                'match_result': match_list,
                'pred_result': y_pred
            }
        # print('sense_time'*5, time.time()-st)
        return sense_dict, time.time()-st

    def get_description(self, sent_list, essay_type='common'):
        """ 其它类别 """
        _, proba_list = self.model_multi.parser_text_list(sent_list)
        relist = []
        for index in range(len(sent_list)):
            proba = proba_list[index]
            labelis = [1 if proba[i] > self.thresholds[i] else 0 for i in range(self.labelnumb)]
                
            # 同时命中景物和环境，只展示一个识别结果：写人叙事-环境；写景-景物；通用-景物
            if labelis[self.label2id["scenery"]] == 1 and labelis[self.label2id["environment"]] == 1:
                if essay_type == 'narrative':
                    labelis[self.label2id["scenery"]] = 0
                else:
                    labelis[self.label2id["environment"]] = 0
                
            # 语言描写规则
            if labelis[self.label2id["language"]] == 1:
                sent = sent_list[index]
                if re.search(self.language_pyscho_reg, sent) or re.search(self.language_as_if_reg, sent):
                    labelis[self.label2id["language"]] = 0

            relist.append(labelis)
        return relist

            
if __name__ == "__main__":
    sent_list = [
        '此时他心中冒出了一个想法：不能放弃！', # appearance 0
        '何老师有一头长长的头发，下面有两条弯弯的眉毛，眉毛下面有两只大眼睛，还有一个笔直的鼻子，鼻梁上配了一副眼镜，显得非常有学问。', # appearance 1
        '她叫小蕾，长着一双水灵灵的大眼睛，又淡又清秀的眉毛“挂”在额下，小小的鼻子下有一张能说会道的樱桃小嘴，可爱极了！' # appearance 1
        '我的妈妈先推开门，再xiān开被子接着说：“起床了起床了。”妈妈走出了房门。', # lang 1
        '拿出豆腐切成一个个可爱的小正方体，起锅烧油之后，我们把这些菜依次“进锅中，过了一会儿，爸爸把麻婆豆腐速地揣上了桌子。', # lang 0
        '我快速地穿完了衣服，又快速地刷完了牙，洗完了脸，准备吃早cān', # lang 0
        '好不容易下课了，我差红了脸，低着头，找到班长道歉说：“对不起，是我误会了你。', # lang 1
        '班长大方的说。“没关系，我们还是和好吧。”', # lang 1
        '到了山塘街，往前看，可以看见许多人，人山人海的，一不小心没跟上，就找不到人了，所以一定要慎重。', # env 0
        '在蔚蓝的开空，美丽的大自然和我们壮观的校园都不停地回荡着“运动员进行曲”的小调，运动员啦啦队也在表演，为运动会助威。', # env 1
        '灿烂的阳光照耀在奔流的长江上，波光粼粼。', # env 1
        '我一路上总是忐忑不安，我神经都快绷断了，忽然，月亮被云遮住了，连一点点月光也不透下来。' # env 0
        '摆动的枝条像美丽的小姑娘在拨开自己的头发，仿佛对河流说：“春天来了！”', # jingwu 1
        '刮风的时候叶子会发出沙沙声，像是和在和对方说着悄悄话。', # jingwu 1
        '我的家乡，绿水青山环绕，春日里春茶靡，莺飞水长，十里芍药，溃散成花海。', # jingwu 0
        '竹子摸上去硬硬的，像一块砖头。' # jingwu 1
        '天黑了下来，乌云把太阳盖住了，天空下起了雨，雨声淅沥，不一会，就小了，它很细，很棉，像春天时，空中漂浮的柳絮，又像满天发亮的珍珠，飘飘扬扬地挥洒着。', #env and jingwu 1
        '即使是烈日炎炎，但大部分阳光都被浓密的叶子挡住了，只透出了星星点点的阳光。', #env and jingwu 1
        '我们沿着弯弯曲曲的小石子路在林中穿行，古木参天，那密密的枝叶连一丁点儿太阳也照不进来，要不是时不时传来几声鸟叫，那里真有点儿恐怖。',
        '一个例子一个例子一个例子一个例子一个例子一个例子一个例子。',
        '此时他心中冒出了一个想法：不能放弃！', # appearance 0
        '何老师有一头长长的头发，下面有两条弯弯的眉毛，眉毛下面有两只大眼睛，还有一个笔直的鼻子，鼻梁上配了一副眼镜，显得非常有学问。', # appearance 1
        '她叫小蕾，长着一双水灵灵的大眼睛，又淡又清秀的眉毛“挂”在额下，小小的鼻子下有一张能说会道的樱桃小嘴，可爱极了！' # appearance 1
        '我的妈妈先推开门，再xiān开被子接着说：“起床了起床了。”妈妈走出了房门。', # lang 1
        '拿出豆腐切成一个个可爱的小正方体，起锅烧油之后，我们把这些菜依次“进锅中，过了一会儿，爸爸把麻婆豆腐速地揣上了桌子。', # lang 0
        '我快速地穿完了衣服，又快速地刷完了牙，洗完了脸，准备吃早cān', # lang 0
        '好不容易下课了，我差红了脸，低着头，找到班长道歉说：“对不起，是我误会了你。', # lang 1
        '班长大方的说。“没关系，我们还是和好吧。”', # lang 1
        '到了山塘街，往前看，可以看见许多人，人山人海的，一不小心没跟上，就找不到人了，所以一定要慎重。', # env 0
        '在蔚蓝的开空，美丽的大自然和我们壮观的校园都不停地回荡着“运动员进行曲”的小调，运动员啦啦队也在表演，为运动会助威。', # env 1
        '灿烂的阳光照耀在奔流的长江上，波光粼粼。', # env 1
        '我一路上总是忐忑不安，我神经都快绷断了，忽然，月亮被云遮住了，连一点点月光也不透下来。' # env 0
        '摆动的枝条像美丽的小姑娘在拨开自己的头发，仿佛对河流说：“春天来了！”', # jingwu 1
        '刮风的时候叶子会发出沙沙声，像是和在和对方说着悄悄话。', # jingwu 1
        '我的家乡，绿水青山环绕，春日里春茶靡，莺飞水长，十里芍药，溃散成花海。', # jingwu 0
        '竹子摸上去硬硬的，像一块砖头。' # jingwu 1
        '天黑了下来，乌云把太阳盖住了，天空下起了雨，雨声淅沥，不一会，就小了，它很细，很棉，像春天时，空中漂浮的柳絮，又像满天发亮的珍珠，飘飘扬扬地挥洒着。', #env and jingwu 1
        '即使是烈日炎炎，但大部分阳光都被浓密的叶子挡住了，只透出了星星点点的阳光。', #env and jingwu 1
        '我们沿着弯弯曲曲的小石子路在林中穿行，古木参天，那密密的枝叶连一丁点儿太阳也照不进来，要不是时不时传来几声鸟叫，那里真有点儿恐怖。',
        '一个例子一个例子一个例子一个例子一个例子。',
        '此时他心中冒出了一个想法：不能放弃！', # appearance 0
        '何老师有一头长长的头发，下面有两条弯弯的眉毛，眉毛下面有两只大眼睛，还有一个笔直的鼻子，鼻梁上配了一副眼镜，显得非常有学问。', # appearance 1
        '她叫小蕾，长着一双水灵灵的大眼睛，又淡又清秀的眉毛“挂”在额下，小小的鼻子下有一张能说会道的樱桃小嘴，可爱极了！' # appearance 1
        '我的妈妈先推开门，再xiān开被子接着说：“起床了起床了。”妈妈走出了房门。', # lang 1
        '拿出豆腐切成一个个可爱的小正方体，起锅烧油之后，我们把这些菜依次“进锅中，过了一会儿，爸爸把麻婆豆腐速地揣上了桌子。', # lang 0
        '我快速地穿完了衣服，又快速地刷完了牙，洗完了脸，准备吃早cān', # lang 0
        '好不容易下课了，我差红了脸，低着头，找到班长道歉说：“对不起，是我误会了你。', # lang 1
        '班长大方的说。“没关系，我们还是和好吧。”', # lang 1
        '到了山塘街，往前看，可以看见许多人，人山人海的，一不小心没跟上，就找不到人了，所以一定要慎重。', # env 0
        '在蔚蓝的开空，美丽的大自然和我们壮观的校园都不停地回荡着“运动员进行曲”的小调，运动员啦啦队也在表演，为运动会助威。', # env 1
        '灿烂的阳光照耀在奔流的长江上，波光粼粼。', # env 1
        '我一路上总是忐忑不安，我神经都快绷断了，忽然，月亮被云遮住了，连一点点月光也不透下来。' # env 0
        '摆动的枝条像美丽的小姑娘在拨开自己的头发，仿佛对河流说：“春天来了！”', # jingwu 1
        '刮风的时候叶子会发出沙沙声，像是和在和对方说着悄悄话。', # jingwu 1
        '我的家乡，绿水青山环绕，春日里春茶靡，莺飞水长，十里芍药，溃散成花海。', # jingwu 0
        '竹子摸上去硬硬的，像一块砖头。' # jingwu 1
        '天黑了下来，乌云把太阳盖住了，天空下起了雨，雨声淅沥，不一会，就小了，它很细，很棉，像春天时，空中漂浮的柳絮，又像满天发亮的珍珠，飘飘扬扬地挥洒着。', #env and jingwu 1
        '即使是烈日炎炎，但大部分阳光都被浓密的叶子挡住了，只透出了星星点点的阳光。', #env and jingwu 1
        '我们沿着弯弯曲曲的小石子路在林中穿行，古木参天，那密密的枝叶连一丁点儿太阳也照不进来，要不是时不时传来几声鸟叫，那里真有点儿恐怖。',
        '一张慈祥的脸，一双水汪汪的大眼睛，长长的、乌黑的秀发。',
        '她是那么的温柔可亲呀！',
        '可小明的手都拽红了，脖了通红通红的，小明双手死死地握住了绳子。',
    ]
    # ori_list = [{'paragraph_id': 0, 'original_text': '小区里的杏花开了，一丛丛、一簇簇的白中带粉的花瓣，美丽而柔软；就像我们睡的棉被一样，又像一个个趴在树上的小精，还没长出叶子的枝干随风摆动，像极了在温暖的春风中等树阳光雨露的孩子。', 'sentence_id': 0}, {'paragraph_id': 1, 'original_text': '这是一棵棵毒茂盛的杏花树，微风一吹，阵香气扑鼻而来，不浓不淡相相宜，一根根树枝伸向四周，仿佛在对人们说：“春天来啦！春天来啦！”', 'sentence_id': 1}, {'paragraph_id': 2, 'original_text': '春天可真偏心啊！把它到来的息先告诉了杏花，正月未过，杏花迎阳光约情纵放。', 'sentence_id': 2}, {'paragraph_id': 2, 'original_text': '好像在告诉我们：“开花要领先，学习要趁早，奋斗要积极。', 'sentence_id': 3}, {'paragraph_id': 3, 'original_text': '小区里的杏花开了，一丛丛、一簇舞的白中带粉的花瓣，美丽而柔软，就像我们睡的棉被一样，又像一个个趴在树上的小精，还没长出叶子的枝干随风摆动，像极了在温暖的春风中等树阳光雨露的孩了。', 'sentence_id': 4}, {'paragraph_id': 4, 'original_text': '这是一棵棵毒茂盛的杏花树，微风一吹，阵阵香气扑鼻而来，不浓不淡箱相宜，一根根树枝伸向四周，仿佛在对人们说：“春天来啦！春天来拉！”', 'sentence_id': 5}, {'paragraph_id': 5, 'original_text': '春天可真偏心啊！把它到来的息先告诉了杏花，正月未过，杏花迎阳光约情纵放，好像在告诉我们：“开花要领先，学习要趁早，奋斗要积极。', 'sentence_id': 6}]
    # sent_list = [x['original_text'] for x in ori_list]
    essay_type='narrative'
    desc = Description()
    state, description = desc.init()
    print(state, description)
    i = 0
    while i < 20:
        state, desc_info = desc.get_all_descriptions(sent_list,essay_type)
        print(state, desc_info)
        print('description num', desc_info['num'])
        for k,v in desc_info.items():
            print(k)
            print(v)
        i += 1
    print('success')
    # import torch
    # torch.load('/share/作文批改/src/工程代码/v2_5/model/description_model/Action_roberta_state.th')
    # print('success')