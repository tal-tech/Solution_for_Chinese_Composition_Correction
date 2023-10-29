import torch
import torch.nn as nn
from torch.autograd import Variable
from torch.nn import functional as F
import numpy as np



class SiameseNet(torch.nn.Module):
    def __init__(self, batch_size, hidden_size, vocab_size, embedding_length, weights, keep_rate, requires_grad=True):
        super(SiameseNet, self).__init__()
        self.batch_size = batch_size
        self.hidden_size = hidden_size
        self.vocab_size = vocab_size
        self.embedding_length = embedding_length

        self.word_embeddings = nn.Embedding(vocab_size, embedding_length)
        self.word_embeddings.weights = nn.Parameter(weights, requires_grad=requires_grad)

        self.lstm = nn.LSTM(embedding_length, hidden_size)
        self.dropout = nn.Dropout(1-keep_rate)
        
    def attention_net(self, lstm_output, final_state):
        hidden = final_state.squeeze(0)
        attn_weights = torch.bmm(lstm_output, hidden.unsqueeze(2)).squeeze(2)
        soft_attn_weights = F.softmax(attn_weights, 1)
        new_hidden_state = torch.bmm(lstm_output.transpose(1, 2), soft_attn_weights.unsqueeze(2)).squeeze(2)

        return new_hidden_state

    def forward(self, query, doc, batch_size=None):
        """ 
        Parameters
        ----------
        query: query input_sentence of shape = (batch_size, num_sequences)
        doc: doc input_sentence of shape = (batch_size, num_sequences)
        batch_size : default = None. Used only for prediction on a single sentence after training (batch_size = 1)

        Returns
        -------
        Output of the linear layer containing logits for pos & neg class which receives its input as the new_hidden_state which is basically the output of the Attention network.
        final_output.shape = (batch_size, output_size)

        """

        input_query = self.word_embeddings(query)
        input_query = input_query.permute(1, 0, 2)
        input_doc = self.word_embeddings(doc)
        input_doc = input_doc.permute(1, 0, 2)
        if batch_size is None:
            h_0 = Variable(torch.zeros(1, self.batch_size, self.hidden_size).cuda())
            c_0 = Variable(torch.zeros(1, self.batch_size, self.hidden_size).cuda())
            input_query = self.dropout(input_query)
            input_doc = self.dropout(input_doc)
        else:
            h_0 = Variable(torch.zeros(1, batch_size, self.hidden_size).cuda())
            c_0 = Variable(torch.zeros(1, batch_size, self.hidden_size).cuda())

        output_query, (final_hidden_state_query, _) = self.lstm(input_query, (h_0, c_0)) # final_hidden_state_query.size() = (1, batch_size, hidden_size) 
        output_query = output_query.permute(1, 0, 2) # output.size() = (batch_size, num_seq, hidden_size)
        embd_query = self.attention_net(output_query, final_hidden_state_query) # embd_query.size = (batch_size, hidden_size)

        output_doc, (final_hidden_state_doc, _) = self.lstm(input_doc, (h_0, c_0)) # final_hidden_state.size() = (1, batch_size, hidden_size) 
        output_doc = output_doc.permute(1, 0, 2) # output.size() = (batch_size, num_seq, hidden_size)
        embd_doc = self.attention_net(output_doc, final_hidden_state_doc) # embd_doc.size = (batch_size, hidden_size)

        return embd_query, embd_doc



# class HierarchicalSiameseNet(torch.nn.Module):
#     def __init__(self, hidden_size, vocab_size, embedding_length, weights, keep_rate, requires_grad=True):
#         super(HierarchicalSiameseNet, self).__init__()
#         self.hidden_size = hidden_size
#         self.vocab_size = vocab_size
#         self.embedding_length = embedding_length

#         self.word_embeddings = nn.Embedding(vocab_size, embedding_length)
#         self.word_embeddings.weights = nn.Parameter(weights, requires_grad=requires_grad)

#         self.word_lstm = nn.LSTM(embedding_length, hidden_size)
#         self.sent_lstm = nn.LSTM(hidden_size, hidden_size)
#         self.dropout = nn.Dropout(1-keep_rate)
        
#     def attention_net(self, lstm_output, final_state):
#         hidden = final_state.squeeze(0)
#         attn_weights = torch.bmm(lstm_output, hidden.unsqueeze(2)).squeeze(2)
#         soft_attn_weights = F.softmax(attn_weights, 1)
#         new_hidden_state = torch.bmm(lstm_output.transpose(1, 2), soft_attn_weights.unsqueeze(2)).squeeze(2)

#         return new_hidden_state

#     def get_sentence_level_embd(self, query, doc):
#         """ 
#         Parameters
#         ----------
#         query: query input_sentence of shape = (num_sentences, sentence_len)
#         doc: doc input_sentence of shape = (num_sentences, sentence_len)
#         num_sentences : number of sentences in a text. default = None. Used only for prediction on a single sentence after training (batch_size = 1)
#         sentence_len : number of tokens in a sentence.

#         Returns
#         -------
#         sequence of hiddent state for query and doc. size=(num_sentences, hidden_size)

#         """

#         input_query = self.word_embeddings(query) # input_query.size=(num_sentences, sentence_len, embedding_length)
#         input_query = input_query.permute(1, 0, 2) # input_query.size=(sentence_len, num_sentences, embedding_length)
#         input_doc = self.word_embeddings(doc) # input_doc.size=(num_sentences, sentence_len, embedding_length)
#         input_doc = input_doc.permute(1, 0, 2) # input_doc.size=(sentence_len, num_sentences, embedding_length)

#         output_query, (final_hidden_state_query, _) = self.word_lstm(input_query) # final_hidden_state_query.size() = (1, num_sentences, hidden_size), output_query.size() = (sentence_len, num_sentences, hidden_size)
#         output_query = output_query.permute(1, 0, 2) # output.size() = (num_sentences, sentence_len, hidden_size)
#         embd_query = self.attention_net(output_query, final_hidden_state_query) # embd_query.size = (num_sentences, hidden_size)

#         output_doc, (final_hidden_state_doc, _) = self.word_lstm(input_doc) # final_hidden_state.size() = (1, num_sentences, hidden_size) 
#         output_doc = output_doc.permute(1, 0, 2) # output.size() = (num_sentences, sentence_len, hidden_size)
#         embd_doc = self.attention_net(output_doc, final_hidden_state_doc) # embd_doc.size = (num_sentences, hidden_size)
#         return embd_query, embd_doc


#     def get_document_embd(self, sent_embd_query, sent_embd_doc):
#         '''
#         args: 
#         sent_embd_query: sequence of hiddent state for query text. size=(batch_size, num_sentences, hidden_size)
#         sent_embd_doc: sequence of hiddent state for doc text. size=(batch_size, num_sentences, hidden_size)
#         '''

#         sent_embd_query = sent_embd_query.permute(1, 0, 2) #sent_embd_query shape = [num_sentences, batch_size, hidden_size]
#         sent_embd_doc = sent_embd_doc.permute(1, 0, 2) #sent_embd_doc shape = [num_sentences, batch_size, hidden_size]
        
#         output_query, (final_hidden_state_query, _) = self.sent_lstm(sent_embd_query) # final_hidden_state_query.size() = (1, batch_size, hidden_size) 
#         output_query = output_query.permute(1, 0, 2) # output.size() = (batch_size, num_sentences, hidden_size)
#         embd_query = self.attention_net(output_query, final_hidden_state_query) # embd_query.size = (batch_size, hidden_size)

#         output_doc, (final_hidden_state_doc, _) = self.sent_lstm(sent_embd_doc) # final_hidden_state.size() = (1, batch_size, hidden_size) 
#         output_doc = output_doc.permute(1, 0, 2) # output.size() = (batch_size, num_sentences, hidden_size)
#         embd_doc = self.attention_net(output_doc, final_hidden_state_doc) # embd_doc.size = (batch_size, hidden_size)
#         return embd_query, embd_doc

#     def forward(self, query_lst, doc_lst, batch_size=None):
#         '''
#         args:
#         query: input query list of size=(batch_size, num_sentences, sentence_len)
#         doc: input query list of size=(batch_size, num_sentences, sentence_len)
#         '''
#         bs = len(query_lst)
#         sent_embd_q, sent_embd_d = [], []

#         for q, d in zip(query_lst, doc_lst):
#             sent_level_embd_q, sent_level_embd_d = self.get_sentence_level_embd(q, d)
#             sent_embd_q.append(sent_level_embd_q)
#             sent_embd_d.append(sent_level_embd_d)

#         Q = torch.cat(sent_embd_q).reshape(bs, -1, self.hidden_size) # (batch_size, num_sentences, hidden_size)
#         D = torch.cat(sent_embd_d).reshape(bs, -1, self.hidden_size) # (batch_size, num_sentences, hidden_size)
#         return self.get_document_embd(Q, D) # (batch_size, hidden_size)





# # class SiameseNet(torch.nn.Module):
# #     def __init__(self, batch_size, hidden_size, vocab_size, embedding_length, weights, keep_rate, requires_grad=None):
# #         super(SiameseNet, self).__init__()
# #         self.batch_size = batch_size
# #         self.hidden_size = hidden_size
# #         self.vocab_size = vocab_size
# #         self.embedding_length = embedding_length

# #         self.word_embeddings = nn.Embedding(vocab_size, embedding_length)
# #         self.word_embeddings.weights = nn.Parameter(weights, requires_grad=requires_grad)

# #         self.lstm_query = nn.LSTM(embedding_length, hidden_size)
# #         self.lstm_doc = nn.LSTM(embedding_length, hidden_size)
# #         self.dropout = nn.Dropout(1-keep_rate)
        
# #     def attention_net(self, lstm_output, final_state):
# #         hidden = final_state.squeeze(0)
# #         attn_weights = torch.bmm(lstm_output, hidden.unsqueeze(2)).squeeze(2)
# #         soft_attn_weights = F.softmax(attn_weights, 1)
# #         new_hidden_state = torch.bmm(lstm_output.transpose(1, 2), soft_attn_weights.unsqueeze(2)).squeeze(2)

# #         return new_hidden_state

# #     def forward(self, query, doc, batch_size=None):
# #         """ 
# #         Parameters
# #         ----------
# #         query: query input_sentence of shape = (batch_size, num_sequences)
# #         doc: doc input_sentence of shape = (batch_size, num_sequences)
# #         batch_size : default = None. Used only for prediction on a single sentence after training (batch_size = 1)

# #         Returns
# #         -------
# #         Output of the linear layer containing logits for pos & neg class which receives its input as the new_hidden_state which is basically the output of the Attention network.
# #         final_output.shape = (batch_size, output_size)

# #         """

# #         input_query = self.word_embeddings(query)
# #         input_query = input_query.permute(1, 0, 2)
# #         input_doc = self.word_embeddings(doc)
# #         input_doc = input_doc.permute(1, 0, 2)
# #         if batch_size is None:
# #             h_0 = Variable(torch.zeros(1, self.batch_size, self.hidden_size).cuda())
# #             c_0 = Variable(torch.zeros(1, self.batch_size, self.hidden_size).cuda())
# #             input_query = self.dropout(input_query)
# #             input_doc = self.dropout(input_doc)
# #         else:
# #             h_0 = Variable(torch.zeros(1, batch_size, self.hidden_size).cuda())
# #             c_0 = Variable(torch.zeros(1, batch_size, self.hidden_size).cuda())

# #         _, (final_hidden_state_query, _) = self.lstm_query(input_query, (h_0, c_0)) # final_hidden_state_query.size() = (1, batch_size, hidden_size) 
# #         embd_query = torch.squeeze(final_hidden_state_query) # embd_query.size() = (batch_size, hidden_size)

# #         output_doc, (final_hidden_state_doc, _) = self.lstm_doc(input_doc, (h_0, c_0)) # final_hidden_state.size() = (1, batch_size, hidden_size) 
# #         output_doc = output_doc.permute(1, 0, 2) # output.size() = (batch_size, num_seq, hidden_size)
# #         embd_doc = self.attention_net(output_doc, final_hidden_state_doc) # embd_doc.size = (batch_size, hidden_size)

# #         return embd_query, embd_doc



# if __name__=='__main__':
#     import os
#     import pickle

#     embd_path = '/share/作文批改/model/word_embd/tencent_small'
#     device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
#     torch.cuda.set_device(0)
#     print('Device is {}'.format(device))

#     w2i = pickle.load(open(os.path.join(embd_path, 'w2i.pkl'),'rb'))
#     embeddings = np.load(os.path.join(embd_path, 'matrix.npy'))
#     word_embeddings = torch.Tensor(embeddings).to(device)
#     vocab_size = word_embeddings.shape[0]
#     embedding_length = word_embeddings.shape[1]
#     hidden_size = 1280
#     keep_rate = 0.9

#     model = HierarchicalSiameseNet(hidden_size, vocab_size, embedding_length, word_embeddings, keep_rate)
#     model.to(device)

#     query = torch.LongTensor([[1,2,3,0,0,0], [1,2,3,0,0,0], [1,2,3,0,0,0], [1,2,3,0,0,0], [0,0,0,0,0,0]]).to(device)
#     doc = torch.LongTensor([[1,2,3,0,0,0], [1,2,3,0,0,0], [1,2,3,0,0,0], [1,2,3,0,0,0], [0,0,0,0,0,0]]).to(device)

#     bs = 32
#     query_lst = [query for _ in range(bs)]
#     doc_lst = [doc for _ in range(bs)]

#     embd_query, embd_doc = model(query_lst, doc_lst)
#     print(embd_query.shape)