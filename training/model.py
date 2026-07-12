import os
import sys

import tensorflow as tf
from tensorflow.keras import layers, models

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import config


def build_transfer_learning_model(num_classes=config.NUM_CLASSES, fine_tune=False):

    base_model = tf.keras.applications.MobileNetV2(
        input_shape=(config.IMG_HEIGHT, config.IMG_WIDTH, 3),
        include_top=False,
        weights="imagenet",
    )

    if not fine_tune:
        base_model.trainable = False
    else:
        base_model.trainable = True
        for layer in base_model.layers[: config.FINE_TUNE_AT_LAYER]:
            layer.trainable = False

    inputs = tf.keras.Input(shape=(config.IMG_HEIGHT, config.IMG_WIDTH, 3))

    x = layers.Rescaling(scale=1.0 / 127.5, offset=-1.0)(inputs)
    x = base_model(x, training=False if not fine_tune else None)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dropout(0.3)(x)
    x = layers.Dense(128, activation="relu")(x)
    x = layers.Dropout(0.2)(x)
    outputs = layers.Dense(num_classes, activation="softmax")(x)

    model = models.Model(inputs, outputs, name="ecosort_mobilenetv2")
    return model, base_model


def build_custom_cnn(num_classes=config.NUM_CLASSES):

    model = models.Sequential(
        [
            layers.Input(shape=(config.IMG_HEIGHT, config.IMG_WIDTH, 3)),
            layers.Rescaling(1.0 / 255),

            layers.Conv2D(32, 3, activation="relu", padding="same"),
            layers.BatchNormalization(),
            layers.MaxPooling2D(),

            layers.Conv2D(64, 3, activation="relu", padding="same"),
            layers.BatchNormalization(),
            layers.MaxPooling2D(),

            layers.Conv2D(128, 3, activation="relu", padding="same"),
            layers.BatchNormalization(),
            layers.MaxPooling2D(),

            layers.Conv2D(128, 3, activation="relu", padding="same"),
            layers.BatchNormalization(),
            layers.MaxPooling2D(),

            layers.GlobalAveragePooling2D(),
            layers.Dense(256, activation="relu"),
            layers.Dropout(0.4),
            layers.Dense(num_classes, activation="softmax"),
        ],
        name="ecosort_custom_cnn",
    )
    return model
