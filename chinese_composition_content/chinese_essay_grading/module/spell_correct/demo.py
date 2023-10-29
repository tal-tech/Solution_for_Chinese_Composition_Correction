import spell 

model = spell.spellModel()
sent = "少先队员因该为老人让坐"
_input = [[sent, sent], [sent, sent]]

# 纠错
print(model.predict_paragraphs(_input))

# 检测
print(model.predict_paragraphs(_input, need_correct=False))