import os
import numpy as np
# import tensorflow as tf
import tensorflow as tf
# tf.disable_v2_behavior()
# tf.enable_eager_execution()
# from tensorflow.keras.optimizers import Adam
from keras.layers import Lambda, Dense
from tensorflow.python.keras.callbacks import EarlyStopping,ModelCheckpoint
from bert4keras.backend import keras, set_gelu
from bert4keras.tokenizers import Tokenizer
from bert4keras.models import build_transformer_model
from bert4keras.optimizers import Adam, extend_with_piecewise_linear_lr
from bert4keras.snippets import sequence_padding, DataGenerator
from bert4keras.snippets import open
from base_model import BaseModel
from metric_utils import *
config = tf.ConfigProto()
config.gpu_options.allow_growth=True
sess = tf.Session(config=config)
# gpus=tf.config.experimental.list_physical_devices(device_type='XLA_GPU')
# tf.config.experimental.set_memory_growth(gpus[0],True) #设置显存按需申请
# tf.config.experimental.VirtualDeviceConfiguration(memory_limit=2048) #限制最大显存使用2G
import time

set_gelu('tanh')  # 切换gelu版本
AdamLR = extend_with_piecewise_linear_lr(Adam, name='AdamLR')


def init_dir(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

def process_data_one(data, tokenizer, tasks, max_len):
    idxs = list(range(len(data)))
    one_text, one_label = data[0]
    all_token_ids, all_segment_ids, labels = [], [], {k:[] for k in list(one_label.keys())}
    for i in idxs:
        text, label = data[i]
        token_ids, segment_ids = tokenizer.encode(text, maxlen=max_len)
        all_token_ids.append(token_ids)
        all_segment_ids.append(segment_ids)
        for k,v in label.items():
            labels[k].append([v])
    all_token_ids = sequence_padding(all_token_ids)
    all_segment_ids = sequence_padding(all_segment_ids)
    for k,v in one_label.items():
        labels[k] = sequence_padding(labels[k])
    return [all_token_ids, all_segment_ids], [labels[x['name']] for x in tasks]


def sinusoidal(shape, dtype=None):
    """NEZHA直接使用Sin-Cos形式的位置向量
    """
    vocab_size, depth = shape
    embeddings = np.zeros(shape)
    for pos in range(vocab_size):
        for i in range(depth // 2):
            theta = pos / np.power(10000, 2. * i / depth)
            embeddings[pos, 2 * i] = np.sin(theta)
            embeddings[pos, 2 * i + 1] = np.cos(theta)
    return embeddings
class SinusoidalInitializer:
    def __call__(self, shape, dtype=None):
        return sinusoidal(shape, dtype=dtype)


class data_generator_multi(DataGenerator):
    """数据生成器
    """
    def __init__(self, data, tasks, tokenizer, max_len, batch_size=32, buffer_size=None):
        self.tasks = tasks
        self.data = data
        self.batch_size = batch_size
        self.tokenizer = tokenizer
        self.max_len = max_len
        if hasattr(self.data, '__len__'):
            self.steps = len(self.data) // self.batch_size
            if len(self.data) % self.batch_size != 0:
                self.steps += 1
        else:
            self.steps = None
        self.buffer_size = buffer_size or batch_size * 1000

    def __iter__(self, random=False):
        idxs = list(range(len(self.data)))
        if random:
            np.random.shuffle(idxs)
        batch_token_ids, batch_segment_ids, batch_labels = [], [], {x['name']:[] for x in self.tasks}
        for i in idxs:
            text, label = self.data[i]
            token_ids, segment_ids = self.tokenizer.encode(text, maxlen=self.max_len)
            batch_token_ids.append(token_ids)
            batch_segment_ids.append(segment_ids)
            for k,v in label.items():
                batch_labels[k].append([v])
            # batch_labels.append(label)
            if len(batch_token_ids) == self.batch_size or i == idxs[-1]:
                batch_token_ids = sequence_padding(batch_token_ids)
                batch_segment_ids = sequence_padding(batch_segment_ids)
                for k,v in label.items():
                    batch_labels[k] = sequence_padding(batch_labels[k])
                yield [batch_token_ids, batch_segment_ids], [batch_labels[x['name']] for x in self.tasks]
                batch_token_ids, batch_segment_ids, batch_labels = [], [], {x['name']:[] for x in self.tasks}



class Bert4KearsMultiTask(BaseModel):
    def __init__(self, config):
        # config_path,checkpoint_path,dict_path
        '''
        config = {"config_path":,"checkpoint_path":,"save_dir":,"dict_path","tasks":}
        '''
        super().__init__(config)
        init_dir(self.save_dir)
        self.tokenizer = Tokenizer(
            self.config['dict_path'], do_lower_case=True)
        self.graph = tf.compat.v1.get_default_graph()
        self.model_name = self.config['model_name']
        self.best_weights_path = self.config['model_path']
        self.model_path = None
        # self.task_num = int(self.config.get("task_num", 6))
        self.tasks = self.config['tasks']
        self.batch_size = self.config['batch_size']

    def optimizer(self):
        AdamLR = extend_with_piecewise_linear_lr(Adam, name='AdamLR')
        _optimizer = AdamLR(lr=1e-5, lr_schedule={
            1000: 1,
            2000: 0.1
        })
        return _optimizer

    def _init_model(self):
        # 加载预训练模型
        bert = build_transformer_model(
            config_path=self.config['config_path'],
            checkpoint_path=self.config['checkpoint_path'],
            model=self.model_name,
            return_keras_model=False,
        )
        output_b = Lambda(lambda x: x[:, 0], name='CLS-token')(bert.model.output)
        outputs = [Dense(units=item['label_num'], 
                         activation='softmax', 
                         kernel_initializer=bert.initializer, name=item['name'])(output_b) for item in self.tasks]
        
        model = keras.models.Model(bert.model.input, outputs)
        return model

    def _load_data(self,df):
        # df = load_df(path)
        D = []
        for text, label in zip(df['text'], df['label']):
            D.append((str(text), label))
        return D

    def process_data(self, train_path, dev_path, test_path):
        train_data = self._load_data(train_path)
        dev_data = self._load_data(dev_path)
        test_data = self._load_data(test_path)
        # print('train_data', len(train_data))
        train_generator = data_generator_multi(
            train_data, self.tasks, self.tokenizer, self.max_len, self.batch_size)
        dev_generator = data_generator_multi(
            dev_data,  self.tasks, self.tokenizer, self.max_len, self.batch_size)
        test_generator = data_generator_multi(
            test_data, self.tasks, self.tokenizer, self.max_len, self.batch_size)
        # train_processed_data = process_data_one(train_data, self.tokenizer, self.tasks, self.max_len)
        # dev_processed_data = process_data_one(dev_data, self.tokenizer, self.tasks, self.max_len)
        # test_processed_data = process_data_one(test_data, self.tokenizer, self.tasks, self.max_len)
        return train_generator, dev_generator, test_generator

    def train(self, train_path, dev_path, test_path, custom_objects):
        train_generator, dev_generator, test_generator = self.process_data(
            train_path, dev_path, test_path)
        # train_data, dev_data, test_data = self.process_data(
        #     train_path, dev_path, test_path)
        # print('train_generator', len(train_generator))
        # load model
        with self.graph.as_default():
            self.model = self._init_model()
            _optimizer = self.optimizer()
            self.model.compile(
                loss='sparse_categorical_crossentropy',
                optimizer=_optimizer,
                metrics=['accuracy'],
            )
            # start train
            early_stopping_monitor = EarlyStopping(patience=self.patience, verbose=1)
            checkpoint = ModelCheckpoint(self.best_weights_path, monitor='val_loss', verbose=1, save_best_only=True, mode='auto', period=1)
            callbacks = [early_stopping_monitor,checkpoint]

            self.model.fit(train_generator.forfit(),
                                steps_per_epoch=len(train_generator),
                                validation_data = dev_generator.forfit(),
                                validation_steps = len(dev_generator),
                                epochs=self.epochs,
                                callbacks=callbacks)

            # self.model.load_weights(self.best_weights_path)
            # self.model.save(self.model_path)
        self.load_model(self.best_weights_path, custom_objects)
        model_report, pred_list, pred_sample_list = self.evaluate(test_path)
        return model_report

    def load_model(self, model_path, custom_objects):
        # self.model = keras.models.load_model(model_path,
        #                                      custom_objects=custom_objects)
        self.model = self._init_model()
        _optimizer = self.optimizer()
        self.model.compile(
            loss='sparse_categorical_crossentropy',
            optimizer=_optimizer,
            metrics=['accuracy']
        )
        self.model.load_weights(model_path)
        
    def demo(self,text):
        text_list = [text]
        pred_list, pred_sampe_list = self.demo_text_list(text_list)
        pred = pred_sampe_list[0]
        return pred

    def get_preds(self, preds, label_num):
        if label_num == 2:
            return preds[:,1]
        else:
            return np.argmax(preds, axis=1).flatten()
        
    def demo_text_list(self, text_list):
        st = time.time()
        batch_token_ids, batch_segment_ids = [], []
        for text in text_list:
            token_ids, segment_ids = self.tokenizer.encode(text,
                                                           maxlen=self.max_len)
            batch_token_ids.append(token_ids)
            batch_segment_ids.append(segment_ids)
        batch_token_ids = sequence_padding(batch_token_ids)
        batch_segment_ids = sequence_padding(batch_segment_ids)
        # print(batch_token_ids.shape)
        # with self.graph.as_default():
        # print('sense'*10, 'tokenize_time', time.time()-st)
        st = time.time()
        preds = self.model.predict([batch_token_ids, batch_segment_ids])
        # print('sense'*10, 'pred_time', time.time()-st)
        st = time.time()
        pred_list = [{
            'name':
            self.tasks[i]['name'],
            'pred':
            self.get_preds(preds[i], self.tasks[i]['label_num'])
        } for i in range(len(self.tasks))]

        pred_sampe_list = []
        names = [x['name'] for x in self.tasks]
        for name in names:
            name_pred_list = [x for x in pred_list
                              if x['name'] == name][0]['pred']
            if len(pred_sampe_list) == 0:
                for i in range(len(name_pred_list)):
                    pred_sampe_list.append({name: name_pred_list[i]})
            else:
                if len(name_pred_list) != len(pred_sampe_list):
                    raise ValueError(
                        'pred list lengths are not equal, current {} != before {}'
                        .format(len(name_pred_list), len(pred_sampe_list)))
                for i in range(len(name_pred_list)):
                    pred_sampe_list[i][name] = name_pred_list[i]
        # print('sense'*10, 'deal_time', time.time()-st)
        return pred_list, pred_sampe_list
    
    def demo_text_list_batch(self, text_list):
        st = time.time()
        start = 0
        pred_list = [{'name':self.tasks[i]['name'],'pred':[]} for i in range(len(self.tasks))]
        while start < len(text_list):
            batch_num = min(self.batch_size, len(text_list)-start)
            sub_text_list = text_list[start:start+batch_num]
            batch_token_ids, batch_segment_ids = [], []
            for text in sub_text_list:
                token_ids, segment_ids = self.tokenizer.encode(text, maxlen=self.max_len)
                batch_token_ids.append(token_ids)
                batch_segment_ids.append(segment_ids)  
            batch_token_ids = sequence_padding(batch_token_ids)
            batch_segment_ids = sequence_padding(batch_segment_ids)
            # with self.graph.as_default():
            preds = self.model.predict([batch_token_ids, batch_segment_ids])
            for i in range(len(self.tasks)):
                pred_list[i]['pred'] = np.concatenate((pred_list[i]['pred'], self.get_preds(preds[i],self.tasks[i]['label_num'])), axis=0)
            start += batch_num
            # print('start',start)
        # print('pred_list', len(pred_list[0]))
        # print('sense'*10, 'pred_time', time.time()-st)
        pred_sampe_list = []
        names = [x['name'] for x in self.tasks]
        for name in names:
            name_pred_list = [x for x in pred_list if x['name']==name][0]['pred']
            if len(pred_sampe_list) == 0:
                for i in range(len(name_pred_list)):
                    pred_sampe_list.append({name: name_pred_list[i]})
            else:
                if len(name_pred_list) != len(pred_sampe_list):
                    raise ValueError('pred list lengths are not equal, current {} != before {}'.format(
                        len(name_pred_list), len(pred_sampe_list)))
                for i in range(len(name_pred_list)):
                    pred_sampe_list[i][name] = name_pred_list[i]

        return pred_list, pred_sampe_list

    def evaluate(self, df, tradeoff=0.5):
        pred_list, pred_sample_list = self.demo_text_list(df['text'].tolist())
        report_dict = {}
        for item in pred_list:
            name = item['name']
            label_num = [x for x in self.tasks if x['name']==name][0]['label_num']
            name_pred_list = item['pred']
            label_list = [x[name] for x in df['label'].tolist()]
            # print('report of {}'.format(name))
            report_dict[name] = get_report(label_list, name_pred_list, label_num, tradeoff=tradeoff)
            # print()
        return report_dict, pred_list, pred_sample_list
    
    def evaluate_exist_pred(self, df, pred_list, tradeoff=0.5):
        report_dict = {}
        for item in pred_list:
            name = item['name']
            label_num = [x for x in self.tasks if x['name']==name][0]['label_num']
            name_pred_list = item['pred']
            label_list = [x[name] for x in df['label'].tolist()]
            # print('report of {}'.format(name))
            report_dict[name] = get_report(label_list, name_pred_list, label_num, tradeoff=tradeoff)
        return report_dict

    def release(self):
        # K.clear_session()
        del self.model
        del self.graph
        del self.tokenizer

    