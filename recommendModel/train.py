import torch
import torch.nn.functional as F
import math

from torch import Tensor, nn

def Scaled_Dot(Q :Tensor,
               K :Tensor,
               V :Tensor,
               mask :Tensor = None) -> (Tensor, Tensor):

    Esize = Q.size(-1)

    scores = torch.matmul(Q, K.transpose(-2, -1)) / math.sqrt(Esize)

    if mask is not None:
        scores = scores.masked_fill(mask == 0, float('-inf'))

    attention_weights = F.softmax(scores, dim=-1)

    result = torch.matmul(attention_weights, V)

    return result, attention_weights

def