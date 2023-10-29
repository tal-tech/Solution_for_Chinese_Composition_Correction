import os

root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

rhe_key_map = {
    'analogy':'比喻',
    'personification':'拟人',
    'parallelism':'排比',
    'shewen':'设问',
    'fanwen':'反问'    
}

model_config = {
    # 比喻
    'analogy': {
        'checkpoint_lst':[os.path.join(root, 'model/rhetoric_model/Analogy_PretrainedBert_1e-05_16_0.5.pt')],
        'use_bert': True,
        'embd_path': os.path.join(root, 'model/word_embedding/tencent_small'),
        'model_config_lst': [{
            'is_state': False,
            'model_name': 'bert',
            'pretrained_model_path': os.path.join(root, 'model/bert_chinese_wwm_ext_pytorch')
        }]
    },
    # 拟人
    'personification': {
        'checkpoint_lst':[os.path.join(root, 'model/rhetoric_model/Niren_PretrainedBert_5e-06_48_None.pt')],
        'use_bert': True,
        'embd_path': os.path.join(root, 'model/word_embedding/tencent_small'),
        'model_config_lst': [{
            'is_state': False,
            'model_name': 'bert',
            'pretrained_model_path': os.path.join(root, 'model/bert_chinese_wwm_ext_pytorch')
        }],
        'max_seq_len': 115,
        'need_mask': True
    },
    # 排比
    'parallelism': {
        'checkpoint_lst':[os.path.join(root, 'model/rhetoric_model/Parallel_PretrainedBert_1e-05_16.pt')],
        'use_bert': True,
        'embd_path': os.path.join(root, 'model/word_embedding/tencent_small'),
        'model_config_lst': [{
            'is_state': False,
            'model_name': 'bert',
            'pretrained_model_path': os.path.join(root, 'model/bert_chinese_wwm_ext_pytorch')
        }]
    },
    # 设问
    'shewen': {
        'checkpoint_lst':[os.path.join(root, 'model/rhetoric_model/Shewen_PretrainedBert_1e-05_32_None.pt')],
        'use_bert': True,
        'embd_path': os.path.join(root, 'model/word_embedding/tencent_small'),
        'model_config_lst': [{
            'is_state': False,
            'model_name': 'bert',
            'pretrained_model_path': os.path.join(root, 'model/bert_chinese_wwm_ext_pytorch')
        }]
    },
    # 反问
    'fanwen': {
        'checkpoint_lst':[os.path.join(root, 'model/rhetoric_model/Fanwen_PretrainedBert_1e-06_64_0.3.pt')],
        'use_bert': True,
        'embd_path': os.path.join(root, 'model/word_embedding/tencent_small'),
        'model_config_lst': [{
            'is_state': False,
            'model_name': 'bert',
            'pretrained_model_path': os.path.join(root, 'model/bert_chinese_wwm_ext_pytorch')
        }],
        'max_seq_len': 120,
        'need_mask': True
    }
    # 'embd_path': os.path.join(root, 'model/word_embedding/tencent_small'),
    # 'BERT_ROOT_PATH': os.path.join(root,'model/bert_chinese_wwm_ext_pytorch')
}

pattern_config = {
    'fanwen':[
        r'.*(?:岂不|岂非|岂止|岂可|岂)+.*[?？]+.*',
        r'.*(?:不都是|不还是|不也是|不就是|不是应该|还不是|这不是|不更是)+[^，。？！；：“”‘’,;:\?\!"\']*[吗呀嘛么]+.*[?？]+.*',
        r'.*(?:不就|不都|不也|不正)+[^，。？！；：“”‘’,;:\?\!"\']*[吗呀嘛么]+[?？]+.*',
        r'.*(?:何尝|何苦|何妨|何必|何曾|何至于)+.*[?？]+.*',
        r'.*(?:怎会|怎能|怎敢|怎舍得|怎不|怎样不|怎样能|怎样可以|又怎么|怎么能|怎么可以|怎么能够|怎么可能|怎么舍得|怎么会是|又能怎么|又能怎样|怎么忍受|怎么承受|怎么会不)+.*[呢啊呀]*.*[?？]+.*',
        r'.*[再不|可是|但是|可|但]+[^。？！；：“”‘’;:\?\!"\']+(?:怎么能|怎么有|怎能).*[?？]+.*',
        r'.*(?:谁能|谁叫|谁不|谁说|谁又|谁会|有谁|可谁|谁还|谁舍得)+[^，。？！；：“”‘’,;:\?\!"\']+[呢吗啊呀嘛么]+.*[?？]+.*',
        r'.*(?:哪能|哪会|哪还)+[^，。？！；：“”‘’,;:\?\!"\']+[呢吗啊呀嘛么]+.*[?？]+.*',
        r'.*哪里?.+(?:还有|能有)+.*[?？]+.*',
        r'.*能不[^，。？！；：“”‘’,;:\?\!"\']+[吗嘛么]+.*[?？]+.*',
        r'.*不应该[^，。？！；：“”‘’,;:\?\!"\']*[呢吗嘛]+.*[?？]+.*',
        r'.*[^是]不是[^，。？！；：“”‘’,;:\?\!"\']*[呢吗嘛]+.*[?？]+.*',
        r'.*有什么[理由|借口|原因]+不.*[?？]+.*',
        r'.*(?:为什么|为何|为啥)不[能|肯|敢|愿意|可以]*.+[呢啊呀]+.*[?？]+.*',
        r'.*难道.+[吗嘛么]+.*[?？]+.*',
        r'.*难道[^，。？！；：“”‘’,;:\?\!"\']*(?:不|只有|只能|真的|就是|也是)+.*[?？]+.*',
        r'.*(?:难道)[^，。？！；：“”‘’,;:\?\!"\']+不成.*[?？]+.*',
        r'.*(?:又|可|但|可是|但是|还)有多少[^，。？！；：“”‘’,;:\?\!"\']+(?:能|会|可以|敢|肯|愿意)+.*[?？]+.*',
        r'.*又(?:有谁|有几个|有什么|有多少|有几件|能否|有何|从何|算得了什么).*[?？]+.*',
        r'.*(?:总不能|总不得|总不会).+吧.*[?？]+.*',
        r'.*(?:如果|假如|假设|假想|设想|试想|设问|万一|如此|这样|现在不|不这么|不这样).+(?:还会|还能|还有|还可以)[^，。？！；：“”‘’,;:\?\!"\']+[呢吗嘛么]+[?？]+.*',
        r'.*(?:但|可|但是|可是).*(?:为什么|为何|为啥)(?:一定)?要.*[?？]+.*',
        r'.*哪里?[^，。？！；：“”‘’,;:\?\!"\']+又[^，。？！；：“”‘’,;:\?\!"\']+[?？]+.*',
        r'.*更*何况.+呢.*[?？]+.*',
    ]
}
