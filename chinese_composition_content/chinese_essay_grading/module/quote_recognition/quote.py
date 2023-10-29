import os
# import collections
import json
from quote_utils import read_text

class Quote(object):
    def __init__(self):
        root = os.path.split(os.path.abspath(__file__))[0]
        self.chengyu_list = read_text(os.path.join(root, 'lib/chengyu.txt'))
        self.suyu_list = read_text(os.path.join(root, 'lib/suyu.txt'))
        self.mingyan_list = read_text(os.path.join(root, 'lib/mingyan.txt'))

    # 工具函数
    def find_all(self, text, sub):
        result = []
        k = 0
        while k < len(text):
            k = text.find(sub, k)
            if k == -1:
                return result
            else:
                result.append((k, sub))
                k += len(sub)
        return result

    # [(6, 衣来伸手，饭来张口), (11, 饭来张口)]
    def remove_duplicate(self, matched_list):
        new_matched = []
        matched_list = list(set(matched_list))
        for i in range(len(matched_list)):
            remove = False
            cand = matched_list[i]
            rest = matched_list[0:i]+matched_list[i+1:]
            res = [(x[0], x[0]+len(x[1])) for x in rest if cand[1] in x[1]]
            for r in res:
                if cand[0] >= r[0] and cand[0] < r[1]:
                    remove = True
                    break
            if remove == False:
                new_matched.append(cand)
        return new_matched

    # key='suyu' or 'mingyan'
    def merge_match(self, match_list, text, key):
        merge_list = []
        if len(match_list) == 0:
            return merge_list
        match_list.sort(key=lambda x:x[0])
        st,ed = 0, 0
        i = 0
        while i < len(match_list)-1:
            item_1 = match_list[i]
            item_2 = match_list[i+1]
            st,ed = item_1[0], item_1[0]+len(item_1[1])
            if item_2[0] > item_1[0]+len(item_1[1]) + 1:
                merge_list.append((st,text[st:ed]))
            else:
                while item_2[0]<=item_1[0]+len(item_1[1])+1 and i < len(match_list)-1:
                    ed = item_2[0]+len(item_2[1])
                    i += 1
                    if i >= len(match_list)-1:
                        break
                    item_1 = match_list[i]
                    item_2 = match_list[i+1]
                merge_list.append((st,text[st:ed]))
            i += 1
        if ed != match_list[-1][0]+len(match_list[-1][1]):
            st=match_list[-1][0]
            ed=match_list[-1][0]+len(match_list[-1][1])
            merge_list.append((st,text[st:ed]))
        if key == 'mingyan':
            merge_list=[x for x in merge_list if len(x[1])>4]
        return list(set(merge_list))

    def tuple_2_dict(self, tuple_list):
        dict_list = [] 
        for item in tuple_list:
            start = item[0]
            content = item[1]
            end = start + len(content)
            dict_list.append({
                'start_index':start,
                'end_index': end,
                'content': content
            })
        return dict_list

    def match_chengyu_direct(self, text):
        match_list = []
        for word in self.chengyu_list:
            temp = self.find_all(text, word)
            match_list += temp
        match_list = self.remove_duplicate(match_list)
        res_list = self.tuple_2_dict(match_list)
        return res_list

    def match_suyu_direct(self, text):
        match_list = []
        for word in self.suyu_list:
            temp = self.find_all(text, word)
            match_list += temp
        match_list = self.remove_duplicate(match_list)
        match_list = self.merge_match(match_list, text, 'suyu')
        res_list = self.tuple_2_dict(match_list)
        return res_list

    def match_mingyan_direct(self, text):
        match_list = []
        for word in self.mingyan_list:
            temp = self.find_all(text, word)
            match_list += temp
        match_list = self.remove_duplicate(match_list)
        match_list = self.merge_match(match_list, text, 'mingyan')
        res_list = self.tuple_2_dict(match_list)
        return res_list

    def get_quote_info(self, para_list):
        idiom_info, alle_info, mingyan_info = [], [], []
        # idiom_info, alle_info, mingyan_info = {}, {}, {}
        idiom_num, alle_num, mingyan_num = 0, 0, 0
        for i in range(len(para_list)):
            text = para_list[i]
            # print(text)
            para_id = i+1
            idiom_list = self.match_chengyu_direct(text)
            if len(idiom_list) > 0:
                idiom_info.append({'paragraph':para_id, 'details':idiom_list})
                idiom_num += len(idiom_list)

            alle_list = self.match_suyu_direct(text)
            if len(alle_list) > 0:
                alle_info.append({'paragraph':para_id, 'details':alle_list})
                alle_num += len(alle_list)
            
            mingyan_list = self.match_mingyan_direct(text)
            if len(mingyan_list) > 0:
                mingyan_info.append({'paragraph':para_id, 'details':mingyan_list})
                mingyan_num += len(mingyan_list)
        
        quote_info = dict(idiom_num=idiom_num, idiom_info=idiom_info,
            allegorical_num=alle_num, allegorical_info=alle_info,
            quote_num=mingyan_num, quote_info=mingyan_info
        )
        # print('quote_info', mingyan_info)  
        return quote_info
