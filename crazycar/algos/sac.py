import tensorflow as tf
import sonnet as snt

from tensorflow_probability import distributions

from crazycar.utils import make_mlp
from crazycar.algos.base import BaseModel, BaseNetwork


EPS = 1e-16


class Actor(BaseNetwork):
    """
    Actor for DDPG

    Args:
        encoder: class from crazycar.encoder
        act_dim: number of action
        hiddens: NO. units for each layers
    """

    def __init__(self, encoder, act_dim, hiddens=[256, 256], name=None):
        super().__init__(name=name)
        self.enc = encoder()
        self.act_dim = act_dim
        self.hidden = make_mlp(
            sizes=hiddens,
            activation=tf.nn.tanh
        )
        self.mean = snt.Linear(act_dim)
        self.log_std = snt.Linear(act_dim)
        self.initialize_input()

    @tf.function
    def __call__(self, obs):
        x = self.enc(obs)
        x = self.hidden(x)
        mean = self.mean(x)
        log_std = self.log_std(x)
        return mean, log_std

    @tf.function
    def sample(self, obs):
        mean, log_std = self(obs)
        std = tf.exp(log_std)
        dist = distributions.Normal(mean, std)

        # sample the action and apply tanh squashing
        action_sample = dist.sample()
        action = tf.tanh(action_sample)

        # calculate log prob
        log_prob = dist.log_prob(action_sample)
        log_prob -= tf.reduce_sum(tf.math.log(1 - action**2 + EPS), axis=1, keepdims=True)

        return action, log_prob


class Critic(BaseNetwork):
    """
    Double Q for DDPG

    Args:
        encoder: class from crazycar.encoder
        act_dim: number of action
        hiddens: NO. units for each layers
    """

    def __init__(self, encoder, act_dim, hiddens=[256, 256], name=None):
        super().__init__(name=name)
        self.enc = encoder()
        self.act_dim = act_dim
        # print([self.enc.out_size + act_dim] + hiddens + [1])
        self.q1 = make_mlp(sizes=hiddens + [1], activation=tf.nn.tanh)
        self.q2 = make_mlp(sizes=hiddens + [1], activation=tf.nn.tanh)
        self.initialize_input()

    @tf.function
    def __call__(self, obs, act):
        x = self.enc(obs)
        x = tf.concat([x, act], axis=1)
        return self.q1(x), self.q2(x)


class SAC(BaseModel):
    """
    Soft Actor-Critic

    Args:
        ...
    """

    def __init__(self, encoder, act_dim,
                 lr=1e-4,
                 gamma=0.5,
                 interval_target=2,
                 tau=0.05,
                 replay_size=int(1e5),
                 hiddens=[256, 256],
                 name="SAC"):

        super().__init__(replay_size, name=name)

        self.tau = tau
        self.gamma = gamma
        self.interval_target = interval_target

        # define actor
        self.actor = Actor(encoder, act_dim, hiddens, name="actor")
        self.actor_target = Actor(encoder, act_dim, hiddens, name="actor_target")
        self.actor_target.hard_update(self.actor)

        # define critic
        self.critic = Critic(encoder, act_dim, hiddens, name="critic")
        self.critic_target = Critic(encoder, act_dim, hiddens, name="critic_target")
        self.critic_target.hard_update(self.critic)

        # define alpha
        self.log_alpha = tf.Variable(.0, dtype=tf.float32)
        self.target_entropy = -tf.constant(act_dim, dtype=tf.float32)

        # define optimizer
        self.actor_opt = snt.optimizers.Adam(lr)
        self.critic_opt = snt.optimizers.Adam(lr)
        self.alpha_opt = snt.optimizers.Adam(lr)

    @tf.function
    def actor_loss(self, batch):
        """
        L(s) = -E[Q(s, a)| a~u(s)]

        Where,
            Q is a soft-Q: Q - alpha * log_prob
        """

        act, log_prob = self.actor.sample(batch['obs'])
        q1, q2 = self.critic(batch['obs'], act)
        q = tf.minimum(q1, q2) - tf.exp(self.log_alpha) * log_prob
        loss = -tf.reduce_mean(q)
        return loss

    @tf.function
    def critic_loss(self, batch):
        """
        L(s, a) = (y - Q(s,a))^2

        Where,
            Q is a soft-Q: Q - alpha * log_prob
            y(s, a) = r(s, a) + (1 - done) * gamma * Q'(s', a'); a' ~ u'(s')
        """

        next_act, next_log_prob = self.actor_target.sample(batch['obs'])
        q_target1, q_target2 = self.critic_target(batch['next_obs'], next_act)
        q_target = tf.minimum(q_target1, q_target2) - tf.exp(self.log_alpha) * next_log_prob
        y = batch['rew'] + (1 - batch['done']) * self.gamma * tf.stop_gradient(q_target)

        q1, q2 = self.critic(batch['obs'], batch['act'])

        loss1 = tf.reduce_mean(tf.square(y - q1))
        loss2 = tf.reduce_mean(tf.square(y - q2))

        return loss1 + loss2

    @tf.function
    def alpha_loss(self, batch):
        """
        L = -(alpha * log_prob + target_entropy)
        """

        act, log_prob = self.actor.sample(batch['obs'])
        loss = -tf.reduce_mean(self.log_alpha * (log_prob + self.target_entropy))
        return loss

    @tf.function
    def update_alpha(self, batch):
        with tf.device('/GPU:0' if tf.test.is_gpu_available() else '/CPU:0'):
            with tf.GradientTape() as tape:
                loss = self.alpha_loss(batch)

            # Optimize the alpha
            grads = tape.gradient(loss, [self.log_alpha])
            self.alpha_opt.apply(grads, [self.log_alpha])

        return loss

    def update_params(self, i, batch_size=256):
        batch = self.rb.sample(batch_size)

        critic_loss = self.update_critic(batch)
        actor_loss = self.update_actor(batch)
        alpha_loss = self.update_alpha(batch)

        # update target network
        if i % self.interval_target == 0:
            self.actor_target.soft_update(self.actor, self.tau)
            self.critic_target.soft_update(self.critic, self.tau)

        return {
            "actor_loss": actor_loss.numpy(),
            "critic_loss": critic_loss.numpy(),
            "alpha_loss": alpha_loss.numpy(),
            "alpha": tf.exp(self.log_alpha).numpy()
        }

    def write_metric(self, metric, step):
        tf.summary.scalar("loss/actor_loss", metric['actor_loss'], step)
        tf.summary.scalar("loss/critic_loss", metric['critic_loss'], step)
        tf.summary.scalar("loss/alpha_loss", metric['alpha_loss'], step)
        tf.summary.scalar("track/alpha", metric['alpha'], step)

    def predict(self, obs):
        act, _ = self.actor.sample(obs)
        act = act.numpy()
        if len(act[0]) == 2:
            # apply rescale to speed
            act[0][0] = self.rescale(act[0][0])
        return act


if __name__ == "__main__":
    from crazycar.encoder import Sensor, Image
    from crazycar.utils import set_seed

    from crazycar.agents.constants import SENSOR_SHAPE, CAMERA_SHAPE

    set_seed()
    agent = SAC(Sensor, 5)

    tmp = {
        "sensor": tf.ones((1, ) + SENSOR_SHAPE),
        "image": tf.ones((1, ) + CAMERA_SHAPE)
    }

    print(agent.predict(tmp))
