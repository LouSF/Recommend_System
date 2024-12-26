import torch
import torch.nn.functional as F
import math
import recommendModel.config as config

from torch import Tensor, nn

import logging

logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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

class Dot_Attention(nn.Module):
    def __init__(self, Esize :int):
        super().__init__()

        self.Esize = Esize

        self.w_q = nn.Linear(Esize, Esize)
        self.w_k = nn.Linear(Esize, Esize)
        self.w_v = nn.Linear(Esize, Esize)

    def forward(self,
                q :Tensor,
                k :Tensor,
                v :Tensor,
                mask :Tensor = None) -> (Tensor, Tensor):

        q = self.w_q(q)
        k = self.w_q(k)
        v = self.w_q(v)

        return Scaled_Dot(q, k, v, mask)
