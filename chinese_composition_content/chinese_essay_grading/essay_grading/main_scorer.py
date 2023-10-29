import time
import random

class MainScorer():
    def __init__(self):
        self.comprehensive_comments_dict = {
            '90_100' : ['文章流畅，行文洒脱，与众不同，凸显出你良好的语言驾驭能力。',
                '文章立意新颖，构思巧妙，取材于生活，情感真挚。',
                '本文详略得当，主次分明，用词精彩。',
                '文章不落俗套，构思奇特，见解精辟，给人启发。',
                '本文视角独特，语句流畅，文笔优美，让人印象深刻。',
                '本文取材于生活，幽默风趣，有大家风范。'],
            '70_89' : ['文章构思新颖又未脱离生活，语言流畅，妙趣横生，吸引读者眼球。',
                '文章从细节出发，描写具体，加深了读者印象。',
                '文章行文流畅，结构鲜明，继续练笔，你会更出色。',
                '文章语言得体，有详有略，文脉畅通。',
                '文章内容生动具体，段落明确，语言朴实，通俗易懂。',
                '本文描写细致，叙事具体，字里行间，透露着对生活的热爱。'],
            '60_69' : ['文章取材于生活，通俗易懂，具有一定的代表性。',
                '文章符合题意，语言平实。',
                '本文符合题意，扎根于生活，真实有趣。',
                '文章取材于生活，语言平实，符合题意。',
                '文章观察细致，语言自然，令读者读起来很舒服。',
                '本文想象奇特，对精彩地方有较细致的描写。'],
            '30_59' : ['本文内容较平淡，结构不够清晰，前后关联不紧密。',
                '文章内容不够充实，语言过于简洁。',
                '文章逻辑性较弱，叙事不够完整。',
                '文章语句不够通畅，表意不明。',
                '文章缺少细节描述，内容不够新颖。',
                '文章主题不够突出，衔接有些生硬，缺少点题。'],
            '0_29' : ['本文主题不明确，内容孤立，距离规范性写作还有段距离。',
                '文章立意不明，层次不够清晰，需加强练习。',
                '文章主题不鲜明，重点不突出，需要注意多积累，多阅读。',
                '拼凑感强，无清晰的逻辑，可用心观察生活，多思考多领悟，积累写作素材。',
                '本文内容不够充实，叙事不够具体，写作水平有待提升，继续练笔，会越来越好。',
                '文章重点不够突出，好似流水帐，缺少设计感。']
        }

        self.pros_comment_dict = {
            'theme' : ['主题突出，贴近生活，恰到好处；',
                '符合题意，中心明确，立意鲜明；',
                '重点突出，中心凸显于内容之中；',
                '中心突出，详略得当；'],
            'organization' : ['思路清晰，构思精妙，衔接自然连贯，称得上一篇佳作；',
                '层次分明，条理清晰，过渡自然；',
                '主次分明，结构严谨，脉络清晰；',
                '结构完整，巧用连接词，衔接自然；'],
            'content' : ['巧用成语和佳句，语言深刻有内涵，情真意切，感人至深；',
                '巧用成语，事半功倍，让文章锦上添花；',
                '引用成语和佳句，深化主题，让文章增色很多；',
                '详略得当，精挑细拣，素材似为主题量身定制；'],
            'expression' : ['运用多种表达方式，文笔老练，说理畅达，读你的文章真是一种享受；',
                '使用多种修辞手法，从多个角度说明事物的特征，给读者留下了深刻印象；',
                '动静结合，直抒胸臆，生动活泼，增添了感染力；',
                '句式富有变化，运用多种描写手法，使文章更加生动；']
        }

        self.cons_comment_dict = {
            'theme' : ['立意不够新颖，注意挖掘事物真相，从多角度思考，继续练习，就可写出让人印象深刻的文章。',
                '中心主题不够明确，写作目的不清晰。注重审题，收集素材，紧扣主题，充实内容，继续练笔，会越来越好的。'],
            'organization' : ['文层次感较弱，衔接不够连贯，但依然有可圈可点之处；不要灰心，继续练笔，梳理写作思路，合理选材，详略得当，定会写出优秀篇章。',
                '文章的组织条理较弱，层次不够分明；试试思维导图法，写作前可列一下提纲，文章层次就会清晰的多。'],
            'content' : ['情节较平直，无悬念；写作素材源于生活，留意观察，并加强阅读，必能写出优秀篇章，期待你的进步。',
                '前后内容关联度不大，与主题联系不够紧密。写作也是一种思维训练，要注意谋篇布局，留心日常生活中的小事，多思考多领悟，加强练习，这会提升你的写作水平。'],
            'expression' : ['表达方式较为单一，语言不够生动，富于变化，才会让人读了耳目一新；用心留意生活，多角度思考问题，注意模仿和积累，你一定会越来越出色的。',
                '句式不够丰富，修辞手法使用的较少。细致观察，注意积累和仿写，循序渐进，必能写出优秀作品。']
        }

        self.suggestion_dict = {
            'theme' : ['中心主题是文章的灵魂，写出与主题贴切的文章，第一步就是审题，确保理解题目的意思，紧扣题意写作，可以从以下方面做好审题：(1)认证的阅读作文的题目，了解作文的含义。(2)在作文材料中寻找出介绍作文题目的句子。(3)在题目描述中找到限制中心词的词语，明确作文范围和体裁。(4)了解中心词后的说明作文要求的句子，审出作文的具体要求。',
                '中心主题是文章的灵魂，写出与主题贴切的文章，可以从以下方面着手：1.明确中心主题，所有素材全部围绕主题展开；2.行文过程中不断呼应主题；3.摒弃一切和主题无关的语句，围绕主题组织语言。',
                '材料作文或半命题作文，我们可以从以下几个点着手找主题：1.从题目或话题中探索主题；2.结合现实探求主题，写作时尽量从正面表达思想,有时也可结合现实从反面立意；3.巧用联想去表现文章主题，通过对平凡事物的精雕细刻,以显示深层内蕴,并巧用联想,由物及人,从而表现文章主题；4.变换角度去寻找新的主题。'],
            'organization' : ['结构是文章的骨架，要求完整，清晰，严谨。1.结构完整是指文章有开头，过渡和结尾三部分。一般文章开头要快速切入正题，做到先声夺人，“开门见山法”，“引用法”以及“比喻法”都是常用的开头办法；过渡内容简练不拖沓，可与开头也可与结尾照应；结尾往往升华主题，深化中心，“照应法”，“点睛法”以及“总结法”都是常用的结尾办法。2.结构清晰要求分段合理，段与段的内容不能相互包含，纠缠不清。3.结构严谨则要求段与段之间有逻辑关系，合理安排段落之间的过渡和衔接，也要注意文章体裁的。可先编写提纲，再行文。',
                '文章层次之间总说和分说的关系，有三种基本形式：1.先总后分，文章开头部分总括提出所要叙述事件的整体面貌、基本特征或中心观点；后面的段落分别从若干方面列举事例具体详细地加以描写或从不同的角度提出分论点具体加以阐述。　　2.先分后总；　　3.先总说，后分说，再总说。　　无论使用哪一种形式，都应注意，分总之间必须有紧密的内在联系，分述部分要围绕总述的中心进行，总述部分应是分述的总纲或水到渠成的总结。',
                '什么是并列式的文章结构？并列式是从若干方面入笔，不分主次、并列平行地叙述事件、说明事物，或以几个并列的层次论证中心论点的结构方式。其特点是将事件、事物或论题分成几个方面来叙写、说明和议论，每个部分都是独立完整的部分，与其他部分是并列平行关系。　　运用并列式结构注意点：　　1、并列的几个内容各自独立，又紧紧围绕一个中心。　2、并列的各个部分必须是平行的，要防止各个方面交叉或从属。'],
            'content' : ['材料内容是文章的血肉，恰当的选材，可以更好地表达文章的中心。常用的选材方法有：1.仔细观察，用心感悟，从生活中积累材料，材料真实才可靠；2.围绕中心选取典型的新颖的材料，感情真挚得分高；3.注意多阅读书籍报刊，积累并正确运用成语、名人警句，提升文章语言的生动性。',   
                '材料内容是文章的血肉，恰当的选材，可以更好地表达文章的中心。常用的选材方法有：1.转换角度法。写作构思时要多角度思考，从不同的方向切入，给读者不一样的视角，更容易让你的文章在众多相似度很高的文章当中脱颖而出；2.关键要素组合法。把你的目标读者喜欢的一些痛点，热点要素，都记录下来；3.设置悬念法。吸引读者的兴趣，文章中要学会制造悬念，不断激发读者的好奇心，让对方迫不及待地往下读。',
                '材料内容是文章的血肉，恰当的选材，可以更好地表达文章的中心。常用的选材方法有：1.发散思维，深入思考，多想一步；2.不管写作的主题也好，风格也好，叙述的方式也好，最终的目的都是为了满足读者内心的需求；3.积累素材，记录生活中的新鲜事，有趣的故事。'],
            'expression' : ['在写作中巧用修辞手法，不仅能使语言有文采，还能增添文章的亮点。正确使用修辞手法，提升文章表达效果。首先，要了解熟悉常用的八种表达修辞手法；其次，要充分调动各种感官，注意仿写。合理地运用各种修辞手法，才能够使文章生动、形象、逼真，情节引人入胜，扣人心弦。',
                '在写作过程中，表达技巧很重要。我们需要做到：1.要合理地运用事件，去粗取精，选择事例中最具有典型性和代表性的环节作为重点来详写，次要一点的环节略写，与中心无关的干脆不写。2.要适当地铺垫和渲染。3.综合运用各种描写方法来塑造人物形象。一个成功的人物形象一定是有血有肉的，他就是我们生活中的一个个体，要让他自己在读者面前充分的展示。',
                '作文表达要突出真情实感，我们要努力做到：一是写真写实，即把自己的情感表达得真实，让人可信，从而引起人的共鸣；二是写深写透，即把情感的最深处表达出来，不仅要获得理解，而且要引起深度的理解。“写进去”，才能体现真正的写作功力。']
        }

        self.typos_suggestion = '4.可经常翻阅字典，注意积累形似汉字的笔画，释义和用法，避免文章出现错别字。'
        
        self.dimension_priority_lst = ['theme', 'organization', 'content', 'expression'] # 顺序体现优先级，不可改变

        self.inner_check()

    
    def inner_check(self):
        for k in self.pros_comment_dict:
            if(k not in self.dimension_priority_lst):
                raise ValueError('{} not in {}'.format(k, self.dimension_priority_lst))
        for k in self.cons_comment_dict:
            if(k not in self.dimension_priority_lst):
                raise ValueError('{} not in {}'.format(k, self.dimension_priority_lst))

        for k in self.suggestion_dict:
            if(k not in self.dimension_priority_lst):
                raise ValueError('{} not in {}'.format(k, self.dimension_priority_lst))
        print('Check all dictionary key spelling...')

    def calculate_total_score(self, score_dict, content_len, min_text_len, num_typos, verbose):
        theme_score = score_dict['theme']
        organization_score = score_dict['organization']
        content_score = score_dict['content']
        expression_score = score_dict['expression']
        # print('theme={},organization={},content={},expression={}'.format(
        #     theme_score,organization_score,content_score,expression_score
        # ))

        raw_total_score = int(20*(theme_score*0.15 + organization_score*0.3 + content_score*0.3 + expression_score*0.25))
        final_total_score, n_content_length = self.deduct_points_content_length(raw_total_score, content_len, min_text_len)
        final_total_score, n_typos = self.deduct_points_typo(final_total_score, num_typos)

        if(verbose):
            print('最终总分{}, 原始总分{}, 字数扣分{}，错别字扣分{}'.format(final_total_score, raw_total_score, n_content_length, n_typos))
        return final_total_score

    def deduct_points_content_length(self, total_score, content_len, min_text_len):
        n = 0
        if(content_len<min_text_len):
            n = int((min_text_len-content_len)/50)
            n = min(n, 5)
            total_score -= n
        return total_score, n

    def deduct_points_typo(self, total_score, num_typos):
        n = min(num_typos, 5)
        return total_score-n, n

    def decide_pros_cons(self, score_dict, verbose):
        '''
        输入： score_dict: 分项打分dict
        输出：pros_dimension ： 优点维度； cons_dimension：缺点维度；suggestion_dimension: 建议维度；若返回None则表示不存在优点或者缺点
        '''
        max_score = max(score_dict.values())
        min_score = min(score_dict.values())

        pros_candidate = {k:v for k,v in score_dict.items() if v==max_score}
        cons_candidate = {k:v for k,v in score_dict.items() if v==min_score}
        pros_dimension, cons_dimension, suggestion_dimension = None, None, None
        for dimension in self.dimension_priority_lst:
            if(dimension in pros_candidate.keys() and pros_candidate[dimension]>=4):
                pros_dimension = dimension
                break

        for dimension in self.dimension_priority_lst:
            if(dimension in cons_candidate.keys() and cons_candidate[dimension]<=3):
                cons_dimension = dimension
                break

        for dimension in self.dimension_priority_lst:
            if(dimension in cons_candidate.keys()):
                suggestion_dimension = dimension
                break

        if(verbose):
            print('优点维度:{}, 缺点维度:{}, 建议维度:{}'.format(pros_dimension, cons_dimension, suggestion_dimension))
        return pros_dimension, cons_dimension, suggestion_dimension


    # 总分，总评，建议的入口函数
    def apply(self, score_dict, content_len, min_text_len, num_typos, verbose=False):
        '''
        入参：
        1）score_dict： 分项评分dict，例如 score_dict = {'theme' : 5, 'organization' : 5, 'content' : 5,  'expression' : 4}
        content_len: 正文长度, int
        min_text_len : 最低字数要求, int
        num_typos : 错别字数目, int
        verbose: 打印关键中间结果的开关，设为false则不显示，设为True打印输出

        出参:
        result = {  'total_score' : final_total_score, # 最终总分, int 0~100
                    'comment' : final_comment, # 总评语， str
                    'suggestion' : suggestion #建议,str
                    }

        '''
        st = time.time()
        # 检查入参中的分项评分字典key是否合法
        for k in score_dict:
            if(k not in self.dimension_priority_lst):
                raise ValueError('{} not in {}'.format(k, self.dimension_priority_lst))

        final_total_score = self.calculate_total_score(score_dict, content_len, min_text_len, num_typos, verbose)
        if(final_total_score>=90):
            t = '90_100'
        elif(final_total_score>=70 and final_total_score<=89):
            t = '70_89'
        elif(final_total_score>=60 and final_total_score<=69):
            t = '60_69'
        elif(final_total_score>=30 and final_total_score<=59):
            t = '30_59'
        elif(final_total_score<=29):
            t = '0_29'
        comprehensive_comment_cands = self.comprehensive_comments_dict[t]
        comprehensive_comments = random.choice(comprehensive_comment_cands) # 综合评语

        pros_dimension, cons_dimension, suggestion_dimension = self.decide_pros_cons(score_dict, verbose)
        
        pro_comment, cons_comment = '', ''
        if(pros_dimension is not None):
            pro_comments = self.pros_comment_dict[pros_dimension]
            pro_comment = random.choice(pro_comments)    #优点评语
        if(cons_dimension is not None):
            cons_comments = self.cons_comment_dict[cons_dimension]
            cons_comment = random.choice(cons_comments)  #缺点激励评语

        # 总评==综合评语+优点评语+缺点激励评语
        final_comment = comprehensive_comments + pro_comment + cons_comment

        # 建议
        suggestion_cands = self.suggestion_dict[suggestion_dimension]
        suggestion = random.choice(suggestion_cands)
        # 如果建议维度是内容，且错别字超过3个，则加上错别字项
        if suggestion_dimension == 'content' and num_typos > 3:
            suggestion += self.typos_suggestion

        result = {  'total_score' : final_total_score,
                    'comment' : final_comment,
                    'suggestion' : suggestion
                    }
        return result, time.time()-st

        

if __name__ == '__main__':
    import numpy as np

    main_scorer = MainScorer()

    for _ in range(100):
        score_dict = {'theme' : np.random.randint(low=1, high=5),
                        'organization' : np.random.randint(low=1, high=5),
                        'content' : np.random.randint(low=1, high=5),
                        'expression' : np.random.randint(low=1, high=5)}

        content_len = np.random.randint(low=200, high=1500)
        min_text_len = np.random.randint(low=500, high=1000)
        num_typos = np.random.randint(low=0, high=20)
        
        for k, v in score_dict.items():
            print(k, v)

        print('字数{}, 最小字数要求{}, 错别字{}'.format(content_len, min_text_len, num_typos))
        result = main_scorer.apply(score_dict, content_len, min_text_len, num_typos, True)
        print('返回结果')
        for k,v in result.items():
            print(k, v)
        print('-'*66)
        
        
            

    

