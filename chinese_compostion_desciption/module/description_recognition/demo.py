import sys
from description import Description

if __name__ == "__main__":
    desc = Description()
    state, description = desc.init()
    print(state, description)
    if state < 0:
        sys.exit(0)

    sentence_list = [
        '几次尝试下来，燕子风筝只是奋力向上跃了几下，很快就摇摇晃晃、无精打采地落了下来。',
        '生机勃勃的春天来到了，万物复苏，这正是放风筝的好时节。', 
        '五颜六色的风筝在天空中上下翻飞，看，那是“燕子”，那是“山鹰”，那是“大蜈蚣”，它们把天空点缀得特别美丽。',
        '草地上 传来他们一阵阵的欢呼声，如银铃般清脆,如驼铃般悠远，与这美好的 舂色融为了一体。',
        '小睿举着一只美丽的燕子风筝，小明在前面像一名百米冲刺的运动员，低着头只顾拼命地拉着线奔跑。'
    ]
    state, desc_info = desc.get_all_descriptions(sentence_list)
    print('描写数目', desc_info['num'])
    for k,v in desc_info['info'].items():
        print(k)
        print(v)
        print()
    # print(desc_info)
