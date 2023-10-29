import os

root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

desc_key_map = {
    'appearance':'外貌描写',
    'action':'动作描写',
    'psychology':'心理描写',
    'environment':'环境描写',
    'scenery': '景物描写',
    'shentai':'神态描写',
    'language':'语言描写',
    'smell':'嗅觉描写',
    'taste':'味觉描写',
    'hearing':'听觉描写',
    'see': '视觉描写',
    'touch': '触觉描写'
}

model_config = {
    'batch_size': 20,
    'max_len': 128,
    'num_labels': 7,
    'model_path': os.path.join(root, 'model/description_model/desc_7_classifier'),
    'thresholds': [0.914, 0.505, 0.606, 0.454, 0.501, 0.454, 0.748],
    'need_mask': True
}

model_config_old = {
    # 外貌
    'appearance': {
        'checkpoint_lst':[os.path.join(root, 'model/description_model/Appearance_PretrainedBert_1e-05_64_None.pt')],
        'use_bert': True,
        'embd_path': os.path.join(root, 'model/word_embedding/tencent_small'),
        'model_config_lst': [{
            'is_state': False,
            'model_name': 'bert',
            'pretrained_model_path': os.path.join(root, 'model/bert_chinese_wwm_ext_pytorch')
            # 'pretrained_model_path': '/share/作文批改/model/bert/chinese_wwm_ext_pytorch'
        }],
        'max_seq_len': 75,
        'need_mask': True
    },
    # 语言
    'language': {
        'checkpoint_lst':[os.path.join(root, 'model/description_model/language_1e-06_24_None_2.pt')],
        'use_bert': True,
        'embd_path': os.path.join(root, 'model/word_embedding/tencent_small'),
        'model_config_lst': [{
            'is_state': False,
            'model_name': 'bert',
            # 'pretrained_model_path': os.path.join(root, 'model/bert_chinese_wwm_ext_pytorch')
            'pretrained_model_path': os.path.join(root, 'model/roberta')
            # 'pretrained_model_path': '/share/作文批改/model/bert/chinese_wwm_ext_pytorch'
        }],
        'max_seq_len': 256,
        'need_mask': True
    },
    # 动作
    'action': {
        'checkpoint_lst':[os.path.join(root, 'model/description_model/Action_PretrainedBert_3e-06_23_None_16.pt')],
        'use_bert': True,
        'embd_path': os.path.join(root, 'model/word_embedding/tencent_small'),
        # 'embd_path': os.path.join(root, 'model/word_embedding/action_word_emb'),
        'model_config_lst': [{
            'is_state': False,
            'model_name': 'bert',
            'pretrained_model_path': os.path.join(root, 'model/bert_chinese_wwm_ext_pytorch')
            # 'pretrained_model_path': '/share/fwp/tools/auto_text_classifier/atc/data/chinese_roberta_wwm_ext'
        }],
        'max_seq_len': 80
    },
    # 'action': {
    #     'checkpoint_lst':[os.path.join(root, 'model/description_model/Action_lstm_1layer_2dirs_state.pt')],
    #     'use_bert': False,
    #     'embd_path': os.path.join(root, 'model/word_embedding/action_word_emb'),
    #     'model_config_lst': [{
    #         'is_state': True,
    #         'model_name': 'bilstm',
    #         'batch_size': 256,
    #         'output_size': 2,
    #         'hidden_size': 64,
    #         'keep_rate': 0.9,
    #         'biFlag': True,
    #         'pretrained_model_path': None
    #     }]
    # },
    # 心理
    'psychology': {
        'checkpoint_lst':[os.path.join(root, 'model/description_model/Psycho_PretrainedBert_1e-05_32_None.pt')],
        'use_bert': True,
        'embd_path': os.path.join(root, 'model/word_embedding/tencent_small'),
        'model_config_lst': [{
            'is_state': False,
            'model_name': 'bert',
            'pretrained_model_path': os.path.join(root, 'model/bert_chinese_wwm_ext_pytorch')
        }],
        'max_seq_len': 120
    },
    # 环境
    'enviroment': {
        'checkpoint_lst':[os.path.join(root, 'model/description_model/Env_PretrainedBert_5e-06_64_None.pt')],
        'use_bert': True,
        'embd_path': os.path.join(root, 'model/word_embedding/tencent_small'),
        'model_config_lst': [{
            'is_state': False,
            'model_name': 'bert',
            'pretrained_model_path': os.path.join(root, 'model/bert_chinese_wwm_ext_pytorch')
        }],
        'max_seq_len': 120,
        'need_mask': True
    },
    # 景物
    'scenery': {
        'checkpoint_lst':[os.path.join(root, 'model/description_model/Jingwu_PretrainedBert_2e-06_64_0.5.pt')],
        'use_bert': True,
        'embd_path': os.path.join(root, 'model/word_embedding/tencent_small'),
        'model_config_lst': [{
            'is_state': False,
            'model_name': 'bert',
            'pretrained_model_path': os.path.join(root, 'model/bert_chinese_wwm_ext_pytorch')
        }],
        'max_seq_len': 120,
        'need_mask': True
    },
    # 神态
    'shentai': {
        'checkpoint_lst':[os.path.join(root, 'model/description_model/Shentai_PretrainedBert_5e-06_48_None.pt')],
        'use_bert': True,
        'embd_path': os.path.join(root, 'model/word_embedding/tencent_small'),
        'model_config_lst': [{
            'is_state': False,
            'model_name': 'bert',
            'pretrained_model_path': os.path.join(root, 'model/bert_chinese_wwm_ext_pytorch')
        }],
        'max_seq_len': 120
    },
    # 'embd_path': os.path.join(root, 'model/word_embedding/tencent_small'),
    # 'BERT_ROOT_PATH': os.path.join(root, 'model/bert_chinese_wwm_ext_pytorch')
}

# pattern_config = {
#     'smell':[r'.*[闻嗅].*?[香味气].*']
# }

sense_config = {
    'nezha_dir': os.path.join(root, 'model/nezha_base'),
    'multi_config': {
        'batch_size': 20,
        'max_len': 200,
        'epochs': 100,
        'patience': 5,
        'save_dir': os.path.join(root, 'model/description_model'),
        'num_labels': 2,
        'dict_path': os.path.join(root, 'model/nezha_base/vocab.txt'),
        'config_path': os.path.join(root, 'model/nezha_base/bert_config.json'),
        'checkpoint_path': os.path.join(root, 'model/nezha_base/model.ckpt-900000'),
        'tasks': [{'name': 'shijue','label_num': 2}, {'name': 'weijue','label_num': 2}, 
            {'name': 'tingjue','label_num': 2}, {'name': 'chujue','label_num': 2}, 
            {'name': 'xiujue','label_num': 2}],
        'model_name': 'nezha',
        'model_path': os.path.join(root, 'model/description_model/Sense_nezha_base_v2_1.h5')
    },
    'name_map': {
        'shijue':'see','tingjue':'hearing','chujue':'touch','xiujue':'smell','weijue':'taste'
    }
}

