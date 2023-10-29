import math
import torch
import torch.nn as nn
import torch.nn.functional as F


# Temporarily leave PositionalEncoding module here. Will be moved somewhere else.
class PositionalEncoding(nn.Module):
    r"""Inject some information about the relative or absolute position of the tokens
        in the sequence. The positional encodings have the same dimension as
        the embeddings, so that the two can be summed. Here, we use sine and cosine
        functions of different frequencies.
    .. math::
        \text{PosEncoder}(pos, 2i) = sin(pos/10000^(2i/d_model))
        \text{PosEncoder}(pos, 2i+1) = cos(pos/10000^(2i/d_model))
        \text{where pos is the word position and i is the embed idx)
    Args:
        d_model: the embed dim (required).
        dropout: the dropout value (default=0.1).
        max_len: the max. length of the incoming sequence (default=5000).
    Examples:
        >>> pos_encoder = PositionalEncoding(d_model)
    """

    def __init__(self, d_model, dropout=0.1, max_len=5000):
        super(PositionalEncoding, self).__init__()
        self.dropout = nn.Dropout(p=dropout)

        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0).transpose(0, 1)
        self.register_buffer('pe', pe)

    def forward(self, x):
        r"""Inputs of forward function
        Args:
            x: the sequence fed to the positional encoder model (required).
        Shape:
            x: [sequence length, batch size, embed dim]
            output: [sequence length, batch size, embed dim]
        Examples:
            >>> output = pos_encoder(x)
        """

        x = x + self.pe[:x.size(0), :]
        return self.dropout(x)


# class TransformerModel(nn.Module):
#     """Container module with an encoder, a recurrent or transformer module, and a decoder."""
#     def __init__(self, batch_size, max_time_step, output_size, \
#                 d_model, nhead, dim_feedforward, nlayers, weights, keep_rate, requires_grad=False):
#         super(TransformerModel, self).__init__()
#         try:
#             from torch.nn import TransformerEncoder, TransformerEncoderLayer
#         except:
#             raise ImportError('TransformerEncoder module does not exist in PyTorch 1.1 or lower.')
#         self.model_type = 'Transformer'
#         self.src_mask = None
#         self.droprate = 1- keep_rate
#         self.batch_size = batch_size
#         self.d_model = d_model

#         vocab_size = weights.shape[0]
#         embedding_length = weights.shape[1]
#         self.embedding_length = embedding_length
#         self.word_embeddings = nn.Embedding(vocab_size, embedding_length)# Initializing the look-up table.
#         self.word_embeddings.weight = nn.Parameter(weights, requires_grad=requires_grad) # Assigning the look-up table to the pre-trained GloVe word embedding.

#         if(embedding_length!=d_model):
#             self.embedding_projector = nn.Linear(embedding_length, d_model, bias=False)
#         else:
#             self.embedding_projector = None

#         self.pos_encoder = PositionalEncoding(d_model, self.droprate)
#         encoder_layers = TransformerEncoderLayer(d_model, nhead, dim_feedforward, self.droprate)
#         self.transformer_encoder = TransformerEncoder(encoder_layers, nlayers)
        
#         self.weighted_sum_layer = nn.Linear(max_time_step, 1, bias=False)
#         self.linear = nn.Linear(d_model, output_size)
        
#         self.init_weights()

#     def generate_square_subsequent_mask(self, sz):
#         mask = (torch.triu(torch.ones(sz, sz)) == 1).transpose(0, 1)
#         mask = mask.float().masked_fill(mask == 0, float('-inf')).masked_fill(mask == 1, float(0.0))
#         return mask

#     def generate_src_key_padding_mask(self, src):
#         '''
#         args:
#         src shape: batch_size, max_time_step
#         returns:
#         boolean padding mask of shape: batch_size, max_time_step
#         where True values are posititions taht should be masked with -inf
#         and False values will be unchanged.
#         '''
#         return src==0

#     def init_weights(self):
#         initrange = 0.1
#         if(self.embedding_projector is not None):
#             self.embedding_projector.weight.data.uniform_(-initrange, initrange)
#         self.weighted_sum_layer.weight.data.uniform_(-initrange, initrange)
#         self.linear.bias.data.zero_()
#         self.linear.weight.data.uniform_(-initrange, initrange)

#     def forward(self, src, batch_size=None, has_mask=True):
#         '''
#         Args:
#         src: input sequence of shape: batch_size, max_time_step

#         Returns:
#         final_output of shape: batch_size, output_size
#         '''
#         if(has_mask):
#             device = src.device
#             if self.src_mask is None or self.src_mask.size(0) != len(src):
#                 mask = self.generate_src_key_padding_mask(src)
#                 self.src_mask = mask
#         else:
#             self.src_mask = None

#         src = self.word_embeddings(src) * math.sqrt(self.embedding_length) #  batch_size, max_time_setp, embedding_length
    
#         if(self.embedding_projector is not None): # solve embedding_length and d_model dimension mismatch
#             src = self.embedding_projector(src) # batch_size, max_time_step, d_model
        
#         src = src.permute(1, 0, 2) # max_time_setp, batch_size, d_model
#         src = self.pos_encoder(src) # max_time_setp, batch_size, d_model

#         output = self.transformer_encoder(src, src_key_padding_mask=self.src_mask) # max_time_step, batch_size, d_model


#         # compute weighted sum of hidden states over each time_step
#         output = torch.transpose(output, 0, 1) # batch_size, max_time_step, d_model
#         output = torch.transpose(output, 1, 2) # batch_size, d_model, max_time_step
#         final_hidden = self.weighted_sum_layer(output).view(-1, self.d_model) # batch_size, d_model
        
#         final_output = self.linear(final_hidden) # batch_size, output_size
#         return final_output



class TransformerModel(nn.Module):
    """Container module with an encoder, a recurrent or transformer module, and a decoder."""
    def __init__(self, batch_size, max_time_step, output_size, \
                d_model, nhead, dim_feedforward, nlayers, weights, keep_rate, use_cls_token=False, requires_grad=False):
        super(TransformerModel, self).__init__()
        try:
            from torch.nn import TransformerEncoder, TransformerEncoderLayer
        except:
            raise ImportError('TransformerEncoder module does not exist in PyTorch 1.1 or lower.')
        self.model_type = 'Transformer'
        self.src_mask = None
        self.droprate = 1- keep_rate
        self.batch_size = batch_size
        self.d_model = d_model
        self.use_cls_token = use_cls_token

        vocab_size = weights.shape[0]
        embedding_length = weights.shape[1]
        self.embedding_length = embedding_length
        self.word_embeddings = nn.Embedding(vocab_size, embedding_length)# Initializing the look-up table.
        self.word_embeddings.weight = nn.Parameter(weights, requires_grad=requires_grad) # Assigning the look-up table to the pre-trained GloVe word embedding.

        if(embedding_length!=d_model):
            self.embedding_projector = nn.Linear(embedding_length, d_model, bias=False)
        else:
            self.embedding_projector = None

        self.pos_encoder = PositionalEncoding(d_model, self.droprate)
        encoder_layers = TransformerEncoderLayer(d_model, nhead, dim_feedforward, self.droprate)
        self.transformer_encoder = TransformerEncoder(encoder_layers, nlayers)
        
        if(use_cls_token==True):
            print('Enable CLS token for classification... ')
            self.cls_token_vector = torch.empty(embedding_length).uniform_(-0.1, 0.1)
        else:
            print('Enable weighted sum hidden states for classification...')
            self.weighted_sum_layer = nn.Linear(max_time_step, 1, bias=False)
        self.linear = nn.Linear(d_model, output_size)
        
        self.init_weights()

    def generate_square_subsequent_mask(self, sz):
        mask = (torch.triu(torch.ones(sz, sz)) == 1).transpose(0, 1)
        mask = mask.float().masked_fill(mask == 0, float('-inf')).masked_fill(mask == 1, float(0.0))
        return mask

    def generate_src_key_padding_mask(self, src):
        '''
        args:
        src shape: batch_size, max_time_step
        returns:
        boolean padding mask of shape: batch_size, max_time_step
        where True values are posititions taht should be masked with -inf
        and False values will be unchanged.
        '''
        return src==0

    def init_weights(self):
        initrange = 0.1
        if(self.embedding_projector is not None):
            self.embedding_projector.weight.data.uniform_(-initrange, initrange)
        if(not self.use_cls_token):
            self.weighted_sum_layer.weight.data.uniform_(-initrange, initrange)
        self.linear.bias.data.zero_()
        self.linear.weight.data.uniform_(-initrange, initrange)

    def forward(self, src, batch_size=None, has_mask=True):
        '''
        Args:
        src: input sequence of shape: batch_size, max_time_step

        Returns:
        final_output of shape: batch_size, output_size
        '''
        if(has_mask):
            device = src.device
            if self.src_mask is None or self.src_mask.size(0) != len(src):
                mask = self.generate_src_key_padding_mask(src)
                self.src_mask = mask
        else:
            self.src_mask = None

        if(self.use_cls_token==True):
            src = src[:, :-1] # batch_size, max_time_step-1
            cls_vector_repeat = self.cls_token_vector.repeat(src.shape[0], 1, 1).to(src.device) 
            src = torch.cat((cls_vector_repeat, self.word_embeddings(src)), dim=1) # append cls token vector at the front
            src *= math.sqrt(self.embedding_length)
        else:
            src = self.word_embeddings(src) * math.sqrt(self.embedding_length) #  batch_size, max_time_setp, embedding_length
            

        if(self.embedding_projector is not None): # solve embedding_length and d_model dimension mismatch
            src = self.embedding_projector(src) # batch_size, max_time_step, d_model
        
        src = src.permute(1, 0, 2) # max_time_setp, batch_size, d_model
        src = self.pos_encoder(src) # max_time_setp, batch_size, d_model

        output = self.transformer_encoder(src, src_key_padding_mask=self.src_mask) # max_time_step, batch_size, d_model

        if(self.use_cls_token): # use cls hidden state for classification
            final_hidden = output[0, :, :].view(-1, self.d_model) # batch_size, d_model
        else:
            # compute weighted sum of hidden states over each time_step
            output = torch.transpose(output, 0, 1) # batch_size, max_time_step, d_model
            output = torch.transpose(output, 1, 2) # batch_size, d_model, max_time_step
            final_hidden = self.weighted_sum_layer(output).view(-1, self.d_model) # batch_size, d_model
        
        final_output = self.linear(final_hidden) # batch_size, output_size

        return final_output