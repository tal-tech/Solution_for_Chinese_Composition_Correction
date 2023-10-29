import time
import sys
sys.path.append("../")
import spell
import re
import numpy as np
import tqdm 

input_txt_path = "../../../gec_ch/data/zuowen/1000.txt"
output_txt_path = "../../../gec_ch/data/zuowen/cor_1000.txt"
def cut_sent(para):
    para = re.sub('([。！？\?])([^”’])', r"\1\n\2", para)  # 单字符断句符
    para = re.sub('(\.{6})([^”’])', r"\1\n\2", para)  # 英文省略号
    para = re.sub('(\…{2})([^”’])', r"\1\n\2", para)  # 中文省略号
    para = re.sub('([。！？\?][”’])([^，。！？\?])', r'\1\n\2', para)
    # 如果双引号前有终止符，那么双引号才是句子的终点，把分句符\n放到双引号后，注意前面的几句都小心保留了双引号
    para = para.rstrip()  # 段尾如果有多余的\n就去掉它
    # 很多规则中会考虑分号;，但是这里我把它忽略不计，破折号、英文双引号等同样忽略，需要的再做些简单调整即可。
    return para.split("\n")

def load_passages(txt_path=input_txt_path):
    with open(txt_path, "r", encoding="utf-8") as f:
        passage_list = f.readlines()
    return passage_list

model = spell.spellModel()


passage_list = load_passages()

corrected_passages = []
correct_cost = []
detect_cost = []
word_num = 0
cor_passages = []
passage_length_list = [ len(p) for p in passage_list]
print("average length {}".format(sum(passage_length_list)/len(passage_list)))
print("max length {}".format(max(passage_length_list)))
print("min length {}".format(sorted(passage_length_list)[1:5]))
# for passage in tqdm.tqdm(passage_list[:10]):
#     sent_list = cut_sent(passage.strip())
#     _input = [sent_list]
#     correct_ret = model.predict_paragraphs(_input)

# for passage in tqdm.tqdm(passage_list):
#     sent_list = cut_sent(passage.strip())
#     _input = [sent_list]
#     t0 = time.time()
#     correct_ret = model.predict_paragraphs(_input)
#     cor_passages.append(correct_ret["correction_result"])
#     t1 = time.time()
#     model.predict_paragraphs(_input, need_correct=False)
#     t2 = time.time()
#     correct_cost.append(t1-t0)
#     detect_cost.append(t2-t1)
#     word_num += len(passage)
# print("correct 平均耗时 {}".format(np.mean(correct_cost)))
# print("detect 平均耗时 {}".format(np.mean(detect_cost)))
# print("字符总数 {}".format(word_num))
# print("correct {}".format(np.sum(correct_cost)/word_num))
# print("detect {}".format(np.sum(detect_cost)/word_num))
# with open(output_txt_path,"w", encoding="utf-8") as f:
#     f.write("\n".join(cor_passages))


# # 纠错
# print(model.predict_paragraphs(_input))

# # 检测
# print(model.predict_paragraphs(_input, need_correct=False))