#  -*-  coding:utf-8 -*-
"""
文本分类，只用 cls
"""
import torch
import torch.nn as nn
from transformers import BertPreTrainedModel, BertModel, BertConfig, BertTokenizer


class BertCLS(BertPreTrainedModel):

    def __init__(self,  *args, **kwargs):
        super(BertCLS, self).__init__( *args, **kwargs)
        self.config = args[0]
        # print(self.config)
        self.hidden_size = int(self.config.hidden_size)
        self.num_labels = 7
        self.hidden_dropout_prob = self.config.hidden_dropout_prob
        # self.hidden_dropout_prob = 0.5
        self.token_type_ids_disable = False
        # self.bert_config = BertConfig.from_pretrained(self.config._name_or_path)
        self.bert = BertModel(self.config)
        
        for p in self.parameters():
            p.requires_grad = False

        self.dropout = nn.Dropout(self.hidden_dropout_prob)
        self.fc = nn.Linear(self.hidden_size, self.num_labels)
        self.init_weights()

    def forward(self, input_ids, token_type_ids=None, attention_mask=None, labels=None) -> torch.Tensor:

        outputs = self.bert(input_ids,
                            attention_mask=attention_mask,
                            token_type_ids=token_type_ids)

        cls_hid_out = outputs[1]
        cls_hid_out = self.dropout(cls_hid_out)

        # todo 全联接层
        logits = self.fc(cls_hid_out) # [B, ]
        
        logits = torch.sigmoid(logits)
        outputs = (logits,) + outputs[2:]

        #print(logits.size(), labels.size())

        if labels is not None:
            # loss_fct = nn.MSELoss()
            label_mask = torch.where(labels>=0, 1, 0).view(-1)
            loss_fct = nn.BCELoss()
            loss = loss_fct(logits.view(-1) * label_mask, labels.view(-1) * label_mask)
            #print(loss)
            outputs = (loss,) + outputs

        return outputs


class BaseModel():
    def __init__(self, config):
        self.config = config
        self.batch_size = int(self.config.get('batch_size', 32))
        self.max_len = int(self.config.get('max_len', 128))
        self.num_labels = int(self.config.get('num_labels', 7))
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class MultClassifier(BaseModel):
    
    def __init__(self, config):
        """
        config: 配置
        """
        super().__init__(config)
        self.tokenizer = BertTokenizer.from_pretrained(config['model_path'])
        self.bert_config = BertConfig.from_pretrained(config['model_path'])
        self.model = BertCLS.from_pretrained(config['model_path'])
        self.model = self.model.to(self.device)

    def parser_text_list(self, sent_list):
        """
        对外接口1: 输入字符串列表，返回响应的类别输出
        """
        batch_count = len(sent_list) // self.batch_size + 1 # batch数
        st_idx, ed_idx = 0, 0
        pred_lst, proba_lst = [], []
        # todo 循环 batch
        self.model.eval()
        for batch in range(batch_count):
            batch_size = min(len(sent_list)-ed_idx, self.batch_size)
            st_idx = ed_idx
            ed_idx = st_idx + batch_size
            batch_list = sent_list[st_idx:ed_idx]
            if len(batch_list) == 0:
                break
            batch_pred_list, batch_proba_list = self.parser_batch(batch_list, max_seq_len=self.max_len, max_batch_size=self.batch_size, need_mask=True)
            pred_lst += batch_pred_list
            proba_lst += batch_proba_list
        return pred_lst, proba_lst
    
    def parser_batch(self, batch_list, vote='hard', max_seq_len=80, max_batch_size=64, need_mask=False):
        """ 处理一个batch """
        if len(batch_list) > max_batch_size:
            raise ValueError('data size is bigger than max_batch_size!')
        
        batch_seq_list = self.tokenize_batch_mask(batch_list, max_seq_len=max_seq_len)
        input_list = [x['sequence'] for x in batch_seq_list] 
        input_list = torch.tensor(input_list).to(self.device)
        atten_mask_list = [x['attention'] for x in batch_seq_list]
        atten_mask = None
        if atten_mask_list[0] is not None:
            atten_mask = torch.tensor(atten_mask_list).to(self.device)
        
        model_hat_list, model_proba_list = [], []
        proba = self.model(input_list, attention_mask=atten_mask)
        y_proba_list = proba[0].cpu().detach().numpy() # batch x label_numb
        for i in range(len(y_proba_list)):
            y_proba = y_proba_list[i]
            y_hat_lst = [1 if x>=0.5 else 0 for x in y_proba]
            model_hat_list.append(y_hat_lst)
            model_proba_list.append(y_proba)

        return model_hat_list, model_proba_list

    def tokenize_batch_mask(self, batch_list, max_seq_len=80):
        "token to token_id"
        batch_seq_list = []
        for text in batch_list:
            res = self.tokenizer.encode_plus(text,
                                            add_special_tokens=True,
                                            pad_to_max_length=True,
                                            max_length=max_seq_len)
            sequence = res['input_ids']
            attention_mask = res['attention_mask']
            batch_seq_list.append({'sequence':sequence, 'attention':attention_mask})
        return batch_seq_list




