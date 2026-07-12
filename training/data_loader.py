import os
import tensorflow as tf
from tensorflow.keras import layers

import config


def _check_data_dir():
    if not os.path.isdir(config.DATA_DIR):
        raise FileNotFoundError(
            f"Dataset introuvable dans '{config.DATA_DIR}'.\n"
            "Télécharge le dataset Kaggle 'Garbage Classification' et place-le "
            "dans data/raw/ avec un sous-dossier par classe "
            f"({config.CLASS_NAMES}). Ce dossier ne doit JAMAIS être commité "
            "(voir .gitignore)."
        )


def get_datasets():

    _check_data_dir()

    train_ds = tf.keras.utils.image_dataset_from_directory(
        config.DATA_DIR,
        validation_split=config.VALIDATION_SPLIT,
        subset="training",
        seed=config.SEED,
        image_size=config.IMG_SIZE,
        batch_size=config.BATCH_SIZE,
        label_mode="categorical",
    )

    val_ds = tf.keras.utils.image_dataset_from_directory(
        config.DATA_DIR,
        validation_split=config.VALIDATION_SPLIT,
        subset="validation",
        seed=config.SEED,
        image_size=config.IMG_SIZE,
        batch_size=config.BATCH_SIZE,
        label_mode="categorical",
    )

    class_names = train_ds.class_names  # ordre alphabétique, déterministe

    # Sécurité : vérifie que les classes trouvées correspondent à celles attendues
    if sorted(class_names) != sorted(config.CLASS_NAMES):
        raise ValueError(
            f"Classes trouvées dans le dataset {class_names} "
            f"!= classes attendues dans config.py {config.CLASS_NAMES}. "
            "Vérifie l'organisation des dossiers."
        )

    # Data augmentation (appliquée uniquement au train, pas à la validation) 
    data_augmentation = tf.keras.Sequential(
        [
            layers.RandomFlip("horizontal"),
            layers.RandomRotation(0.15),
            layers.RandomZoom(0.15),
            layers.RandomContrast(0.1),
        ],
        name="data_augmentation",
    )

    train_ds = train_ds.map(
        lambda x, y: (data_augmentation(x, training=True), y),
        num_parallel_calls=tf.data.AUTOTUNE,
    )

    # Cache + prefetch pour accélérer l'entraînement
    autotune = tf.data.AUTOTUNE
    train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=autotune)
    val_ds = val_ds.cache().prefetch(buffer_size=autotune)

    return train_ds, val_ds, class_names
