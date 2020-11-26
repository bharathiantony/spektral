"""
This example implements an experiment from the paper

    > [Design Space for Graph Neural Networks](https://arxiv.org/abs/2011.08843)<br>
    > Jiaxuan You, Rex Ying, Jure Leskovec

using the PROTEINS dataset.

The configuration at the top of the file is the best one identified in the
paper, and should work well for many different datasets without changes.

Note: the results reported in the paper are averaged over 3 random repetitions
with an 80/20 split.
"""
import tensorflow as tf
import numpy as np
from spektral.models import GeneralGNN

from spektral.data import DisjointLoader

from spektral.datasets import TUDataset
from tensorflow.keras.optimizers import Adam

physical_devices = tf.config.list_physical_devices('GPU')
tf.config.experimental.set_memory_growth(physical_devices[0], True)

# Best config
batch_size = 32
learning_rate = 0.01
epochs = 400

# Read data
data = TUDataset('PROTEINS')

# Train/test split
np.random.shuffle(data)
split = int(0.8 * len(data))
data_tr, data_te = data[:split], data[split:]

# Data loader
loader_tr = DisjointLoader(data_tr, batch_size=batch_size, epochs=epochs)
loader_te = DisjointLoader(data_te, batch_size=batch_size)

# Create model
model = GeneralGNN(data.n_labels, activation='softmax')
optimizer = Adam(learning_rate)
model.compile('adam', 'categorical_crossentropy', metrics=['categorical_accuracy'])


# Evaluation function
def evaluate(loader):
    step = 0
    results = []
    for batch in loader:
        step += 1
        loss, acc = model.test_on_batch(*batch)
        results.append((loss, acc))
        if step == loader.steps_per_epoch:
            return np.mean(results, 0)


# Training loop
epoch = step = 0
results = []
for batch in loader_tr:
    step += 1
    loss, acc = model.train_on_batch(*batch)
    results.append((loss, acc))
    if step == loader_tr.steps_per_epoch:
        step = 0
        epoch += 1
        results_te = evaluate(loader_te)
        print('Epoch {} - Train loss: {:.3f} - Train acc: {:.3f} - '
              'Test loss: {:.3f} - Test acc: {:.3f}'
              .format(epoch, *np.mean(results, 0), *results_te))

results_te = evaluate(loader_te)
print('Final results - Loss: {:.3f} - Acc: {:.3f}'.format(*results_te))
