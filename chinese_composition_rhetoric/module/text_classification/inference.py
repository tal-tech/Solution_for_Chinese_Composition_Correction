import torch
from classify_utils import tokenizer, sentence_split, load_json, metrics
import pickle
import jieba
import os
import time
import pandas as pd
import numpy as np
# from pytorch_transformers import BertTokenizer, AutoTokenizer
from transformers import BertTokenizer
from model.bert import BertForTextClassification
from model.BiLSTM import BiLSTMClassifier
from model.LSTM import LSTMClassifier
from model.RCNN import RCNN
from model.roberta import RobertaForTextClassification


# def load_model(checkpoint, device):
#     with open(checkpoint, 'rb') as f:
#         #torch.cuda.set_device(0)
#         model = torch.load(f).to(device)
#     model.eval()
#     return model
    
def load_model(checkpoint, embd_path, device, model_config):
    is_state = model_config['is_state']
    if is_state:
        model_name = model_config['model_name']
        batch_size = model_config['batch_size'] if 'batch_size' in model_config else 64
        output_size = model_config['output_size'] if 'output_size' in model_config else 2
        hidden_size = model_config['hidden_size'] if 'output_size' in model_config else 64
        keep_rate = model_config['keep_rate'] if 'keep_rate' in model_config else 0.2
        biFlag = model_config['biFlag'] if 'biFlag' in model_config else False
        pretrained_model_path = model_config['pretrained_model_path']
        embeddings = np.load(os.path.join(embd_path, 'matrix.npy'))
        word_embeddings = torch.Tensor(embeddings).to(device)
        vocab_size = word_embeddings.shape[0]
        embedding_length = word_embeddings.shape[1]
        if model_name == 'bert':
            model = BertForTextClassification(pretrained_model_path, output_size)
        elif model_name =='lstm':
            model = LSTMClassifier(batch_size, output_size, hidden_size, vocab_size, embedding_length, word_embeddings, keep_rate)
        elif model_name == 'bilstm':
            model = BiLSTMClassifier(batch_size, output_size, hidden_size, vocab_size, embedding_length, word_embeddings, keep_rate, biFlag)
        elif model_name == 'rcnn':
            model = RCNN(batch_size, output_size, hidden_size, vocab_size, embedding_length, word_embeddings, keep_rate)
        elif model_name == 'roberta':
            model = RobertaForTextClassification(pretrained_model_path, output_size)
        else:
            raise ValueError('model name wrong')
        # print('load_state'*10)
        # print(checkpoint)
        # print('device', device)
        # print('biFlag', biFlag)
        # print(model)
        model.load_state_dict(torch.load(checkpoint, map_location=device))
    else:
        with open(checkpoint, 'rb') as f:
            # model = torch.load(f).to(device)
            model = torch.load(f, map_location=device)
        model.eval()
    return model

class TextClassifier():
    def __init__(self, embd_path, checkpoint_lst, model_config_list, BERT_ROOT_PATH=None):
        if(type(checkpoint_lst) is not list):
            raise TypeError('Argument checkpoint_lst must be a list of checkpoint path')
        if(len(checkpoint_lst)%2!=1):
            raise ValueError('Checkpoint list must contain odd number of checkpoint for majority voting.')

        self.w2i = pickle.load(open(os.path.join(embd_path, 'w2i.pkl'),'rb'))
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        #print('Loading {} models from checkpoint list'.format(len(checkpoint_lst)))
        self.models = [load_model(checkpoint, embd_path, self.device, model_config) for checkpoint,model_config in zip(checkpoint_lst,model_config_list)]
        self.softmax = torch.nn.Softmax()
        self.min_votes = int((len(checkpoint_lst)+1) / 2)
        
        if(BERT_ROOT_PATH is not None):
            self.use_bert = True
            self.bert_tokenizer = BertTokenizer.from_pretrained(os.path.join(BERT_ROOT_PATH, 'vocab.txt'))
            # self.bert_tokenizer = AutoTokenizer.from_pretrained(os.path.join(BERT_ROOT_PATH, 'vocab.txt'))
        else:
            self.use_bert = False

    # def predict(self, text, vote='hard', max_seq_len=80):
    #     if(self.use_bert):
    #         sequence = self.bert_tokenizer.encode(''.join(['[CLS]', text, '[SEP]']))
    #         if(len(sequence)<max_seq_len):
    #             sequence += [0 for _ in range(max_seq_len-len(sequence))]
    #         else:
    #             sequence = []
    #     else:
    #         sequence = tokenizer(text, self.w2i, max_seq_len=max_seq_len)
    #     if(sequence==[]):
    #         return -1, -1
    #     else:
    #         sequence = np.array(sequence).reshape(1, -1)
    #         inp = torch.tensor(sequence, dtype=torch.long).to(self.device)
    #         y_hat_lst, y_proba_lst = [], []
    #         for model in self.models:
    #             proba = self.softmax(model(inp, batch_size=1))
    #             y_hat = torch.argmax(proba).cpu().detach().numpy()
    #             y_hat_lst.append(y_hat)
    #             y_proba_lst.append(proba.cpu().detach().numpy()[0][1])
    #         if(vote=='hard'):
    #             if(sum(y_hat_lst)>=self.min_votes):
    #                 return 1, sum(y_proba_lst)/len(y_proba_lst)
    #             else:
    #                 return 0, sum(y_proba_lst)/len(y_proba_lst)
    #         else:
    #             avg_proba = sum(y_proba_lst)/len(y_proba_lst)
    #             return int(avg_proba>0.5), avg_proba

    def predict(self, text, vote='hard', max_seq_len=80):
        if(self.use_bert):
            sequence = self.bert_tokenizer.encode(''.join(['[CLS]', text, '[SEP]']))
            if(len(sequence)<max_seq_len):
                sequence += [0 for _ in range(max_seq_len-len(sequence))]
            sequence = sequence[:max_seq_len]
        else:
            sequence = tokenizer(text, self.w2i, max_seq_len=max_seq_len)
        sequence = np.array(sequence).reshape(1, -1)
        inp = torch.tensor(sequence, dtype=torch.long).to(self.device)
        y_hat_lst, y_proba_lst = [], []
        for model in self.models:
            model.to(self.device)
            proba = self.softmax(model(inp, batch_size=1))
            y_hat = torch.argmax(proba).cpu().detach().numpy()
            y_hat_lst.append(y_hat)
            y_proba_lst.append(proba.cpu().detach().numpy()[0][1])
        if(vote=='hard'):
            if(sum(y_hat_lst)>=self.min_votes):
                return 1, sum(y_proba_lst)/len(y_proba_lst)
            else:
                return 0, sum(y_proba_lst)/len(y_proba_lst)
        else:
            avg_proba = sum(y_proba_lst)/len(y_proba_lst)
            return int(avg_proba>0.5), avg_proba

    def tokenize_batch(self, batch_list, max_seq_len=80):
        batch_seq_list = []
        for text in batch_list:
            # tokenize
            if(self.use_bert):
                sequence = self.bert_tokenizer.encode(''.join(['[CLS]', text, '[SEP]']))
                if(len(sequence)<max_seq_len):
                    sequence += [0 for _ in range(max_seq_len-len(sequence))]
                sequence = sequence[:max_seq_len]
            else:
                sequence = tokenizer(text, self.w2i, max_seq_len=max_seq_len)
            batch_seq_list.append(sequence)
        return batch_seq_list

    def tokenize_batch_mask(self, batch_list, max_seq_len=80):
        batch_seq_list = []
        for text in batch_list:
            # tokenize
            attention_mask = None
            if(self.use_bert):
                # sequence = self.bert_tokenizer.encode(''.join(['[CLS]', text, '[SEP]']))
                # if(len(sequence)<max_seq_len):
                #     sequence += [0 for _ in range(max_seq_len-len(sequence))]
                # sequence = sequence[:max_seq_len]
                res = self.bert_tokenizer.encode_plus(text,
                                            add_special_tokens=True,
                                            pad_to_max_length=True,
                                            max_length=max_seq_len)
                sequence = res['input_ids']
                attention_mask = res['attention_mask']
            else:
                sequence = tokenizer(text, self.w2i, max_seq_len=max_seq_len)
            batch_seq_list.append({'sequence':sequence, 'attention':attention_mask})
        return batch_seq_list

    def predict_batch(self, batch_list, vote='hard', max_seq_len=80, max_batch_size=64):
        if len(batch_list) > max_batch_size:
            raise ValueError('data size is bigger than max_batch_size!')
        batch_size = len(batch_list)
        batch_seq_list = self.tokenize_batch(batch_list, max_seq_len=max_seq_len)
        inp = torch.tensor(batch_seq_list).to(self.device)
        # print('self.device', self.device)
        model_hat_lst, model_proba_lst = [], []
        for model in self.models:
            model.to(self.device)
            proba = self.softmax(model(inp, batch_size=batch_size))
            y_proba_lst = [x[1] for x in proba.cpu().detach().numpy()]
            y_hat_lst = [1 if x>=0.5 else 0 for x in y_proba_lst]
            model_hat_lst.append(y_hat_lst)
            model_proba_lst.append(y_proba_lst)
        proba_lst, pred_lst = [], []
        model_proba_lst = np.array(model_proba_lst)
        proba_lst = list(np.sum(model_proba_lst,axis=0)/model_proba_lst.shape[0])
        if(vote=='hard'):
            model_hat_lst = np.array(model_hat_lst)
            pred_lst = [1 if x>=self.min_votes else 0 for x in np.sum(model_hat_lst,axis=0)]
        else:
            pred_lst = [1 if x>=0.5 else 0 for x in proba_lst]
        return pred_lst, proba_lst

    def predict_batch_mask(self, batch_list, vote='hard', max_seq_len=80, max_batch_size=64, need_mask=False):
        if len(batch_list) > max_batch_size:
            raise ValueError('data size is bigger than max_batch_size!')
        batch_size = len(batch_list)
        batch_seq_list = self.tokenize_batch_mask(batch_list, max_seq_len=max_seq_len)
        inp_list = [x['sequence'] for x in batch_seq_list] 
        inp = torch.tensor(inp_list).to(self.device)
        atten_mask_list = [x['attention'] for x in batch_seq_list]
        atten_mask = None
        if atten_mask_list[0] is not None:
            atten_mask = torch.tensor(atten_mask_list).to(self.device)
        # print('self.device', self.device)
        model_hat_lst, model_proba_lst = [], []
        for model in self.models:
            model.to(self.device)
            if atten_mask is not None and need_mask:
                proba = self.softmax(model(inp, attention_mask=atten_mask, batch_size=batch_size))
            else:
                proba = self.softmax(model(inp, batch_size=batch_size))
            y_proba_lst = [x[1] for x in proba.cpu().detach().numpy()]
            y_hat_lst = [1 if x>=0.5 else 0 for x in y_proba_lst]
            model_hat_lst.append(y_hat_lst)
            model_proba_lst.append(y_proba_lst)
        proba_lst, pred_lst = [], []
        model_proba_lst = np.array(model_proba_lst)
        proba_lst = list(np.sum(model_proba_lst,axis=0)/model_proba_lst.shape[0])
        if(vote=='hard'):
            model_hat_lst = np.array(model_hat_lst)
            pred_lst = [1 if x>=self.min_votes else 0 for x in np.sum(model_hat_lst,axis=0)]
        else:
            pred_lst = [1 if x>=0.5 else 0 for x in proba_lst]
        return pred_lst, proba_lst


    def predict_all(self, text_list, vote='hard', max_seq_len=80, max_batch_size=64):
        batch_count = len(text_list) // max_batch_size + 1
        st_idx, ed_idx = 0, 0
        pred_lst, proba_lst = [], []
        for batch in range(batch_count):
            batch_size = min(len(text_list)-ed_idx, max_batch_size)
            st_idx = ed_idx
            ed_idx = st_idx + batch_size
            batch_list = text_list[st_idx:ed_idx]
            if len(batch_list) == 0:
                break
            batch_pred_list, batch_proba_list = self.predict_batch(batch_list, max_seq_len=max_seq_len, max_batch_size=max_batch_size)
            pred_lst += batch_pred_list
            proba_lst += batch_proba_list
        return pred_lst, proba_lst

    def predict_all_mask(self, text_list, vote='hard', max_seq_len=80, max_batch_size=64, need_mask=False):
        batch_count = len(text_list) // max_batch_size + 1
        st_idx, ed_idx = 0, 0
        pred_lst, proba_lst = [], []
        for batch in range(batch_count):
            batch_size = min(len(text_list)-ed_idx, max_batch_size)
            st_idx = ed_idx
            ed_idx = st_idx + batch_size
            batch_list = text_list[st_idx:ed_idx]
            if len(batch_list) == 0:
                break
            batch_pred_list, batch_proba_list = self.predict_batch_mask(batch_list, max_seq_len=max_seq_len, max_batch_size=max_batch_size, need_mask=need_mask)
            pred_lst += batch_pred_list
            proba_lst += batch_proba_list
        return pred_lst, proba_lst



def find_best_model(embd_path, model_save_root_path, valid_data_path, BERT_ROOT_PATH=None, metric_save_path=None):
    from utils import load_json, metrics
    import time, os
    import pandas as pd
    if(metric_save_path is None):
        metric_save_path = 'performance'

    if(not os.path.exists(metric_save_path)):
        os.makedirs(metric_save_path)

    valid = load_json(valid_data_path).get('data')
    print('Validation size {}'.format(len(valid)))

    model_lst, params_lst = [], []
    acc_lst, prec_lst, rec_lst, f1_lst, auc_lst, f_05_lst, speed_lst = [], [], [], [], [], [], []
    df = pd.DataFrame()
 
    if(os.path.exists(os.path.join(metric_save_path, 'all_metric_valid.csv'))):
        done_metrics = pd.read_csv(os.path.join(metric_save_path, 'all_metric_valid.csv'))
        done_lst = list(done_metrics['parameters'])
    else:
        done_lst = []
        done_metrics = pd.DataFrame()
    
    for dir in os.listdir(model_save_root_path):
        print('Evaluating model {}'.format(dir))
        dir_path = os.path.join(model_save_root_path, dir)
        if(not os.path.isdir(dir_path)):
            print('{} is not a directory, pass'.format(dir_path))
            continue
        for name in os.listdir(dir_path):
            if('.pt' not in name or name in done_lst):
                continue
            try:
                checkpoint_lst = [os.path.join(dir_path, name)]
                if('bert' in dir):
                    BERT_ROOT_PATH = '/share/作文批改/model/bert/chinese_wwm_ext_pytorch'
                    model = TextClassifier(embd_path, checkpoint_lst, BERT_ROOT_PATH)
                else:
                    model = TextClassifier(embd_path, checkpoint_lst)

                y_hat_lst, y_proba_lst, y_truth_lst = [], [], []
                time_lst = []
                
                for item in valid:
                    y_truth = item['label']
                    text = item['text']

                    st = time.time()
                    y_hat, y_proba = model.predict(text)
                    ed = time.time()

                    if(y_hat!=-1):
                        y_hat_lst.append(y_hat)
                        y_proba_lst.append(y_proba)
                        y_truth_lst.append(y_truth)
                        time_lst.append(ed-st)

                acc, prec, rec, f1, auc, f_05 = metrics(y_truth_lst, y_hat_lst, y_proba_lst)
                print('{}: Accuracy {}, precision {}, recall {}, F1 {}, F0.5 {} auc {}'.format(name, acc, prec, rec, f1, f_05, auc))
                print('-'*66)
                avg_time = round(sum(time_lst) / len(time_lst), 5)

                model_lst.append(dir)
                params_lst.append(name)
                acc_lst.append(acc)
                prec_lst.append(prec)
                rec_lst.append(rec)
                f1_lst.append(f1)
                auc_lst.append(auc)
                speed_lst.append(avg_time)
                f_05_lst.append(f_05)

                
                df = pd.DataFrame()
                df['model'] = model_lst
                df['parameters'] = params_lst
                df['acc'] = acc_lst
                df['prec'] = prec_lst
                df['rec'] = rec_lst
                df['f1'] = f1_lst
                df['f0.5'] = f_05_lst
                df['auc'] = auc_lst
                df['s/sentence'] = speed_lst
                df = pd.concat([df, done_metrics], axis=0)
                df.to_csv(os.path.join(metric_save_path, 'all_metric_valid.csv'), index=False)
            except:
                print('Error for model={}'.format(name))
    
    if(df.shape[0]>0):
        model_types = set(df['model'])
        best_model_idx_lst = []
        for model_type in model_types:
            best_metric = -1
            best_model_idx = 0
            for i in range(df.shape[0]):
                if(df['model'].iloc[i]==model_type):
                    metric = df['f0.5'].iloc[i]
                    if(metric>best_metric):
                        best_metric = metric
                        best_model_idx = i
            best_model_idx_lst.append(best_model_idx) 
        best_model_metric = df.iloc[best_model_idx_lst]
        best_model_metric.to_csv(os.path.join(metric_save_path, 'best_metric_valid.csv'), index=False)



def test(embd_path, checkpoint_lst, test_data_root_path, BERT_ROOT_PATH=None, keywords=None):
    model = TextClassifier(embd_path, checkpoint_lst, BERT_ROOT_PATH)
    if(keywords is None):
        test_file_lst = [x for x in os.listdir(test_data_root_path) if 'test' in x and '.json' in x]
    else:
        test_file_lst = [x for x in os.listdir(test_data_root_path) if 'test' in x and '.json' in x and x in keywords]

    test_data_lst, test_size_lst, ratio_lst = [], [] ,[]
    acc_lst, prec_lst, recall_lst, f1_lst, f05_lst, auc_lst = [], [], [], [], [], []

    for test_file in test_file_lst:
        print('Loading {}'.format(test_file))
        test = load_json(os.path.join(test_data_root_path, test_file)).get('data')
        ratio = sum([x['label'] for x in test]) / len(test)
        
        if(ratio==0):
            # No positive examples in test data
            acc, prec, rec, f1, auc, f_05 = 'NA', 'NA', 'NA', 'NA', 'NA', 'NA'
        else:
            y_hat_lst, y_proba_lst, y_truth_lst = [], [], []
            time_lst, text_lst = [], []
            
            for item in test:
                try:
                    y_truth = item['label']
                    text = item['text']

                    st = time.time()
                    y_hat, y_proba = model.predict(text, 'soft')
                    ed = time.time()

                    if(y_hat!=-1):
                        y_hat_lst.append(y_hat)
                        y_proba_lst.append(y_proba)
                        y_truth_lst.append(y_truth)
                        time_lst.append(ed-st)
                        text_lst.append(text)
                except:
                    print('Error for input: {}'.format(text))

            df = pd.DataFrame()
            df['text'] = text_lst
            df['label'] = y_truth_lst
            df['prediction'] = y_hat_lst
            df['probability'] = y_proba_lst
            df['time/(s)'] = time_lst

            # Only save full test data prediction
            if(test_file=='test.json'):
                if(not os.path.exists('prediction')):
                    os.makedirs('prediction')
                df.to_csv('prediction/test_prediction.csv', index=False)

            acc, prec, rec, f1, auc, f_05 = metrics(y_truth_lst, y_hat_lst, y_proba_lst)
        
        print(test_file.replace('.json', ''))
        print('Test data size {}, ratio {}'.format(len(test), ratio))
        print('Test accuracy {}, precision {}, recall {}, F1 {}, F0.5 {}, auc {}'.format(acc, prec, rec, f1, f_05, auc))
        avg_time = round(sum(time_lst) / len(time_lst), 5)
        print('-'*60)

        test_data_lst.append(test_file.split('.')[0])
        test_size_lst.append(len(test))
        ratio_lst.append(ratio)
        acc_lst.append(acc)
        prec_lst.append(prec)
        recall_lst.append(rec)
        f1_lst.append(f1)
        f05_lst.append(f_05)
        auc_lst.append(auc)

        test_metric_df = pd.DataFrame()
        test_metric_df['test_data'] = test_data_lst
        test_metric_df['test_size'] = test_size_lst
        test_metric_df['ratio'] = ratio_lst
        test_metric_df['accuracy'] = acc_lst
        test_metric_df['precision'] = prec_lst
        test_metric_df['recall'] = recall_lst
        test_metric_df['f1'] = f1_lst
        test_metric_df['f0.5'] = f05_lst
        test_metric_df['auc'] = auc_lst
        test_metric_df.to_csv('prediction/test_metric_performance.csv', index=False)


def find_postive_example(data, embd_path, checkpoint_lst, save_path, max_num_sent=None, BERT_ROOT_PATH=None):
    from utils import load_json
    import pandas as pd
    import time
    from sklearn.utils import shuffle

    result, proba = [], []
    data = shuffle(data)
    model = TextClassifier(embd_path, checkpoint_lst, BERT_ROOT_PATH)

    st = time.time()
    for count, text in enumerate(data):
        #content = item['content']
        sent_lst = sentence_split(text)

        for sent in sent_lst:
            y_hat_1, p = model.predict(sent)

            if(y_hat_1==1 and sent not in result and len(sent)>5):
                print(sent)
                result.append(sent)
                proba.append(p)

                if(len(result)%100==0):
                    current = time.time()
                    print('Collapsed {} minutes'.format((current-st)/60))
                    print('Retrived {} postive examples, scan {}%'.format(len(result), round(100*count/len(data), 4)))
                    df = pd.DataFrame()
                    df['positive'] = result
                    df['probability'] = proba
                    df.to_csv(save_path, index=False)

                if(max_num_sent!=None):
                    if(len(result)>=max_num_sent):
                        break
    
    print('Retrived {} postive examples.'.format(len(result)))
    df = pd.DataFrame()
    df['positive'] = result
    df['probability'] = proba
    df.to_csv(save_path, index=False)



def demo(embd_path, checkpoint_lst, BERT_ROOT_PATH=None):
    print('Model initialization...')
    model = TextClassifier(embd_path, checkpoint_lst, BERT_ROOT_PATH)

    while(True):
        try:
            text = input("Please enter something: ")
            if(text=='exit'):
                break
            y_hat, y_proba = model.predict(text)
            print('prediction: {}, probability:{}'.format(y_hat, round(y_proba, 3)))
        except:
            pass



def inner_helper(model, sentence_lst, result, key):
    for sent in sentence_lst:
        y_hat, y_proba = model.predict(sent)
        if(y_hat==1):
            result[key].append(sent)
    return result

def union_symbol(s):
    dic = {
            ',':'，', 
            ';':'；',
            '!':'！',
            '?':'？',
            ':':'：',
            '.':'。',
            '[' : '【',
            ']' : '】',
            '(' : '（',
            ')' : '）'
        } 
    for d, d_ in dic.items():
        s = s.replace(d, d_)
    return s


def helper(text):
    result = {
                'biyu' : [],
                'niren' : [],
                'paibi' : [],
                'fanwen' : [],
                'shewen' : [],
                'waimao' : [],
                'dongzuo' : [],
                'xinli' : [],
                'huanjing' : [],
                'shentai' : [],
                'chengyu' : [],
                'suyu' : [],
                'mingyan' : []
                }

    text = union_symbol(text)
    sentence_lst = sentence_split(text)

    embd_path = '/share/作文批改/model/word_embd/tencent_small'
    BERT_ROOT_PATH = '/share/作文批改/model/bert/chinese_wwm_ext_pytorch'



    key = 'biyu'
    checkpoint_lst = ['/share/作文批改/model/xiuci/biyu/v02/pretrained_bert/PretrainedBert_1e-05_16_0.5.pt']
    model = TextClassifier(embd_path, checkpoint_lst, BERT_ROOT_PATH)
    result = inner_helper(model, sentence_lst, result, key)

    key = 'niren'
    checkpoint_lst = ['/share/作文批改/model/xiuci/niren/v02/pretrained_bert/PretrainedBert_5e-05_64_None.pt']
    model = TextClassifier(embd_path, checkpoint_lst, BERT_ROOT_PATH)
    result = inner_helper(model, sentence_lst, result, key)

    key = 'paibi'
    checkpoint_lst = ['/share/作文批改/model/xiuci/paibi/v02/pretrained_bert/PretrainedBert_1e-05_16.pt']
    model = TextClassifier(embd_path, checkpoint_lst, BERT_ROOT_PATH)
    result = inner_helper(model, sentence_lst, result, key)

    key = 'dongzuo'
    checkpoint_lst = ['/share/作文批改/model/miaoxie/dongzuo/v02/rcnn/rcnn_0.0005_128_128_1.0.pt']
    model = TextClassifier(embd_path, checkpoint_lst)
    result = inner_helper(model, sentence_lst, result, key)

    key = 'xinli'
    checkpoint_lst = ['/share/作文批改/model/miaoxie/xinli/v03/rcnn/rcnn_0.001_64_64_0.5.pt']
    model = TextClassifier(embd_path, checkpoint_lst)
    result = inner_helper(model, sentence_lst, result, key)

    key = 'huanjing'
    checkpoint_lst = ['/share/作文批改/data/描写/环境描写/v02/model/pytorch/lstm_with23/lstm_0.0005_256_128_0.7.pt']
    model = TextClassifier(embd_path, checkpoint_lst)
    result = inner_helper(model, sentence_lst, result, key)

    key = 'waimao'
    checkpoint_lst = ['/share/作文批改/data/描写/外貌描写/v03/model/pytorch/lstm_with23/lstm_0.0005_256_256_1.0.pt']
    model = TextClassifier(embd_path, checkpoint_lst)
    result = inner_helper(model, sentence_lst, result, key)

    key = 'shentai'
    checkpoint_lst = ['/share/作文批改/data/描写/神态描写/v02/model/pytorch/pretrained_bert_with3/PretrainedBert_1e-05_16_None.pt']
    model = TextClassifier(embd_path, checkpoint_lst, BERT_ROOT_PATH)
    result = inner_helper(model, sentence_lst, result, key)    

    for k in result.keys():
        print('This is {}'.format(k))
        tmp = result[k]
        for item in tmp:
            print(item)
        print('-'*60)
        print()

    from utils import save_json
    save_json(result, '/share/作文批改/自研结果.json')


    

if __name__ =='__main__':

    # text = '“草长莺飞二月天，拂堤杨柳醉春烟。”生机勃勃的春天来到了，万物复苏，这正是放风筝的好时节。郊外小朋友们正兴致勃勃地放着风筝。 五颜六色的风筝在天空中上下翻飞，看，那是“燕子”，那是“山鹰”，那是“大蜈蚣”，它们把天空点缀得特别美丽。小强在爸爸妈妈的帮助下放起了三角风筝，风筝摇摇摆摆地爬上天空，后面的两根丝带随风起舞。小强一家人望着风筝 越飞越高，笑容写在了他们的脸上。小睿、小明和小花三人结伴放风筝。小睿举着一只美丽的燕子风筝，小明在前面像一名百米冲刺的运动员，低着头只顾拼命地拉着线奔跑。几次尝试下来，燕子风筝只是奋力向上跃了几下，很快就摇摇晃晃、无精打采地落了下来。小明累得气喘吁吁，小睿满脸沮丧地看着落在草地上的风筝，这是怎么回事呢？一旁的小花看得认真，她大声提醒道:“小明，你不能只顾着向前跑，应当迎着风跑，风筝才能乘风冲上蓝天。风筝线还要边跑边放，你不能扯着线不放，线太紧风筝肯定飞不上天的。”她这么一嚷嚷，小明才回过神来，他不好意思地笑了，都怪我太心急了，忘记了放线。”“没关系，找出了失败的原因，就有成功的希望， 再试一次，你们肯定行的！”小强的爸爸闻声而来，鼓励他们。“是啊，失败乃成功之母，这一次我们要注意动作，好好配合。”小伙伴们也在互相提醒，互相加油。小睿又把风筝高高举起，向上一拋，小明则顺着风势—边飞奔，一边拉线放线。在他们的齐心协力下，燕子风筝渐渐离开了地面，迎着扑面的春风，展开美丽的翅旁，勇敢地向天空飞去。草地上 传来他们一阵阵的欢呼声，如银铃般清脆,如驼铃般悠远，与这美好的 舂色融为了一体。蔚蓝的天空中，多了一只色彩斑斓的“小燕子”，也多了—份小伙伴们的希望。'
    # #text = '跳起来摘苹果.春风是寒冬的向往,丰硕是金秋的向往,雨露是大地的向往,海岸是风帆的向往,欢乐是痛苦的向往,蓝天是小鸟的向往,大海是鱼儿的向往,旭日是黎明的向往.小的时候,向往长大；长大之后,向往读书；读书之后,向往工作；工作之后,向往一份温馨的爱；有了爱之后,向往有一个幸福的家.可以说,向往是随着年龄的增长而不断变化目标,向往是随着阅历而不断走向完美.向往是一条美丽的飘带,一头牢牢地系在自己的灵魂深处,一头高高飘扬于广袤的人生天空.向往给人以希望,给人以动力.“黑夜给了我黑色的眼睛,我却用它来寻找光明.”人生其实就是在向往中体现价值,生活就是在向往中追求美好,生命就是在向往中走向成熟.因此,没有向往的人生是黯淡的,没有向往的人生是空虚的,没有向往的生命是苍白的.向往可以在充实中度过,也可以在寂寞中度过,还可以在无奈中度过.向往可以使你成为潺潺的小溪,也可以使你成为滔滔的江河,还可以使你成为茫茫的海洋.向往是思想的折射,灵魂的写照,行动的先导。有的人向往事业的成功,于是就孜孜以求,默默耕耘；有的人向往奉献的快乐,于是就淡泊明志,心底无私；有的人向往生命的辉煌,于是就志存高远,胸怀天下；有的人向往人格的升华,于是就洁身自好,一尘不染；有的人向往正气的弘扬,于是就大义凛然,气贯长虹；因此,向往有好坏之分,是非之别.正可谓“高尚是高尚者的通行证,卑鄙是卑鄙者的墓志铭”.要想使向往成为现实,就需要百折不挠的坚强,全力以赴的投入,风雨无阻的前行,痴心不改的初衷.人生不可能一帆风顺,身陷逆境一时又无力扭转的颓势,那么只要向往的飘带不断,就会使你从山穷水尽走向柳暗花明.'
    # helper(text)
    st = time.time()
    embd_path = '/share/作文批改/model/word_embd/tencent_small'
    data = load_json('/share/作文批改/data/描写/外貌描写/v02/json/更正标签/valid.json')
    checkpoint_lst = ['/share/作文批改/data/描写/外貌描写/v02/model/pytorch/rcnn_with23/rcnn_0.001_32_128_1.0.pt']
    print('init model')
    model = TextClassifier(embd_path, checkpoint_lst, BERT_ROOT_PATH=None)
    text_list = [x['text'] for x in data['data']]
    y_truth_lst = [x['label'] for x in data['data']]
    print('data prepared')
    pred_lst, proba_lst = [], []
    pred_lst, proba_lst = model.predict_all(text_list)
    # for text in text_list:
    #     y_hat, y_proba = model.predict(text, 'soft')
    #     pred_lst.append(y_hat)
    #     proba_lst.append(y_proba)
    acc, prec, rec, f1, auc, f_05 = metrics(y_truth_lst, pred_lst, proba_lst)
    print('Test accuracy {}, precision {}, recall {}, F1 {}, F0.5 {}, auc {}'.format(acc, prec, rec, f1, f_05, auc))
    print('use time', time.time()-st)



