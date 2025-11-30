"""Analyze hyperparameter tuning results."""

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from loguru import logger
from ray.tune import ExperimentAnalysis


def load_latest_experiment(tune_dir: Path) -> ExperimentAnalysis:
    """Load the latest Ray Tune experiment."""
    experiments = sorted([d for d in tune_dir.iterdir() if d.is_dir()])
    if not experiments:
        raise ValueError(f"No experiments found in {tune_dir}")

    latest = experiments[-1]
    logger.info(f"Loading experiment from: {latest}")
    return ExperimentAnalysis(latest)


def create_parallel_plot(df: pd.DataFrame, columns: list[str], color: str = "val_acc"):
    """Create parallel coordinates plot."""
    fig = px.parallel_coordinates(
        df[columns + [color]].dropna(),
        color=color,
        color_continuous_scale=px.colors.diverging.Tealrose,
        title="Hyperparameter Parallel Coordinates",
    )
    return fig


def create_scatter_matrix(df: pd.DataFrame, dimensions: list[str]):
    """Create scatter matrix of hyperparameters."""
    fig = px.scatter_matrix(
        df,
        dimensions=dimensions,
        color="val_acc",
        title="Hyperparameter Scatter Matrix",
    )
    return fig


def create_heatmap(df: pd.DataFrame, x: str, y: str, z: str = "val_acc"):
    """Create heatmap for two hyperparameters."""
    pivot = df.pivot_table(values=z, index=y, columns=x, aggfunc="mean")

    fig = go.Figure(data=go.Heatmap(z=pivot.values, x=pivot.columns, y=pivot.index))

    fig.update_layout(
        title=f"{z} vs {x} and {y}",
        xaxis_title=x,
        yaxis_title=y,
    )

    return fig


def analyze_results(tune_dir: Path):
    """Analyze and visualize hyperparameter tuning results."""
    # Load experiment
    analysis = load_latest_experiment(tune_dir)
    df = analysis.results_df

    # Get best configuration
    best_config = analysis.get_best_config(metric="val_acc", mode="max")
    best_result = analysis.best_result

    logger.info("=" * 60)
    logger.info("BEST CONFIGURATION")
    logger.info("=" * 60)
    for key, value in best_config.items():
        if not key.startswith("config/"):
            logger.info(f"{key}: {value}")
    logger.info(f"Validation Accuracy: {best_result['val_acc']:.4f}")
    logger.info(f"Validation Loss: {best_result['val_loss']:.4f}")
    logger.info("=" * 60)

    # Select columns for analysis
    param_cols = [
        "config/num_conv_layers",
        "config/base_filters",
        "config/dropout",
        "config/learning_rate",
    ]

    # Filter to only completed trials
    completed = df[df["training_iteration"] == df["training_iteration"].max()].copy()

    logger.info(f"\nTotal trials: {len(df)}")
    logger.info(f"Completed trials: {len(completed)}")

    # Create visualizations
    logger.info("\nCreating visualizations...")

    # Parallel coordinates
    fig1 = create_parallel_plot(completed, param_cols)
    fig1.write_html("parallel_coordinates.html")
    logger.info("Saved: parallel_coordinates.html")

    # Top 10 configurations
    top10 = completed.nlargest(10, "val_acc")[param_cols + ["val_acc", "val_loss"]]
    logger.info("\nTop 10 Configurations:")
    print(top10.to_string())

    # Summary statistics
    logger.info("\nSummary Statistics:")
    print(completed[param_cols + ["val_acc"]].describe())

    return analysis, completed


if __name__ == "__main__":
    tune_dir = Path("logs/ray").resolve()

    if not tune_dir.exists() or not list(tune_dir.iterdir()):
        logger.error(f"No experiments found in {tune_dir}")
        logger.info("Run hypertune.py first!")
    else:
        analysis, df = analyze_results(tune_dir)
