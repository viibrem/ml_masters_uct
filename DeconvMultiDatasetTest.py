import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.datasets import mnist
from tensorflow.keras.datasets import cifar10
import matplotlib.pyplot as plt
from DeconvDft2dLayer import DeconvDft2dLayer
import time


def mnist_deconv_test():
    print('\n=================================================================')
    print('=================================================================')
    print('                       Deconvolutional Model                     ')
    print('=================================================================')

    (x_train, y_train), (x_test, y_test) = mnist.load_data()
    x_train = x_train.astype("float32") / 255.0
    x_test = x_test.astype("float32") / 255.0

    # Functional API for Deconv Layer
    model = keras.Sequential([
        layers.Input(shape=(28, 28)),
        DeconvDft2dLayer((3, 3)),
        layers.Flatten(),
        layers.Dense(256, activation="relu", name="second_layer"),
        layers.Dense(10, activation="softmax"),
    ])

    return train_and_evaluate(model, x_test, x_train, y_test, y_train), model.layers[0].w


def mnist_conv_test():
    print('\n=================================================================')
    print('=================================================================')
    print('                      Convolution Model                          ')
    print('=================================================================')

    (x_train, y_train), (x_test, y_test) = mnist.load_data()
    x_train = x_train.astype("float32") / 255.0
    x_test = x_test.astype("float32") / 255.0

    # Functional API for Dense layer
    inputs = tf.keras.Input(shape=(28, 28, 1))
    x = layers.Conv2D(1, (3, 3))(inputs)
    x = layers.Flatten()(x)
    x = layers.Dense(256, activation="relu", name="second_layer")(x)
    outputs = layers.Dense(10, activation="softmax")(x)
    model = tf.keras.Model(inputs=inputs, outputs=outputs)

    return train_and_evaluate(model, x_test, x_train, y_test, y_train), tf.reshape(model.layers[1].kernel, (3, 3))


def mnist_dense_test():
    print('\n=================================================================')
    print('=================================================================')
    print('                         Dense Model                             ')
    print('=================================================================')

    (x_train, y_train), (x_test, y_test) = mnist.load_data()
    x_train = x_train.reshape(-1, 28 * 28).astype("float32") / 255.0
    x_test = x_test.reshape(-1, 28 * 28).astype("float32") / 255.0

    # Functional API for Dense layer
    model = keras.Sequential([
        layers.Input(shape=(28 * 28)),
        layers.Dense(512, activation="relu", name="first_layer"),
        layers.Dense(256, activation="relu", name="second_layer"),
        layers.Dense(10, activation="softmax"),
    ])

    return train_and_evaluate(model, x_test, x_train, y_test, y_train), None


def cifar10_dataset_test():
    (x_train, y_train), (x_test, y_test) = cifar10.load_data()
    x_train = x_train.astype("float32") / 255.0
    x_test = x_test.astype("float32") / 255.0

    def my_model():
        inputs = tf.keras.Input(shape=(32, 32, 3))
        x = layers.Conv2D(32, 3)(inputs)
        x = layers.BatchNormalization()(x)
        x = tf.keras.activations.relu(x)
        x = layers.MaxPooling2D()(x)
        x = layers.Conv2D(64, 3)(x)
        x = layers.BatchNormalization()(x)
        x = tf.keras.activations.relu(x)
        x = layers.MaxPooling2D()(x)
        x = layers.Conv2D(128, 3)(x)
        x = layers.BatchNormalization()(x)
        x = tf.keras.activations.relu(x)
        x = layers.Flatten()(x)
        outputs = layers.Dense(10, activation='relu')(x)
        model = tf.keras.Model(inputs=inputs, outputs=outputs)
        return model

    def my_model_deconv():
        inputs = tf.keras.Inpput(shape=(32, 32, 3))

    model = my_model()
    model.compile(
        loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
        optimizer=tf.keras.optimizers.Adam(learning_rate=3e-4),
        metrics=['accuracy'],
    )

    model.fit(x_train, y_train, batch_size=64, epochs=10, verbose=2)
    print("Evaluate")
    model.evaluate(x_test, y_test, batch_size=64, verbose=2)


def gcifar10_conv_test():
    ds_train, ds_test = gcifar10_from_directory()

    # Define NN
    inputs = tf.keras.Input(shape=(32, 32, 1))
    x = layers.Conv2D(32, 3)(inputs)
    x = layers.BatchNormalization()(x)
    x = tf.keras.activations.relu(x)
    x = layers.MaxPooling2D()(x)
    x = layers.Conv2D(64, 3)(x)
    x = layers.BatchNormalization()(x)
    x = tf.keras.activations.relu(x)
    x = layers.MaxPooling2D()(x)
    x = layers.Conv2D(128, 3)(x)
    x = layers.BatchNormalization()(x)
    x = tf.keras.activations.relu(x)
    x = layers.Flatten()(x)
    outputs = layers.Dense(10, activation='relu')(x)
    model = tf.keras.Model(inputs=inputs, outputs=outputs)

    return train_and_evaluate_ds(model, ds_train, ds_test)


def gcifar10_from_directory():
    ds_train = tf.keras.preprocessing.image_dataset_from_directory(
        'C:/Users/Rashaad/Documents/Postgrad/Datasets/cifar10_grayscale/images/',
        labels='inferred',
        label_mode='int',  # categorical binary
        color_mode='grayscale',
        batch_size=64,
        image_size=(32, 32),
        shuffle=True,
        seed=123,
        validation_split=0.2,
        subset='training'
    )
    ds_test = tf.keras.preprocessing.image_dataset_from_directory(
        'C:/Users/Rashaad/Documents/Postgrad/Datasets/cifar10_grayscale/images/',
        labels='inferred',
        label_mode='int',  # categorical binary
        color_mode='grayscale',
        batch_size=64,
        image_size=(32, 32),
        shuffle=True,
        seed=123,
        validation_split=0.2,
        subset='validation'
    )
    return ds_train, ds_test


def train_and_evaluate(model, x_test, x_train, y_test, y_train):
    model.summary()
    model.compile(loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=False),
                  optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
                  metrics=['accuracy'])
    t0 = time.time()
    history = model.fit(x_train, y_train, batch_size=32, epochs=10, verbose=2)
    results = model.evaluate(x_test, y_test, batch_size=32, verbose=2)
    t1 = time.time()
    td = t1 - t0

    return history, results, td


def train_and_evaluate_ds(model, ds_train, ds_test):
    model.summary()
    model.compile(loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=False),
                  optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
                  metrics=['accuracy'])
    t0 = time.time()
    history = model.fit(ds_train, batch_size=64, epochs=10, verbose=2)
    results = model.evaluate(ds_test, batch_size=64, verbose=2)
    t1 = time.time()
    td = t1 - t0

    return history, results, td


def mnist_test_comparison():
    results = {'dense': mnist_dense_test(),
               'deconv': mnist_deconv_test(),
               'conv': mnist_conv_test()}
    return results


def plot_results(results):
    fig, (ax1, ax2) = plt.subplots(1, 2)
    fig.suptitle('Accuracy and Loss plots')

    for i in results.keys():
        ax1.plot(results[i][0][0].history['accuracy'])
        ax2.plot(results[i][0][0].history['loss'])

    ax1.set(xlabel='Epochs', ylabel='Accuracy')
    ax1.legend(results.keys(), loc='lower right')
    ax2.set(xlabel='Epochs', ylabel='Loss')
    ax2.legend(results.keys(), loc='upper right')

    plt.show()


if __name__ == '__main__':
    physical_devices = tf.config.list_physical_devices("GPU")
    tf.config.experimental.set_memory_growth(physical_devices[0], True)

    # results = gcifar10_conv_test()
    # cifar10_dataset_test()

    results = mnist_test_comparison()
    # Output time taken for results
    for i in results.keys():
        t = round(results[i][0][2], 3)
        print('Time taken for ' + i + ': ' + str(t) + ' seconds')

    for i in results.keys():
        print('Weights for ' + i)
        print(results[i][-1])

    plot_results(results)


