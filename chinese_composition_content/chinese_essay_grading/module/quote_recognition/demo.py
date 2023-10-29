from quote import Quote
import json
import os

if __name__ == "__main__":
    quo = Quote()
    # para_list = [
    #     '几次尝试下来，燕子风筝只是奋力向上跃了几下，很快就摇摇晃晃、无精打采地落了下来。',
    #     '生机勃勃的春天来到了，万物复苏，这正是放风筝的好时节。', 
    #     '郊外小朋友们正兴致勃勃地放着风筝。'
    # ]
    para_list = []
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data = json.loads(open(os.path.join(root, 'test_essay.json')).read())
    j = 0
    while j < 3:
        for i in data:
            para_list = i['paragraphs']  
            print(len(para_list))
            quo_info = quo.get_quote_info(para_list)
            for k,v in quo_info.items():
                print(k)
                print(v)
                print()
        j += 1
    # for i in json.loads(open(os.path.join(root, 'test_essay.json')).read()):
    #     para_list += i['paragraphs']
    # print(len(para_list))
    # j = 0
    # while j < 3:
    #     quo_info = quo.get_quote_info(para_list)
    #     for k,v in quo_info.items():
    #         print(k)
    #         print(v)
    #         print()
    #     j += 1
