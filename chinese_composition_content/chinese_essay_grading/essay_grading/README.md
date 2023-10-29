# 中文作文批改总接口
result_sample.json 为总接口批改结果示例

## 总接口调用方法
见 essay_grading.py 里的 main 函数

## 子维度接口说明
### 主题维度
调用方式：见 theme.py 里的 main 函数  
是否需要GPU：否  
返回字段说明：  
- code: 1或0，int类型。1表示批改成功，0表示批改失败。
- msg: 返回的提示信息，string类型。若code=1，返回“批改成功”；若code=0，返回具体的错误信息。
- data: 主题维度的得分，评语及具体批改信息，object类型。
- time: 主题维度所用时间，object类型。时间单位为s。此字段是为了测试用时，正式返回结果中不需要包含。  
返回示例：
``` json
{
    "code":1,
    "msg":"批改成功",
    "data":{
        "theme_score":5,
        "theme_comment":"主题很鲜明，直接凸显于内容之中，简明扼要，见解独到。",
        "theme_info":{
            "theme_type":1,
            "theme_word_list":[
                {
                    "theme_word":"妈妈",
                    "theme_word_num":17
                },
                {
                    "theme_word":"爸爸",
                    "theme_word_num":18
                }
            ]
        }
    }, 
    "time": {   
        "theme_time": 0.0017,
        "relevance_time": 0.0016      
    }
}
```
### 结构维度
调用方式：见 organization.py 里的 main 函数
是否需要GPU：否  
返回字段说明：  
- code: 1或0，int类型。1表示批改成功，0表示批改失败。
- msg: 返回的提示信息，string类型。若code=1，返回“批改成功”；若code=0，返回具体的错误信息。
- data: 结构维度的得分，评语及具体批改信息，object类型。
- time: 结构维度所用时间，object类型。时间单位为s。此字段是为了测试用时，正式返回结果中不需要包含。  
返回示例：
``` json
{
    "code":1,
    "msg":"批改成功",
    "data":{
        "organization_score":3,
        "organization_comment":"布局得当，但前后连贯性较弱。",
        "organization_info":{
            "text_length_type":1,
            "paragraph_num":5,
            "conjunction_num":3
        }
    },
    "time":{
        "organization_time":0.001
    }
}
```
特殊说明：
此维度结果依赖于 base.py 里的 basic_info['conj_num'] 的结果
### 表达维度
调用方式：见 expression.py 里的 main 函数  
是否需要GPU：是 
返回字段说明：  
- code: 1或0，int类型。1表示批改成功，0表示批改失败。
- msg: 返回的提示信息，string类型。若code=1，返回“批改成功”；若code=0，返回具体的错误信息。
- data: 表达维度的得分，评语及具体批改信息，object类型。
- time: 表达维度所用时间，object类型。时间单位为s。此字段是为了测试用时，正式返回结果中不需要包含。  
返回示例：
``` json
{
    "code":1,
    "msg":"批改成功",
    "data":{
        "expression_score":4,
        "expression_comment":"巧用了环境描写、比喻等表达手法，发人深思，描写较为细腻，深入浅出，语言生动形象。",
        "expression_info":{
            "rhetorical_num":2,
            "rhetorical_info":{
                "fanwen": [], 
                "personification": [], 
                "analogy": ["草地上 传来他们一阵阵的欢呼声，如银铃般清脆,如驼铃般悠远，与这美好的 舂色融为了一体。", "小睿举着一只美丽的燕子风筝，小明在前面像一名百米冲刺的运动员，低着头只顾拼命地拉着线奔跑。"], 
                "parallelism": [], 
                "shewen": []
            },
            "description_num":0,
            "description_info": {
                "language": [], 
                "smell": [], 
                "action": [], 
                "hearing": [], 
                "psychology": [], 
                "shentai": [], 
                "taste": [], 
                "enviroment": [], 
                "appearance": []
            }
        }
    }, 
    "time": {   
        "expression_time": 1.926,
        "rhetorical_time": 0.5515,
        "description_time": 1.375  
    }
}
```
### 内容维度
调用方式：见 content.py 里的 main 函数  
是否需要GPU：否  
返回字段说明：  
- code: 1或0，int类型。1表示批改成功，0表示批改失败。
- msg: 返回的提示信息，string类型。若code=1，返回“批改成功”；若code=0，返回具体的错误信息。
- data: 内容维度的得分，评语及具体批改信息，object类型。
- time: 内容维度所用时间，object类型。时间单位为s。此字段是为了测试用时，正式返回结果中不需要包含。  
返回示例：
``` json
{
    "code":1,
    "msg":"批改成功",
    "data":{
        "content_score":3,
        "content_comment":"形容词、副词的使用，如“美丽、好”，使文章画面感增强，独有特点。",
        "content_info":{
            "total_char_num":1000,
            "total_term_num":500,
            "term_type":{
                "noun_num":0,
                "verb_num":0,
                "adj_num":0,
                "adv_num":0
            },
            "total_sentence_num":80,
            "misspelling_num":20,
            "grammar_mistake_sentence":4,
            "grammar_mistake_statistic":{
                "spell_errors":4
            },
            "grammar_mistake_info":[
                {
                    "paragraph":1,
                    "details":[
                        {
                            "type":"拼写错误",
                            "cor":"UNK",
                            "ori":"因该",
                            "start":4,
                            "end":6
                        },
                        {
                            "type":"拼写错误",
                            "cor":"UNK",
                            "ori":"因该",
                            "start":4,
                            "end":6
                        }
                    ]
                }
            ],
            "correction_result":[
                "少先队员因该为老人让坐",
                "少先队员因该为老人让坐"
            ],
            "idiom_num":3,
            "idiom_info":[
                {
                    "paragraph":1,
                    "details":[
                        {
                            "content":"无精打采",
                            "end_index":34,
                            "start_index":30
                        },
                        {
                            "content":"生机勃勃",
                            "end_index":4,
                            "start_index":0
                        }
                    ]
                },
                {
                    "paragraph":2,
                    "details":[
                        {
                            "content":"无精打采",
                            "end_index":34,
                            "start_index":30
                        },
                        {
                            "content":"生机勃勃",
                            "end_index":4,
                            "start_index":0
                        }
                    ]
                }
            ],
            "allegorical_num":0,
            "allegorical_info":[
                {
                    "paragraph":1,
                    "details":[
                        {
                            "content":"无精打采",
                            "end_index":34,
                            "start_index":30
                        },
                        {
                            "content":"生机勃勃",
                            "end_index":4,
                            "start_index":0
                        }
                    ]
                }
            ],
            "quote_num":10,
            "quote_info":[
                {
                    "paragraph":1,
                    "details":[
                        {
                            "content":"无精打采",
                            "end_index":34,
                            "start_index":30
                        },
                        {
                            "content":"生机勃勃",
                            "end_index":4,
                            "start_index":0
                        }
                    ]
                }
            ]
        }
    },
    "time":{
        "content_time":5,
        "quote_time":1,
        "mistake_time":4
    }
}
```
特殊说明：
此维度结果依赖于 base.py 里的 basic_info 的结果
## 接口人
傅玮萍 fuweiping1@100tal.com; 许国伟 xuguowei@100tal.com; 
