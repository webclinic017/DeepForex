from keras.layers import Dense,Dropout, Activation, Flatten, Convolution2D,Permute,LSTM
from keras.models import Sequential
from keras.optimizers import Adam
import numpy as np
import random
import os
from collections import deque

class Agent():
    def __init__(self, state_size, action_size,dir):
        self.weight_backup = "{}/weights.h5".format(dir)
        self.state_size = state_size
        self.action_size = action_size
        self.memory = deque(maxlen=20000)
        self.learning_rate = 0.01
        self.gamma = 0.99
        self.exploration_rate = 1.0
        self.exploration_min    = 0.01
        self.exploration_decay  = 0.995
        self.brain              = self._build_model()
    def _build_model(self):
        # Neural Net for Deep-Q learning Model
        model = Sequential()
        # model.add(Dense(24, input_dim=self.state_size, activation='relu'))
        # model.add(Dropout(0.5))
        # model.add(Dense(32, activation='relu'))
        # model.add(Dropout(0.5))
        # model.add(Dense(10, activation='relu'))
        # model.add(Dense(self.action_size, activation='linear'))
        # model.compile(loss='mse', optimizer=Adam(lr=self.learning_rate))
        #
        model.add(LSTM(32,  return_sequences=True,input_shape=(4,5)))
        model.add(LSTM(32,  return_sequences=True))
        model.add(LSTM(32))
        model.add(Dropout(0.5))
        model.add(Dense(32, activation='relu'))
        model.add(Dropout(0.5))
        model.add(Dense(20, activation='relu'))
        model.add(Dropout(0.5))
        model.add(Dense(10, activation='relu'))
        model.add(Dense(self.action_size, activation='linear'))
        # Create the model based on the information above
        model.compile(loss='mse', optimizer=Adam(lr=self.learning_rate))
        #model.compile(loss='mean_squared_error', optimizer='adam')
        if os.path.isfile(self.weight_backup):
                    model.load_weights(self.weight_backup)
                    self.exploration_rate = self.exploration_min
        return model
    def save_model(self):
            self.brain.save(self.weight_backup)
    def act(self, state):
        if np.random.rand() <= self.exploration_rate:
            return random.randrange(self.action_size)
        act_values = self.brain.predict(state)
        return np.argmax(act_values[0])
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))
    def replay(self, sample_batch_size):
        if len(self.memory) < sample_batch_size:
            return
        sample_batch = random.sample(self.memory, sample_batch_size)
        for state, action, reward, next_state, done in sample_batch:
            target = reward
            if not done:
              target = reward + self.gamma * np.amax(self.brain.predict(self.refortmatstate(next_state))[0])
            target_f = self.brain.predict(self.refortmatstate(state))
            target_f[0][action] = target
            self.brain.fit(self.refortmatstate(state), target_f, epochs=1, verbose=0)
        if self.exploration_rate > self.exploration_min:
            self.exploration_rate *= self.exploration_decay
    def refortmatstate(self,state):
        return np.reshape(state,(1,state.shape[0],state.shape[1]))
    def predict(self,state):
        return self.brain.predict(state)