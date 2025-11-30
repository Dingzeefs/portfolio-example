"""Hyperparameter tuning script using Ray Tune."""

from pathlib import Path
from typing import Any, Dict

import ray
import torch
import torch.nn as nn
import torch.optim as optim
from filelock import FileLock
from loguru import logger
from ray import tune
from ray.tune.schedulers import AsyncHyperBandScheduler
from ray.tune.search.hyperopt import HyperOptSearch
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

from src.model import ConfigurableCNN
from src.train import train_epoch, validate

# Configuration
MAX_EPOCHS = 10
NUM_SAMPLES = 20
BATCH_SIZE = 32


def get_data(data_dir: Path, batch_size: int = 32):
    """Load CIFAR-10 dataset with file locking."""
    with FileLock(data_dir / ".lock"):
        transform = transforms.Compose(
            [
                transforms.ToTensor(),
                transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
            ]
        )

        train_dataset = datasets.CIFAR10(
            root=data_dir, train=True, download=True, transform=transform
        )

        val_dataset = datasets.CIFAR10(
            root=data_dir, train=False, download=True, transform=transform
        )

        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)

    return train_loader, val_loader


def get_data_with_augmentation(
    data_dir: Path, augmentation: str = "none", batch_size: int = 32
):
    """
    Load CIFAR-10 dataset with configurable augmentation.

    Args:
        data_dir: Path to data directory
        augmentation: One of ['none', 'light', 'medium', 'strong']
        batch_size: Batch size for training

    Returns:
        train_loader, val_loader
    """
    with FileLock(data_dir / ".lock"):
        # Define augmentation strategies
        if augmentation == "none":
            train_transform = transforms.Compose(
                [
                    transforms.ToTensor(),
                    transforms.Normalize(
                        (0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)
                    ),
                ]
            )
        elif augmentation == "light":
            train_transform = transforms.Compose(
                [
                    transforms.RandomHorizontalFlip(p=0.5),
                    transforms.ToTensor(),
                    transforms.Normalize(
                        (0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)
                    ),
                ]
            )
        elif augmentation == "medium":
            train_transform = transforms.Compose(
                [
                    transforms.RandomCrop(32, padding=4),
                    transforms.RandomHorizontalFlip(p=0.5),
                    transforms.ToTensor(),
                    transforms.Normalize(
                        (0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)
                    ),
                ]
            )
        elif augmentation == "strong":
            train_transform = transforms.Compose(
                [
                    transforms.RandomCrop(32, padding=4),
                    transforms.RandomHorizontalFlip(p=0.5),
                    transforms.ColorJitter(
                        brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1
                    ),
                    transforms.ToTensor(),
                    transforms.Normalize(
                        (0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)
                    ),
                ]
            )
        else:
            raise ValueError(f"Unknown augmentation: {augmentation}")

        # Validation transform (no augmentation)
        val_transform = transforms.Compose(
            [
                transforms.ToTensor(),
                transforms.Normalize(
                    (0.4914, 0.4822, 0.4465), (0.2023, 0.1994, 0.2010)
                ),
            ]
        )

        train_dataset = datasets.CIFAR10(
            root=data_dir, train=True, download=True, transform=train_transform
        )
        val_dataset = datasets.CIFAR10(
            root=data_dir, train=False, download=True, transform=val_transform
        )

        train_loader = DataLoader(
            train_dataset,
            batch_size=batch_size,
            shuffle=True,
            num_workers=2,
            pin_memory=True,
        )
        val_loader = DataLoader(
            val_dataset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=2,
            pin_memory=True,
        )

    logger.info(f"Loaded CIFAR-10 with augmentation='{augmentation}'")

    return train_loader, val_loader


def tune_model(config: Dict[str, Any]):
    """
    Training function for Ray Tune.

    This function will be called by Ray with different configs.
    """
    # Setup device
    device = "cuda" if torch.cuda.is_available() else "cpu"

    # Load data
    data_dir = Path(config["data_dir"])

    # Check if augmentation is specified in config
    if "augmentation" in config:
        train_loader, val_loader = get_data_with_augmentation(
            data_dir, augmentation=config["augmentation"], batch_size=BATCH_SIZE
        )
    else:
        train_loader, val_loader = get_data(data_dir, batch_size=BATCH_SIZE)

    # Create model
    model_config = {
        "input_channels": 3,
        "num_classes": 10,
        "num_conv_layers": int(config["num_conv_layers"]),
        "base_filters": int(config["base_filters"]),
        "use_batchnorm": config["use_batchnorm"],
        "dropout": config["dropout"],
        "activation": config.get("activation", "relu"),
        "use_skip_connections": config.get("use_skip_connections", False),
    }

    model = ConfigurableCNN(model_config).to(device)

    # Count parameters for capacity analysis
    param_info = model.count_parameters()

    # Setup training
    loss_fn = nn.CrossEntropyLoss()

    if config["optimizer"] == "adam":
        optimizer = optim.Adam(model.parameters(), lr=config["learning_rate"])
    else:
        optimizer = optim.SGD(
            model.parameters(), lr=config["learning_rate"], momentum=0.9
        )

    # Setup scheduler
    if config["scheduler"] == "step":
        scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=7, gamma=0.1)
    elif config["scheduler"] == "plateau":
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            optimizer, mode="min", patience=5, factor=0.5
        )
    else:
        scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=MAX_EPOCHS)

    # Training loop
    for epoch in range(config["epochs"]):
        train_loss, train_acc = train_epoch(
            model, train_loader, loss_fn, optimizer, device
        )
        val_loss, val_acc = validate(model, val_loader, loss_fn, device)

        # Update scheduler
        if isinstance(scheduler, optim.lr_scheduler.ReduceLROnPlateau):
            scheduler.step(val_loss)
        else:
            scheduler.step()

        # Report to Ray
        ray.train.report(
            {
                "train_loss": train_loss,
                "train_acc": train_acc,
                "val_loss": val_loss,
                "val_acc": val_acc,
                "total_params": param_info["total_params"],
                "conv_params": param_info["conv_params"],
                "fc_params": param_info["fc_params"],
                "param_ratio_conv": param_info["param_ratio_conv"],
            }
        )


if __name__ == "__main__":
    ray.init()

    # Setup paths
    data_dir = Path("data/raw").resolve()
    if not data_dir.exists():
        data_dir.mkdir(parents=True)
        logger.info(f"Created {data_dir}")

    tune_dir = Path("logs/ray").resolve()

    # Define search space
    config = {
        "data_dir": str(data_dir),
        "epochs": MAX_EPOCHS,
        # Model hyperparameters
        "num_conv_layers": tune.randint(2, 5),  # 2-4 conv layers
        "base_filters": tune.choice([16, 32, 64]),  # Base filter size
        "use_batchnorm": tune.choice([True, False]),
        "dropout": tune.uniform(0.0, 0.5),
        # Training hyperparameters
        "learning_rate": tune.loguniform(1e-4, 1e-2),
        "optimizer": tune.choice(["adam", "sgd"]),
        "scheduler": tune.choice(["step", "plateau", "cosine"]),
    }

    # Setup search algorithm
    search_alg = HyperOptSearch()

    # Setup scheduler
    scheduler = AsyncHyperBandScheduler(
        time_attr="training_iteration",
        grace_period=1,
        reduction_factor=3,
        max_t=MAX_EPOCHS,
    )

    # Run tuning
    logger.info(f"Starting hyperparameter tuning with {NUM_SAMPLES} samples")
    analysis = tune.run(
        tune_model,
        config=config,
        metric="val_acc",
        mode="max",
        num_samples=NUM_SAMPLES,
        search_alg=search_alg,
        scheduler=scheduler,
        storage_path=str(tune_dir),
        verbose=1,
    )

    # Print best config
    best_config = analysis.get_best_config(metric="val_acc", mode="max")
    logger.info(f"Best config: {best_config}")
    logger.info(f"Best validation accuracy: {analysis.best_result['val_acc']:.4f}")

    ray.shutdown()
