import tensorflow as tf
from tensorflow.keras import layers


class DeconvDft2dLayer(layers.Layer):

    def __init__(self, h_shape):
        super(DeconvDft2dLayer, self).__init__()
        self.h_shape = h_shape

        # Initialise filter (w) except for the first element
        # So that first element is not trainable
        self.w = tf.random.uniform((1, h_shape[-2] * h_shape[-1] - 1))
        self.w = tf.Variable(self.w, trainable=True)

    def custom_op(self, xm):
        xm = tf.reshape(xm, (-1, xm.shape[-3], xm.shape[-2]))

        pad_w = tf.constant([[0, 0], [1, 0]])
        # Set first element to 1 then reshape into specified filter shape
        w0 = tf.pad(self.w, pad_w, mode='CONSTANT', constant_values=1)
        w0 = tf.reshape(w0, self.h_shape)

        padding = tf.constant(
            [[0, 0], [int(xm.shape[-2] / 4), int(xm.shape[-2] / 4)], [int(xm.shape[-1] / 4), int(xm.shape[-1] / 4)]])
        xm = tf.pad(xm, padding, "CONSTANT")

        paddings = tf.constant([[0, xm.shape[-2] - w0.shape[-2]], [0, xm.shape[-1] - w0.shape[-1]]])
        hm1 = tf.pad(w0, paddings, "CONSTANT")

        gm1f = tf.divide(1, tf.signal.rfft2d(hm1))
        gm2f = tf.roll(tf.reverse(gm1f, [0]), shift=1, axis=0)
        gm3f = tf.roll(tf.reverse(gm1f, [1]), shift=1, axis=1)
        gm4f = tf.roll(tf.reverse(gm3f, [0]), shift=1, axis=0)

        gmf1 = tf.multiply(gm1f, gm2f)
        gmf2 = tf.multiply(gm3f, gm4f)
        gmf = tf.multiply(gmf1, gmf2)

        ymf = tf.multiply(gmf, tf.signal.rfft2d(xm))
        ym = tf.signal.irfft2d(ymf)

        ym = tf.reshape(ym, (-1, ym.shape[-2], ym.shape[-1], 1))
        ym = tf.image.central_crop(ym, 0.67)

        return ym

    def call(self, inputs):
        return self.custom_op(inputs)
