import numpy as np
import random
import torch
import torch.nn as nn
import os
import logging
import json

from datetime import datetime

from torch.utils.tensorboard import SummaryWriter


def set_seed_everywhere(seed):
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    random.seed(seed)


def huber_loss(x, delta=10.):
    """
    Compute the huber loss.
    Ref: https://en.wikipedia.org/wiki/Huber_loss
    """

    delta = torch.ones_like(x) * delta
    less_than_max = 0.5 * (x * x)
    greater_than_max = delta * (torch.abs(x) - 0.5 * delta)

    return torch.where(
        torch.abs(x) <= delta,
        less_than_max,
        greater_than_max
    )


def weight_init(m):
    """
    delta-orthogonal init.
    Ref: https://arxiv.org/pdf/1806.05393.pdf
    """

    if isinstance(m, nn.Linear):
        nn.init.orthogonal_(m.weight.data)
        m.bias.data.fill_(0.0)
    elif isinstance(m, nn.Conv2d) or isinstance(m, nn.ConvTranspose2d):
        assert m.weight.size(2) == m.weight.size(3)
        m.weight.data.fill_(0.0)
        m.bias.data.fill_(0.0)
        mid = m.weight.size(2) // 2
        gain = nn.init.calculate_gain('relu')
        nn.init.orthogonal_(m.weight.data[:, :, mid, mid], gain)


def make_mlp(sizes, activation, output_activation=nn.Identity):
    layers = []
    for j in range(len(sizes)-1):
        if j < len(sizes)-2:
            # layers += [nn.Linear(sizes[j], sizes[j+1]), nn.BatchNorm1d(sizes[j+1]), activation()]
            layers += [nn.Linear(sizes[j], sizes[j + 1]), activation()]
        else:  # output layer
            layers += [nn.Linear(sizes[j], sizes[j+1]), output_activation()]
    return nn.Sequential(*layers)


def get_default_rb_dict(obs_dim, act_dim, size):
    return {
        "size": size,
        "default_dtype": np.float32,
        "env_dict": {
            "obs": {
                "shape": obs_dim
            },
            "act": {
                "shape": act_dim
            },
            "rew": {},
            "next_obs": {
                "shape": obs_dim
            },
            "done": {},
        }
    }


class Logger:

    def __init__(self, level=None):
        logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(name)s - %(levelname)s: %(message)s')
        self.logger = logging.getLogger('Logger')
        self.start_date = datetime.now().strftime("%b_%d_%Y_%H%M%S")
        self.steps = 0
        self.writer = None
        self.hyperparameter = None

        self.setup_directory()
        self.logger.info('Logger is ready')

    def setup_directory(self):
        # Create model directory
        if not os.path.exists(f'./save/{self.start_date}'):
            os.makedirs(f'./save/{self.start_date}')

    def start(self):

        self.writer = SummaryWriter(f'./save/{self.start_date}/')

        with open(f'./save/{self.start_date}/params.json', 'w') as f:
            json.dump(self.hyperparameter, f)

    def save_hyperparameter(self, **kwargs):
        # Save hyperparameter
        self.hyperparameter = kwargs
        self.logger.info('Parameter has saved.')

    def update_steps(self):
        self.steps += 1

    def save_model(self, model):
        torch.save(model, f'./save/{self.start_date}/models/td3_{self.steps + 1}.pth')
        self.logger.info('Model has saved.')

    def store(self, name, val):
        self.writer.add_scalar(name, val, self.steps)
        self.logger.info(f'[{name}] {val}')

