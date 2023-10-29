import math
import torch
import torch.nn as nn
import torch.nn.functional as F
from pytorch_transformers import BertConfig, BertTokenizer, BertForSequenceClassification

class BertForTextClassification(nn.Module):
    def __init__(self, pretrained_model_path, num_classes, hidden_size=768, num_hidden_layers=12, num_attention_heads=12, \
            intermediate_size=3072, hidden_act='gelu', hidden_dropout_prob=0.1, attention_probs_dropout_prob=0.1, 
            max_position_embeddings=512, use_pretrained_model=False):
        super(BertForTextClassification, self).__init__()

        if(use_pretrained_model==True):
            print('Reloading pretrained models...')
            self.model = BertForSequenceClassification.from_pretrained(pretrained_model_path, num_labels=num_classes)
        else:
            print('Constructing new Bert by parameters...')
            tokenizer = BertTokenizer.from_pretrained(pretrained_model_path)
            vocab_size = len(tokenizer.ids_to_tokens)

            config = BertConfig(vocab_size, hidden_size, num_hidden_layers, num_attention_heads, \
                                intermediate_size, hidden_act, hidden_dropout_prob, \
                                attention_probs_dropout_prob, max_position_embeddings)
            self.model = BertForSequenceClassification(config)

    def forward(self, input_senquence, attention_mask=None, batch_size=None):
        '''
        Args:
        input_senquence: shape=[batch_size, max_time_step]

        Returns:
        logits: shape=[batch_size, num_labels]
        '''
        # print(input_senquence)
        # print(input_senquence.shape)
        logits = self.model(input_senquence,attention_mask=attention_mask)[0]
        return logits