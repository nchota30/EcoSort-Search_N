import json
import os
import sys

import matplotlib
matplotlib.use("Agg")  
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import config
import model as model_lib
from data_loader import get_datasets


def make_callbacks(checkpoint_path):
    return [
        tf.keras.callbacks.ModelCheckpoint(
            checkpoint_path, save_best_only=True, monitor="val_accuracy", mode="max"
        ),
        tf.keras.callbacks.EarlyStopping(
            monitor="val_loss", patience=5, restore_best_weights=True
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss", factor=0.5, patience=3, min_lr=1e-7
        ),
    ]


def plot_history(history_list, save_path):
    """Concatène l'historique de plusieurs phases d'entraînement et trace les courbes."""
    acc, val_acc, loss, val_loss = [], [], [], []
    for h in history_list:
        acc += h.history["accuracy"]
        val_acc += h.history["val_accuracy"]
        loss += h.history["loss"]
        val_loss += h.history["val_loss"]

    epochs_range = range(len(acc))

    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    plt.plot(epochs_range, acc, label="Train")
    plt.plot(epochs_range, val_acc, label="Validation")
    plt.legend(loc="lower right")
    plt.title("Accuracy")

    plt.subplot(1, 2, 2)
    plt.plot(epochs_range, loss, label="Train")
    plt.plot(epochs_range, val_loss, label="Validation")
    plt.legend(loc="upper right")
    plt.title("Loss")

    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()


def evaluate_and_report(model, val_ds, class_names):
    """Génère le rapport de classification et la matrice de confusion sur la validation."""
    y_true, y_pred = [], []
    for images, labels_batch in val_ds:
        preds = model.predict(images, verbose=0)
        y_true.extend(np.argmax(labels_batch.numpy(), axis=1))
        y_pred.extend(np.argmax(preds, axis=1))

    report = classification_report(y_true, y_pred, target_names=class_names, digits=3)
    print("\n=== Rapport de classification (validation) ===")
    print(report)

    with open(config.CLASSIFICATION_REPORT_PATH, "w") as f:
        f.write(report)

    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(7, 6))
    sns.heatmap(
        cm, annot=True, fmt="d", cmap="Blues", xticklabels=class_names, yticklabels=class_names
    )
    plt.xlabel("Prédit")
    plt.ylabel("Réel")
    plt.title("Matrice de confusion")
    plt.tight_layout()
    plt.savefig(config.CONFUSION_MATRIX_PATH)
    plt.close()


def main():
    os.makedirs(config.SAVED_MODEL_DIR, exist_ok=True)
    os.makedirs(config.OUTPUTS_DIR, exist_ok=True)

    print(f"Architecture sélectionnée : {config.ARCHITECTURE}")
    train_ds, val_ds, class_names = get_datasets()
    print(f"Classes détectées : {class_names}")


    with open(config.CLASS_INDICES_PATH, "w") as f:
        json.dump(class_names, f, indent=2)

    history_list = []

    if config.ARCHITECTURE == "mobilenetv2":
        # --- Phase 1 : entraînement de la tête, backbone gelé ---
        model, base_model = model_lib.build_transfer_learning_model(fine_tune=False)
        model.compile(
            optimizer=tf.keras.optimizers.Adam(config.LEARNING_RATE_HEAD),
            loss="categorical_crossentropy",
            metrics=["accuracy"],
        )
        model.summary()

        print("\n--- Phase 1 : entraînement de la tête (backbone gelé) ---")
        history1 = model.fit(
            train_ds,
            validation_data=val_ds,
            epochs=config.EPOCHS_HEAD,
            callbacks=make_callbacks(config.MODEL_PATH),
        )
        history_list.append(history1)

        #  Phase 2 : fine-tuning des dernières couches du backbone 
        print("\n--- Phase 2 : fine-tuning ---")
        base_model.trainable = True
        for layer in base_model.layers[: config.FINE_TUNE_AT_LAYER]:
            layer.trainable = False

        model.compile(
            optimizer=tf.keras.optimizers.Adam(config.LEARNING_RATE_FINE_TUNE),
            loss="categorical_crossentropy",
            metrics=["accuracy"],
        )
        history2 = model.fit(
            train_ds,
            validation_data=val_ds,
            epochs=config.EPOCHS_FINE_TUNE,
            callbacks=make_callbacks(config.MODEL_PATH),
        )
        history_list.append(history2)

    else:  
        model = model_lib.build_custom_cnn()
        model.compile(
            optimizer=tf.keras.optimizers.Adam(config.LEARNING_RATE_HEAD),
            loss="categorical_crossentropy",
            metrics=["accuracy"],
        )
        model.summary()

        print("\n--- Entraînement du CNN custom ---")
        history = model.fit(
            train_ds,
            validation_data=val_ds,
            epochs=config.EPOCHS_HEAD + config.EPOCHS_FINE_TUNE,
            callbacks=make_callbacks(config.MODEL_PATH),
        )
        history_list.append(history)

    #Sauvegarde finale, évaluation et artefacts
    model.save(config.MODEL_PATH)
    print(f"\nModèle sauvegardé : {config.MODEL_PATH}")

    plot_history(history_list, config.HISTORY_PLOT_PATH)
    evaluate_and_report(model, val_ds, class_names)

    print(f"\nArtefacts d'entraînement disponibles dans : {config.OUTPUTS_DIR}")


if __name__ == "__main__":
    main()
