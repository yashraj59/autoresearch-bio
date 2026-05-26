from __future__ import annotations

import argparse
import json
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader, TensorDataset


__version__ = "1.1.0"


class MoFNetLayer(nn.Module):
    """Masked linear layer used by transparent MoFNet blocks."""

    def __init__(self, in_dims: int, out_dims: int, bias: bool = True):
        super().__init__()
        self.in_dims = int(in_dims)
        self.out_dims = int(out_dims)
        self.weight = nn.Parameter(torch.empty(out_dims, in_dims))
        if bias:
            self.bias = nn.Parameter(torch.empty(out_dims))
        else:
            self.register_parameter("bias", None)
        self.reset_parameters()

    def reset_parameters(self) -> None:
        nn.init.kaiming_uniform_(self.weight, a=math.sqrt(5))
        if self.bias is not None:
            fan_in, _ = nn.init._calculate_fan_in_and_fan_out(self.weight)
            bound = 1 / math.sqrt(fan_in)
            nn.init.uniform_(self.bias, -bound, bound)

    def forward(self, x: torch.Tensor, adj: torch.Tensor) -> torch.Tensor:
        if x.ndim != 2:
            raise ValueError(f"Expected 2D input for MoFNetLayer, got shape {tuple(x.shape)}")
        if adj.shape != (self.in_dims, self.out_dims):
            raise ValueError(
                "Adjacency shape mismatch: "
                f"expected {(self.in_dims, self.out_dims)}, got {tuple(adj.shape)}"
            )
        output = x.matmul(self.weight.t() * adj)
        if self.bias is not None:
            output = output + self.bias
        return output


class MoFNet(nn.Module):
    """Single-file MoFNet model. v1.1.0 baseline."""

    def __init__(
        self,
        adj1: torch.Tensor,
        adj2: torch.Tensor,
        hidden2: int = 96,
        hidden3: int = 16,
        dropout: float = 0.5,
    ):
        super().__init__()
        adj1 = adj1.float()
        adj2 = adj2.float()
        modality_b_dims, transparent_dims = adj1.shape
        modality_a_dims = int(adj2.shape[0] - transparent_dims)
        hidden1_dims = int(adj2.shape[1])

        self.modality_a_dims = int(modality_a_dims)
        self.modality_b_dims = int(modality_b_dims)
        self.transparent_dims = int(transparent_dims)
        self.hidden1_dims = int(hidden1_dims)
        self.input_dims = int(self.modality_a_dims + self.modality_b_dims)

        self.register_buffer("adj1", adj1)
        self.register_buffer("adj2", adj2)

        self.mofnet1 = MoFNetLayer(self.modality_b_dims, self.transparent_dims)
        self.mofnet2 = MoFNetLayer(self.modality_a_dims + self.transparent_dims, self.hidden1_dims)

        self.dropout = nn.Dropout(float(dropout))
        self.linear2 = nn.Linear(self.hidden1_dims, int(hidden2))
        self.linear3 = nn.Linear(int(hidden2), int(hidden3))
        self.linear4 = nn.Linear(int(hidden3), 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        modality_a = x[:, : self.modality_a_dims]
        modality_b = x[:, self.modality_a_dims :]
        t1 = torch.relu(self.mofnet1(modality_b, self.adj1))
        h1_input = torch.cat((modality_a, t1), dim=1)
        h1 = torch.relu(self.mofnet2(h1_input, self.adj2))
        h2 = torch.relu(self.linear2(self.dropout(h1)))
        h3 = torch.relu(self.linear3(self.dropout(h2)))
        logits = self.linear4(h3).squeeze(1)
        return logits
