import os
import time
import pickle
import torch
import torch.nn.functional as F
from torch.autograd import Variable
import torch.optim as optim
import numpy as np

from model.LSTM import LSTMClassifier
from model.CNN import CNN
from model.LSTM_Attn import AttentionModel
from model.selfAttention import SelfAttention
from model.RCNN import RCNN
from model.transformer import TransformerModel
from model.bert import BertForTextClassification
from classify_utils import *


def clip_gradient(model, clip_value):
    params = list(filter(lambda p: p.grad is not None, model.parameters()))
    for p in params:
        p.grad.data.clamp_(-clip_value, clip_value)
    
def train_model(model, learning_rate, loss_fn, train_data, batch_size, device, sampling=None):
    total_epoch_loss = 0
    total_epoch_acc = 0
    model.to(device)
    optim = torch.optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=learning_rate)
    train_size = len(train_data)
    num_steps = int(train_size//batch_size)
    model.train()
    for step in range(num_steps):
        optim.zero_grad()
        inp, target = get_batch(train_data, batch_size, device, sampling)

        prediction = model(inp)
        loss = loss_fn(prediction, target)
        num_corrects = (torch.max(prediction, 1)[1].view(target.size()).data == target.data).float().sum()
        acc = 100.0 * num_corrects/batch_size
        loss.backward()
        clip_gradient(model, 1e-1)
        optim.step()

        total_epoch_loss += loss.item()
        total_epoch_acc += acc.item()
        
    return total_epoch_loss/num_steps, total_epoch_acc/num_steps


def eval_model(model, loss_fn, valid_data, batch_size, device):
    total_epoch_loss = 0
    total_epoch_acc = 0
    model.eval()

    valid_size = len(valid_data)
    num_steps = int(valid_size//batch_size)
    with torch.no_grad():
        for step in range(num_steps):
            inp, target = get_batch_valid(valid_data, batch_size, device, step)
            prediction = model(inp, batch_size)
            loss = loss_fn(prediction, target)
            num_corrects = (torch.max(prediction, 1)[1].view(target.size()).data == target.data).sum()
            acc = 100.0 * num_corrects/batch_size
            total_epoch_loss += loss.item()
            total_epoch_acc += acc.item()

    return total_epoch_loss/num_steps, total_epoch_acc/num_steps
	

def inference(model, test_data, device):
    y_hat_lst, y_truth_lst = [], []
    N = len(test_data)
    for step in range(N):
        inp, target = get_batch_valid(test_data, 1, device, step)
        prediction = model(inp, batch_size=1)
        y_hat = torch.argmax(prediction).cpu().detach().numpy()
        y_hat_lst.append(y_hat)
        y_truth_lst.append(target.cpu().detach().numpy()[0])

    acc, prec, rec, f1, f05 = metrics(y_truth_lst, y_hat_lst)
    print('Test accuracy {}, precision {}, recall {}, F1 {}, F0.5 {}'.format(acc, prec, rec, f1, f05))
    print('-'*66)
    print()
    return y_hat_lst, acc, prec, rec, f1, f05



def train_helper(model, learning_rate, loss_fn, train_data, valid_data, batch_size, \
                    device, max_iters, best_model_save_path, model_prefix, max_early_stop_counts=10, sampling=None):
    best_loss = 1e9
    best_model = model
    early_stop_count = 0

    for epoch in range(max_iters):
        if(early_stop_count> max_early_stop_counts):
            print('Early stop at epoch {}.'.format(epoch))
            break

        train_loss, train_acc = train_model(model, learning_rate, loss_fn, train_data, batch_size, device, sampling)
        val_loss, val_acc = eval_model(model, loss_fn, valid_data, batch_size, device)
        print('Epoch {}, train loss {}, train acc {}, val loss {}, val acc {}'.format(epoch+1, round(train_loss, 5), round(train_acc, 5), round(val_loss, 5), round(val_acc, 5)))
        if(val_loss<best_loss):
            early_stop_count = 0
            best_loss = val_loss
            best_model = model

            if(not os.path.exists(best_model_save_path)):
                os.makedirs(best_model_save_path)
            with open(os.path.join(best_model_save_path, '{}.pt'.format(model_prefix)), 'wb') as f:
                torch.save(best_model, f)
        else:
            early_stop_count += 1
    print('Training completed...')
    print('-'*66)
    return best_model



def train_eval_cnn(data_path, embd_path, best_model_save_path, max_seq_len=60, max_iters=200, sampling=None):
    output_size = 2
    in_channels = 1
    kernel_heights = [2, 3, 5]
    stride = 1
    padding = 0
    
    w2i, embeddings, train_data, valid_data, test_data = load_all_data(data_path, embd_path, max_seq_len)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    word_embeddings = torch.Tensor(embeddings).to(device)
    vocab_size = embeddings.shape[0]
    embedding_length = embeddings.shape[1]

    learning_rate_lst = [1e-3, 5e-4, 1e-4]
    batch_size_lst = [32, 64, 128, 256]
    out_channels_lst = [10, 30, 50, 100]
    keep_probab_lst = [0.5, 0.7, 0.9, 1.0]
    
    if(not os.path.exists(best_model_save_path)):
        os.makedirs(best_model_save_path)

    for learning_rate in learning_rate_lst:
        for batch_size in batch_size_lst:
            for out_channels in out_channels_lst:
                for keep_probab in keep_probab_lst:
                    done_lst = [x for x in os.listdir(best_model_save_path) if '.pt' in x]
                    model_prefix = 'cnn_{}_{}_{}_{}'.format(learning_rate, batch_size, out_channels, keep_probab)
                    if(model_prefix+'.pt' in done_lst):
                        print('Pass model {}'.format(model_prefix))
                        continue
                    
                    print('training model {}'.format(model_prefix))
                    model = CNN(batch_size, output_size, in_channels, out_channels, kernel_heights, \
                                            stride, padding, vocab_size, embedding_length, word_embeddings, keep_probab)
                    loss_fn = F.cross_entropy
                    best_model = train_helper(model, learning_rate, loss_fn, train_data, valid_data, \
                                    batch_size, device, max_iters, best_model_save_path, model_prefix, sampling=sampling)
                    
                    _, acc, prec, rec, f1, f05 = inference(best_model, test_data, device)


def train_eval_rcnn(data_path, embd_path, best_model_save_path, max_seq_len=60, max_iters=200, sampling=None):
    output_size = 2
   
    w2i, embeddings, train_data, valid_data, test_data = load_all_data(data_path, embd_path, max_seq_len)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    word_embeddings = torch.Tensor(embeddings).to(device)
    vocab_size = word_embeddings.shape[0]
    embedding_length = word_embeddings.shape[1]
    
    learning_rate_lst = [1e-3, 5e-4, 1e-4]
    batch_size_lst = [32, 64, 128, 256]
    hidden_size_lst = [64, 128, 256, 512]
    keep_probab_lst = [0.5, 0.7, 0.9, 1.0]
    
    if(not os.path.exists(best_model_save_path)):
        os.makedirs(best_model_save_path)

    for learning_rate in learning_rate_lst:
        for batch_size in batch_size_lst:
            for hidden_size in hidden_size_lst:
                for keep_rate in keep_probab_lst:
                    done_lst = [x for x in os.listdir(best_model_save_path) if '.pt' in x]
                    model_prefix = 'rcnn_{}_{}_{}_{}'.format(learning_rate, batch_size, hidden_size, keep_rate)
                    if(model_prefix+'.pt' in done_lst):
                        print('Pass model {}'.format(model_prefix))
                        continue

                    print('training model {}'.format(model_prefix))
                    model = RCNN(batch_size, output_size, hidden_size, vocab_size, embedding_length, word_embeddings, keep_rate)
                    loss_fn = F.cross_entropy
                    
                    best_model = train_helper(model, learning_rate, loss_fn, train_data, valid_data, batch_size, \
                                                            device, max_iters, best_model_save_path, model_prefix, sampling=sampling)
                    _, acc, prec, rec, f1, f05 = inference(best_model, test_data, device)


def train_eval_lstm(data_path, embd_path, best_model_save_path, max_seq_len=60, max_iters=200, sampling=None):
    output_size = 2

    w2i, embeddings, train_data, valid_data, test_data = load_all_data(data_path, embd_path, max_seq_len)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    word_embeddings = torch.Tensor(embeddings).to(device)
    vocab_size = word_embeddings.shape[0]
    embedding_length = word_embeddings.shape[1]

    learning_rate_lst = [1e-3, 5e-4, 1e-4]
    batch_size_lst = [32, 64, 128, 256]
    hidden_size_lst = [64, 128, 256, 512]
    keep_rate_lst = [0.5, 0.7, 0.9, 1.0]
    
    if(not os.path.exists(best_model_save_path)):
        os.makedirs(best_model_save_path)

    for learning_rate in learning_rate_lst:
        for batch_size in batch_size_lst:
            for hidden_size in hidden_size_lst:
                for keep_rate in keep_rate_lst:
                    done_lst = [x for x in os.listdir(best_model_save_path) if '.pt' in x]
                    model_prefix = 'lstm_{}_{}_{}_{}'.format(learning_rate, batch_size, hidden_size, keep_rate)
                    if(model_prefix+'.pt' in done_lst):
                        print('Pass model {}'.format(model_prefix))
                        continue

                    print('training model {}'.format(model_prefix))
                    model = LSTMClassifier(batch_size, output_size, hidden_size, vocab_size, embedding_length, word_embeddings, keep_rate)
                    loss_fn = F.cross_entropy
                    
                    best_model = train_helper(model, learning_rate, loss_fn, train_data, valid_data, \
                                            batch_size, device, max_iters, best_model_save_path, model_prefix, sampling=sampling)
                    _, acc, prec, rec, f1, f05 = inference(best_model, test_data, device)



def train_eval_selfAttn(data_path, embd_path, best_model_save_path, max_seq_len=60, max_iters=200, sampling=None):
    output_size = 2
    
    w2i, embeddings, train_data, valid_data, test_data = load_all_data(data_path, embd_path, max_seq_len)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    word_embeddings = torch.Tensor(embeddings).to(device)
    vocab_size = word_embeddings.shape[0]
    embedding_length = word_embeddings.shape[1]

    learning_rate_lst = [1e-3, 5e-4, 1e-4]
    batch_size_lst = [32, 64, 128, 256]
    hidden_size_lst = [64, 128, 256, 512]
    keep_rate_lst = [0.5, 0.7, 0.9, 1.0]
    
    if(not os.path.exists(best_model_save_path)):
        os.makedirs(best_model_save_path)

    for learning_rate in learning_rate_lst:
        for batch_size in batch_size_lst:
            for hidden_size in hidden_size_lst:
                for keep_rate in keep_rate_lst:
                    done_lst = [x for x in os.listdir(best_model_save_path) if '.pt' in x]
                    model_prefix = 'selfAttention_{}_{}_{}_{}'.format(learning_rate, batch_size, hidden_size, keep_rate)
                    if(model_prefix+'.pt' in done_lst):
                        print('Pass model {}'.format(model_prefix))
                        continue
                    print('training mode {}'.format(model_prefix))
                    model = SelfAttention(batch_size, output_size, hidden_size, vocab_size, embedding_length, word_embeddings, keep_rate)
                    loss_fn = F.cross_entropy
                    
                    best_model = train_helper(model, learning_rate, loss_fn, train_data, valid_data, \
                                                batch_size, device, max_iters, best_model_save_path, model_prefix, sampling=sampling)
                    _, acc, prec, rec, f1, f05 = inference(best_model, test_data, device)


def train_eval_lstm_attn(data_path, embd_path, best_model_save_path, max_seq_len=60, max_iters=200, sampling=None):
    output_size = 2
    
    w2i, embeddings, train_data, valid_data, test_data = load_all_data(data_path, embd_path, max_seq_len)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    word_embeddings = torch.Tensor(embeddings).to(device)
    vocab_size = word_embeddings.shape[0]
    embedding_length = word_embeddings.shape[1]

    learning_rate_lst = [1e-3, 5e-4, 1e-4]
    batch_size_lst = [32, 64, 128, 256]
    hidden_size_lst = [64, 128, 256, 512]
    keep_rate_lst = [0.5, 0.7, 0.9, 1.0]
    
    if(not os.path.exists(best_model_save_path)):
        os.makedirs(best_model_save_path)

    for learning_rate in learning_rate_lst:
        for batch_size in batch_size_lst:
            for hidden_size in hidden_size_lst:
                for keep_rate in keep_rate_lst:
                    done_lst = [x for x in os.listdir(best_model_save_path) if '.pt' in x]
                    model_prefix = 'lstmAttn_{}_{}_{}_{}'.format(learning_rate, batch_size, hidden_size, keep_rate)
                    if(model_prefix+'.pt' in done_lst):
                        print('Pass model {}'.format(model_prefix))
                        continue

                    print('training mode {}'.format(model_prefix))
                    model = AttentionModel(batch_size, output_size, hidden_size, vocab_size, embedding_length, word_embeddings, keep_rate)
                    loss_fn = F.cross_entropy
                    
                    best_model = train_helper(model, learning_rate, loss_fn, train_data, valid_data, \
                                            batch_size, device, max_iters, best_model_save_path, model_prefix, sampling=sampling)
                    _, acc, prec, rec, f1, f05 = inference(best_model, test_data, device)


# def train_eval_transformer(data_path, embd_path, best_model_save_path, max_seq_len=60, max_iters=200, sampling=None):
#     output_size = 2
#     w2i, embeddings, train_data, valid_data, test_data = load_all_data(data_path, embd_path, max_seq_len)
#     device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
#     word_embeddings = torch.Tensor(embeddings).to(device)


#     learning_rate_lst = [1e-5, 5e-5]
#     batch_size_lst = [128]
#     d_model_lst = [64, 128, 256, 512]
#     nhead_lst = [2, 4, 8]
#     nlayers_lst = [2, 4, 6]
#     keep_rate_lst = [0.9]
#     requires_grad_lst = [False, True]
    
#     if(not os.path.exists(best_model_save_path)):
#         os.makedirs(best_model_save_path)

#     for learning_rate in learning_rate_lst:
#         for batch_size in batch_size_lst:
#             for d_model in d_model_lst:
#                 for nhead in nhead_lst:
#                     for nlayers in nlayers_lst:
#                         for keep_rate in keep_rate_lst:
#                             for requires_grad in requires_grad_lst:
#                                 dim_feedforward = 2*d_model
#                                 done_lst = [x for x in os.listdir(best_model_save_path) if '.pt' in x]
#                                 model_prefix = 'transformer_{}_{}_{}_{}_{}_{}_{}_w2vGrad={}'.format(learning_rate, batch_size, d_model, \
#                                                                         nhead, dim_feedforward, nlayers, keep_rate, requires_grad)
#                                 if(model_prefix+'.pt' in done_lst):
#                                     print('Pass model {}'.format(model_prefix))
#                                     continue

#                                 print('training mode {}'.format(model_prefix))
#                                 model = TransformerModel(batch_size, max_seq_len, output_size, d_model, \
#                                             nhead, dim_feedforward, nlayers, word_embeddings, keep_rate, requires_grad=requires_grad)
                                
#                                 loss_fn = F.cross_entropy
                                
#                                 best_model = train_helper(model, learning_rate, loss_fn, train_data, valid_data, \
#                                                         batch_size, device, max_iters, best_model_save_path, model_prefix, sampling=sampling)
#                                 _, acc, prec, rec, f1, f05 = inference(best_model, test_data, device)


def train_eval_transformer(data_path, embd_path, best_model_save_path, max_seq_len=60, max_iters=200, sampling=None):
    output_size = 2
    w2i, embeddings, train_data, valid_data, test_data = load_all_data(data_path, embd_path, max_seq_len)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    word_embeddings = torch.Tensor(embeddings).to(device)


    learning_rate_lst = [1e-5, 5e-5]
    batch_size_lst = [512]
    d_model_lst = [64, 128, 256, 512]
    nhead_lst = [2, 4, 8]
    nlayers_lst = [2, 4, 6]
    keep_rate_lst = [0.9]
    use_cls_token_lst = [True, False]
    requires_grad_lst = [False, True]
    
    if(not os.path.exists(best_model_save_path)):
        os.makedirs(best_model_save_path)

    for learning_rate in learning_rate_lst:
        for batch_size in batch_size_lst:
            for d_model in d_model_lst:
                for nhead in nhead_lst:
                    for nlayers in nlayers_lst:
                        for keep_rate in keep_rate_lst:
                            for use_cls_token in use_cls_token_lst:
                                for requires_grad in requires_grad_lst:
                                    dim_feedforward = 2*d_model
                                    done_lst = [x for x in os.listdir(best_model_save_path) if '.pt' in x]
                                    model_prefix = 'transformer_{}_{}_{}_{}_{}_{}_{}_useCLS={}_w2vGrad={}'.format(learning_rate, batch_size, d_model, \
                                                                            nhead, dim_feedforward, nlayers, keep_rate, use_cls_token, requires_grad)
                                    if(model_prefix+'.pt' in done_lst):
                                        print('Pass model {}'.format(model_prefix))
                                        continue

                                    print('training mode {}'.format(model_prefix))
                                    model = TransformerModel(batch_size, max_seq_len, output_size, d_model, \
                                                nhead, dim_feedforward, nlayers, word_embeddings, keep_rate, use_cls_token=use_cls_token, requires_grad=requires_grad)
                                    
                                    loss_fn = F.cross_entropy
                                    
                                    best_model = train_helper(model, learning_rate, loss_fn, train_data, valid_data, \
                                                            batch_size, device, max_iters, best_model_save_path, model_prefix, sampling=sampling)
                                    _, acc, prec, rec, f1, f05 = inference(best_model, test_data, device)


def train_eval_bert_usePretrained(pretrained_model_path, data_path, best_model_save_path, max_seq_len=60, max_iters=200):
    output_size = 2
    train_data, valid_data, test_data = load_all_data(data_path, None, max_seq_len, pretrained_model_path)[-3:]
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    if(not os.path.exists(best_model_save_path)):
        os.makedirs(best_model_save_path)
    
    learning_rate_lst = [1e-5, 5e-5]
    batch_size_lst = [8, 16, 64, 128]
    sampling_lst = [None, 0.1, 0.2, 0.3, 0.4, 0.5]
    
    if(not os.path.exists(best_model_save_path)):
        os.makedirs(best_model_save_path)

    for learning_rate in learning_rate_lst:
        for batch_size in batch_size_lst:
            for sampling in sampling_lst:
                try:
                    done_lst = [x for x in os.listdir(best_model_save_path) if '.pt' in x]
                    model_prefix = 'PretrainedBert_{}_{}_{}'.format(learning_rate, batch_size, sampling)

                    if(model_prefix+'.pt' in done_lst):
                        print('Pass model {}'.format(model_prefix))
                    else:
                        print('training mode {}'.format(model_prefix))
                        model = BertForTextClassification(pretrained_model_path, output_size, None, None, None, \
                                None, None, None, None, None, use_pretrained_model=True)
                        
                        loss_fn = F.cross_entropy
                        
                        best_model = train_helper(model, learning_rate, loss_fn, train_data, valid_data, \
                                                batch_size, device, max_iters, best_model_save_path, model_prefix, max_early_stop_counts=4, sampling=sampling)
                        _, acc, prec, rec, f1, f05 = inference(best_model, test_data, device)
                except:
                    print('Memory not enough, unable to train {}'.format(model_prefix))


def train_eval_bert(pretrained_model_path, data_path, best_model_save_path, max_seq_len=60, max_iters=200):
    output_size = 2
    train_data, valid_data, test_data = load_all_data(data_path, None, max_seq_len, pretrained_model_path)[-3:]
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    if(not os.path.exists(best_model_save_path)):
        os.makedirs(best_model_save_path)
    
    learning_rate_lst = [1e-5, 5e-5]
    hidden_size_lst = [128, 256, 512]
    num_hidden_layers_lst = [2, 4]
    num_attention_heads_lst = [4, 8]
    intermediate_size_lst = [256, 512]
    hidden_dropout_prob_lst = [0.1, 0.2]
    attention_probs_dropout_prob_lst = [0.1]
    batch_size_lst = [512]
    
    if(not os.path.exists(best_model_save_path)):
        os.makedirs(best_model_save_path)

    for learning_rate in learning_rate_lst:
        for hidden_size in hidden_size_lst:
            for num_hidden_layers in num_hidden_layers_lst:
                for num_attention_heads in num_attention_heads_lst:
                    for intermediate_size in intermediate_size_lst:
                        for hidden_dropout_prob in hidden_dropout_prob_lst:
                            for attention_probs_dropout_prob in attention_probs_dropout_prob_lst:   
                                for batch_size in batch_size_lst:
                                    try:
                                        done_lst = [x for x in os.listdir(best_model_save_path) if '.pt' in x]
                                        model_prefix = 'Bert_{}_{}_{}_{}_{}_{}_{}_{}'.format(learning_rate, hidden_size, num_hidden_layers, num_attention_heads, \
                                            intermediate_size, hidden_dropout_prob, attention_probs_dropout_prob, batch_size)

                                        if(model_prefix+'.pt' in done_lst):
                                            print('Pass model {}'.format(model_prefix))
                                        else:
                                            print('training mode {}'.format(model_prefix))
                                            model = BertForTextClassification(pretrained_model_path, output_size, hidden_size, num_hidden_layers, num_attention_heads, \
                                                    intermediate_size, 'gelu', hidden_dropout_prob, attention_probs_dropout_prob, max_position_embeddings=512, use_pretrained_model=False)
                                            
                                            loss_fn = F.cross_entropy
                                            
                                            best_model = train_helper(model, learning_rate, loss_fn, train_data, valid_data, \
                                                                    batch_size, device, max_iters, best_model_save_path, model_prefix, max_early_stop_counts=4, sampling=sampling)
                                            _, acc, prec, rec, f1, f05 = inference(best_model, test_data, device)
                                    except:
                                        print('Memory not enough, unable to train {}'.format(model_prefix))


if __name__ == "__main__":
    data_path = '/share/作文批改/data/描写/心里描写/v02'
    embd_path = '/share/作文批改/model/word_embd/tencent_small'
    best_model_save_path = '/workspace/Guowei/essay_grading/src/text_classification/tmp'

    #this_model_save_path = os.path.join(best_model_save_path, 'transformer')
    #train_eval_transformer(data_path, embd_path, this_model_save_path, max_seq_len=80, max_iters=200, sampling=None)
    
    
    pretrained_model_path = '/share/作文批改/model/bert/chinese_wwm_ext_pytorch'
    #this_model_save_path = os.path.join(best_model_save_path, 'bert')
    #train_eval_bert(pretrained_model_path, data_path, this_model_save_path, max_seq_len=80, max_iters=200, sampling=None)

    this_model_save_path = os.path.join(best_model_save_path, 'pretrained_bert')
    train_eval_bert_usePretrained(pretrained_model_path, data_path, this_model_save_path, max_seq_len=80, max_iters=200, sampling=None)