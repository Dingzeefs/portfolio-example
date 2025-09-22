# CNN Architecture Exploration with MLflow

This project demonstrates hypothesis-driven experimentation with CNN architectures using MLflow for experiment tracking.

## Features

- **Hypothesis-driven experiments**: Systematic exploration of CNN architecture choices
- **MLflow integration**: Automatic experiment tracking and visualization
- **Interactive notebook**: Pause-and-hypothesis approach for learning
- **Architecture comparisons**: Dropout, normalization, and hyperparameter effects

## Files

- `04_experiments.ipynb` - Main experiment notebook with hypothesis-driven approach
- `03_mlflow.py` - Reference implementation showing MLflow integration patterns
- `mlflow.db` - MLflow database with completed experiments
- `models/` - Saved model artifacts from experiments
- `experiment_log/` - Additional experiment documentation
- `start_server.sh` / `stop_server.sh` - MLflow server management scripts

## Quick Start

1. **Install dependencies**:
   ```bash
   uv sync
   ```

2. **Start MLflow server**:
   ```bash
   ./start_server.sh
   ```

3. **Open the notebook**:
   ```bash
   uv run jupyter lab 04_experiments.ipynb
   ```

4. **View MLflow UI**: http://127.0.0.1:5001

## Experiment Structure

The notebook follows a scientific methodology:

1. **Baseline Model** - Establish performance baseline
2. **Dropout Experiments** - Test regularization effects
3. **Normalization Experiments** - Compare BatchNorm, LayerNorm, etc.
4. **Combined Architectures** - Test interactions between techniques
5. **Analysis & Visualization** - Compare results across experiments

## Key Learning Objectives

- Understand the effect of dropout on overfitting
- Compare different normalization techniques
- Learn MLflow for experiment tracking
- Practice hypothesis-driven experimentation
- Analyze architecture choices systematically

## Technology Stack

- **PyTorch** - Deep learning framework
- **MLflow** - Experiment tracking and model registry
- **MLtrainer** - Training utilities with automatic MLflow integration
- **MADS Datasets** - Fashion-MNIST dataset provider
- **Hyperopt** - Hyperparameter optimization

## Results

The MLflow database contains completed experiments showing:
- Baseline CNN performance on Fashion-MNIST
- Effects of different dropout rates (0.0, 0.1, 0.3, 0.5)
- Comparison of normalization techniques
- Training curves and final metrics for all experiments

Access the results via the MLflow UI to explore experiment comparisons and model artifacts.