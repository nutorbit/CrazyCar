import torch
import torch.nn as nn
import torch.nn.functional as F

from torch.distributions import Normal


def make_mlp(sizes, activation, output_activation=nn.Identity):
    layers = []
    for j in range(len(sizes)-1):
        if j < len(sizes)-2:
            # layers += [nn.Linear(sizes[j], sizes[j+1]), nn.BatchNorm1d(sizes[j+1]), activation()]
            layers += [nn.Linear(sizes[j], sizes[j + 1]), activation()]
        else:  # output layer
            layers += [nn.Linear(sizes[j], sizes[j+1]), output_activation()]
    return nn.Sequential(*layers)


class BaseModel(nn.Module):
    def __init__(self, obs_dim, act_dim):
        super().__init__()
        self.obs_dim = obs_dim
        self.act_dim = act_dim

    def soft_update(self, other_network, tau):

        other_variables = other_network.parameters()
        current_variables = self.parameters()

        with torch.no_grad():
            for (current_var, other_var) in zip(current_variables, other_variables):
                current_var.data.copy_(tau * other_var.data + (1.0 - tau) * current_var.data)

    def hard_update(self, other_network):
        self.soft_update(other_network, tau=1.)


class Critic(BaseModel):
    def __init__(self, obs_dim, act_dim):
        super().__init__(obs_dim, act_dim)
        sizes = [obs_dim + act_dim] + [256, 256, 256] + [1]
        self.q1 = make_mlp(sizes=sizes, activation=nn.ReLU)
        self.q2 = make_mlp(sizes=sizes, activation=nn.ReLU)

    def forward(self, obs, act):
        concat = torch.cat([obs, act], dim=1)
        return self.q1(concat), self.q2(concat)


class Actor(BaseModel):
    def __init__(self, obs_dim, act_dim, action_space=None):
        super().__init__(obs_dim, act_dim)
        sizes = [obs_dim] + [256, 256, 256]
        self.hidden = make_mlp(sizes, activation=nn.ReLU, output_activation=nn.ReLU)
        self.mean = nn.Linear(256, act_dim)
        self.log_std = nn.Linear(256, act_dim)

        if action_space is None:
            self.action_scale = torch.tensor(1.)
            self.action_bias = torch.tensor(0.)
        else:
            self.action_scale = torch.FloatTensor((action_space.high - action_space.low) / 2.)
            self.action_bias = torch.FloatTensor((action_space.high + action_space.low) / 2.)

    def forward(self, obs):
        x = self.hidden(obs)
        mean = self.mean(x)
        log_std = self.log_std(x)
        log_std = torch.clamp(log_std, min=-20, max=2)
        return mean, log_std

    def sample(self, obs):
        mean, log_std = self.forward(obs)
        std = log_std.exp()
        normal = Normal(mean, std)

        x_t = normal.rsample()
        y_t = torch.tanh(x_t)
        action = y_t * self.action_scale + self.action_bias
        log_prob = normal.log_prob(x_t)

        log_prob -= torch.log(self.action_scale * (1 - y_t.pow(2)) + 1e-6)
        log_prob = log_prob.sum(1, keepdim=True)
        mean = torch.tanh(mean) * self.action_scale + self.action_bias
        return action, log_prob, mean

    def to(self, device):
        self.action_scale = self.action_scale.to(device)
        self.action_bias = self.action_bias.to(device)
        return super().to(device)
