# _*_ coding: utf-8 _*_

import torch
import torch.nn as nn
from torch.autograd import Variable
from torch.nn import functional as F


class BiLSTMClassifier(nn.Module):
    def __init__(self, batch_size, output_size, hidden_size, vocab_size, embedding_length, weights, keep_rate=1,
                 biFlag=True, requires_grad=False):
        super(BiLSTMClassifier, self).__init__()

        """
        Arguments
        ---------
        batch_size : Size of the batch which is same as the batch_size of the data returned by the TorchText BucketIterator
        output_size : 2 = (pos, neg)
        hidden_sie : Size of the hidden_state of the LSTM
        vocab_size : Size of the vocabulary containing unique words
        embedding_length : Embeddding dimension of GloVe word embeddings
        weights : Pre-trained GloVe word_embeddings which we will use to create our word_embedding look-up table 
        
        """

        self.batch_size = batch_size
        self.output_size = output_size
        self.hidden_size = hidden_size
        self.vocab_size = vocab_size
        self.embedding_length = embedding_length

        self.word_embeddings = nn.Embedding(vocab_size, embedding_length)  # Initializing the look-up table.
        self.word_embeddings.weight = nn.Parameter(weights,
                                                   requires_grad=requires_grad)  # Assigning the look-up table to the pre-trained GloVe word embedding.
        self.lstm = nn.LSTM(embedding_length, hidden_size, num_layers=1, bidirectional=biFlag, batch_first=False)
        self.label = nn.Linear(hidden_size, output_size)
        # self.layer2 = nn.Sequential(
        #     nn.Linear(hidden_size, 128),
        #     nn.ReLU()
        # )
        # self.label = nn.Linear(128, output_size)
        self.dropout = nn.Dropout(1 - keep_rate)

    def forward(self, input_sentence, batch_size=None):

        """
        Parameters
        ----------
        input_sentence: input_sentence of shape = (batch_size, num_sequences)
        batch_size : default = None. Used only for prediction on a single sentence after training (batch_size = 1)

        Returns
        -------
        Output of the linear layer containing logits for positive & negative class which receives its input as the final_hidden_state of the LSTM
        final_output.shape = (batch_size, output_size)

        """

        ''' Here we will map all the indexes present in the input sequence to the corresponding word vector using our pre-trained word_embedddins.'''
        input = self.word_embeddings(
            input_sentence)  # embedded input of shape = (batch_size, num_sequences,  embedding_length)
        input = input.permute(1, 0, 2)  # input.size() = (num_sequences, batch_size, embedding_length)
        if batch_size is None:
            h_0 = Variable(
                torch.zeros(1 * 2, self.batch_size, self.hidden_size).cuda())  # Initial hidden state of the LSTM
            c_0 = Variable(
                torch.zeros(1 * 2, self.batch_size, self.hidden_size).cuda())  # Initial cell state of the LSTM
            input = self.dropout(input)
        else:
            h_0 = Variable(torch.zeros(1 * 2, batch_size, self.hidden_size).cuda())
            c_0 = Variable(torch.zeros(1 * 2, batch_size, self.hidden_size).cuda())
        output, (final_hidden_state, final_cell_state) = self.lstm(input, (h_0, c_0))

        if batch_size is None:
            final_hidden_state = self.dropout(final_hidden_state)

        # hidden_2_out = self.layer2(output.contiguous().view(-1, 2*self.hidden_size))  # bs,seq_len,2*hs  --> bs,seq_len,512
        # hidden_2_out = self.layer2(output[-1])
        # final_output = self.label(hidden_2_out)
        final_output = self.label(final_hidden_state[-1])  # final_hidden_state.size() = (1, batch_size, hidden_size) & final_output.size() = (batch_size, output_size)

        return final_output


# 定义常量
INPUT_SIZE = 28  # 定义输入的特征数
HIDDEN_SIZE = 32  # 定义一个LSTM单元有多少个神经元
BATCH_SIZE = 32  # batch
EPOCH = 10  # 学习次数
LR = 0.001  # 学习率
TIME_STEP = 28  # 步长，一般用不上，写出来就是给自己看的
DROP_RATE = 0.2  # drop out概率
LAYERS = 2  # 有多少隐层，一个隐层一般放一个LSTM单元
MODEL = 'LSTM'  # 模型名字


class TestLSTM(nn.Module):
    def __init__(self):
        super(TestLSTM, self).__init__()

        self.lstm = nn.LSTM(
            input_size=INPUT_SIZE,
            hidden_size=HIDDEN_SIZE,
            num_layers=LAYERS,
            dropout=DROP_RATE,
            batch_first=True
        )
        self.hidden_out = nn.Linear(HIDDEN_SIZE, 10)
        # self.h_s = None
        # self.h_c = None

    def forward(self, x):
        h_0 = Variable(torch.zeros(2 * 2, BATCH_SIZE, self.hidden_size))
        c_0 = Variable(torch.zeros(2 * 2, BATCH_SIZE, self.hidden_size))
        r_out, (h_s, h_c) = self.lstm(x, (h_0, c_0))
        output = self.hidden_out(r_out)
        return output


if __name__ == '__main__':
    """
    简单测试lstm模型构建的正确性
    """
    # model = LSTMClassifier(5, 2, 20, )
    input = torch.randn(5, 3, 10)
