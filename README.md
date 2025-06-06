# Text Generation Language Models in PyTorch

This project implements four text generation language models using PyTorch:

- **Bigram model** — a simple neural network that learns character-to-character transition probabilities
- **LSTM model** — a recurrent neural network capable of learning longer-range character sequences using memory and context
- **GRU model** — a gated recurrent unit network for efficient sequence modeling with fewer parameters than LSTM
- **Transformer model** — inference-only; uses a pre-built transformer for high-quality text generation (training not yet supported)

The codebase is modular, config-driven, and supports training, checkpointing, early stopping, hyperparameter tuning, and generation from any model via CLI. Comprehensive unit tests are included for all major modules, including training, library, utilities, visualization, tuning, and model/CLI behavior (**current coverage: 98%, 544 stmts / 10 miss**).

## Table of Contents

- [Features](#features)
- [Model Architectures](#model-architectures)
- [Datasets](#datasets)
- [Configuration](#configuration)
- [Hyperparameter Tuning](#hyperparameter-tuning)
- [Usage](#usage)
- [Loss Visualization](#loss-visualization)
- [GPU Acceleration](#gpu-acceleration)
- [Example Output (LSTM)](#example-output-lstm)
- [Dependencies](#dependencies)
- [Docker Usage](#docker-usage)
- [Testing](#testing)
- [Future Improvements](#future-improvements)
- [License](#license)

## Features

- Character-level tokenization across multiple input files
- Dynamic vocabulary and index mapping
- Modular model registry for Bigram, LSTM, GRU, and Transformer (inference-only)
- Configurable training and hyperparameter tuning via `config.json`
- Automatic hyperparameter tuning with Optuna
- Adam optimizer with early stopping
- Automatic checkpoint rotation and resumption
- Multinomial sampling for randomized generation
- Comprehensive CLI interface with model selection, runtime, and hyperparameter configuration
- Full unit test coverage (98%) for all major modules
- Tests include generation and training for all models, tuning, visualization, CLI behavior, and argument parsing helpers
- Loss visualization with matplotlib, including smoothing and saving plots
- GPU-accelerated training by default
- Integrated dataset library with pre-configured datasets
- Support for local files, Hugging Face datasets, and built-in library datasets

## Model Architectures

### Bigram Model

A lightweight model that uses an embedding table to predict the next character from the current character only. Fast and simple, but limited in predictive capability.

### LSTM Model

A recurrent neural network using embedding, multi-layer LSTM, and projection back to vocab size. Learns long-range dependencies across sequences for improved generation.

### GRU Model

A gated recurrent unit network that efficiently models sequences with fewer parameters than LSTM, providing a balance between speed and performance.

### Transformer Model

Integration with a pre-built transformer model that uses self-attention mechanisms for sophisticated text generation. **Currently supports inference only** (cannot be trained or fine-tuned yet).

## Datasets

The project supports three types of datasets:

### Local Dataset

The `dataset/` directory (included in this repo) contains **100 filtered sample texts** for training, preprocessed from [Project Gutenberg](https://www.gutenberg.org). These texts have been cleaned and filtered using length, markup, and English word ratio heuristics.

For more training data, you can download the **full cleaned dataset (4,437 books)** [on Hugging Face](https://huggingface.co/datasets/Yosna/Project-Gutenberg-Training-Data).

### Built-in Library

The project includes a pre-configured library of datasets:

- **News** (0.03 GB) - AG News dataset
- **Science** (0.41 GB) - PubMed QA dataset
- **Movies** (0.49 GB) - IMDB dataset
- **Yelp** (0.51 GB) - Yelp Review Full dataset
- **SQuAD** (0.08 GB) - Stanford Question Answering Dataset
- **Tiny Stories** (1.89 GB) - Tiny Stories dataset
- **Stack Overflow** (5.75 GB) - Stack Overflow Questions dataset
- **Wikipedia** (18.81 GB) - English Wikipedia dataset

### Custom Hugging Face Datasets

You can use any dataset from the Hugging Face Hub by specifying the dataset name and configuration in `config.json`. This allows for flexible experimentation with different text sources.

## Configuration

All behavior is driven by a single `config.json` file.
Example:

```json
{
  "datasets": {
    "source": "library",
    "locations": {
      "local": {
        "directory": "dataset",
        "extension": "txt"
      },
      "library": {
        "data_name": "science"
      },
      "huggingface": {
        "data_name": "pubmed_qa",
        "config_name": "pqa_artificial",
        "split": "train",
        "field": "question"
      }
    }
  },
  "save_model": true,
  "models": {
    "bigram": {
      "runtime": {
        "training": true,
        "steps": 10000,
        "interval": 100,
        "patience": 10,
        "max_new_tokens": 100,
        "max_checkpoints": 10
      },
      "hparams": {
        "batch_size": 16,
        "block_size": 32,
        "lr": 0.001
      }
    },
    "lstm": {
      "runtime": {
        "training": true,
        "steps": 50000,
        "interval": 500,
        "patience": 10,
        "max_new_tokens": 200,
        "max_checkpoints": 10
      },
      "hparams": {
        "batch_size": 32,
        "block_size": 64,
        "lr": 0.0015,
        "embedding_dim": 64,
        "hidden_size": 128,
        "num_layers": 2
      }
    },
    "gru": {
      "runtime": {
        "training": true,
        "steps": 50000,
        "interval": 500,
        "patience": 10,
        "max_new_tokens": 200,
        "max_checkpoints": 10
      },
      "hparams": {
        "batch_size": 32,
        "block_size": 64,
        "lr": 0.0015,
        "embedding_dim": 64,
        "hidden_size": 128,
        "num_layers": 2
      }
    },
    "transformer": {
      "runtime": {
        "max_new_tokens": 256
      },
      "hparams": {
        "block_size": 32
      }
    }
  },
  "auto_tuning": true,
  "save_tuning": true,
  "tuning_ranges": {
    "batch_size": {
      "type": "int",
      "min": 8,
      "max": 128,
      "step": 8
    },
    "block_size": {
      "type": "int",
      "min": 16,
      "max": 256,
      "step": 16
    },
    "lr": {
      "type": "float",
      "min": 0.0001,
      "max": 0.1,
      "log": true
    },
    "embedding_dim": {
      "type": "int",
      "min": 8,
      "max": 128,
      "step": 8
    },
    "hidden_size": {
      "type": "int",
      "min": 16,
      "max": 256,
      "step": 16
    },
    "num_layers": {
      "type": "categorical",
      "values": [1, 2, 3]
    }
  },
  "visualization": {
    "show_plot": true,
    "smooth_loss": true,
    "smooth_val_loss": true,
    "weight": 0.9,
    "save_data": true
  }
}
```

You can configure:

- Dataset source and location
- Training parameters for each model
- Model architecture parameters
- Loss visualization settings
- Hyperparameter tuning ranges and options

## Hyperparameter Tuning

Automatic hyperparameter tuning is supported via [Optuna](https://optuna.org/).

- Enable tuning by setting `"auto_tuning": true` in `config.json`.
- Define search spaces in the `"tuning_ranges"` section (supports `int`, `float`, and `categorical` types).
- Tuning is integrated into the training workflow and can be controlled via the CLI or config.
- Results are saved and can be used to update model hyperparameters automatically if `"save_tuning": true`.

## Usage

### Command Line Interface

The project provides a flexible CLI for controlling model behavior:

```bash
# Basic usage with default model (transformer)
python main.py

# Select a specific model
python main.py --model [bigram | lstm | gru | transformer]

# Training configuration
python main.py --model lstm --training true --steps 1000 --interval 100

# Generation configuration
python main.py --model gru --training false --max-new-tokens 200

# Checkpoint management
python main.py --model lstm --max-checkpoints 5
```

#### Available CLI arguments:

- `--model`: Select model type (default: transformer)
- `--training`: Toggle training mode (true/false)
- `--steps`: Number of training steps
- `--interval`: Validation interval during training
- `--patience`: Early stopping patience
- `--max-new-tokens`: Maximum tokens to generate
- `--max-checkpoints`: Maximum checkpoints to keep
- `--batch-size`: Override batch size for training
- `--block-size`: Override context window size
- `--lr`: Override learning rate
- `--embedding-dim`: Override embedding dimension size
- `--hidden-size`: Override hidden layer size
- `--num-layers`: Override number of model layers

#### Notes

- The model argument will default to `--model transformer` if omitted.
- Any runtime arguments omitted will default to the respective value defined in `config.json`.
- Boolean flags support flexible input: `true`, `false`, `on`, `off`, `yes`, `no`, `1`, `0`.

### Train a model

```bash
# Train the Bigram model
python main.py --model bigram --training true
```

### Generate text

After training, switch to generation mode by setting `"training": false` inside the appropriate section of `config.json`:

```json
"training": false
```

Then run the same command to generate text:

```bash
python main.py --model lstm
```

The output will begin with a randomly selected seed character and continue for the configured number of tokens.

## Loss Visualization

- Plotting both training and validation loss curves
- Optional exponential smoothing for clearer trends
- Saving plots with timestamped filenames to a model-specific directory
- Configurable via `config.json`

## GPU Acceleration

- GPU acceleration is used by default if a CUDA device is available.

## Example Output (LSTM)

```
"Quite pit to well find out of his seed a smarters.

'Ha! you would
a vounty presending out a glanced the busband. The lamb"
```

While not yet semantically coherent, the model demonstrates accurate word shapes, spacing, punctuation, and rudimentary grammar. More training will improve realism and coherence.

## Dependencies

- Python 3.10+
- PyTorch
- matplotlib
- datasets (Hugging Face)
- numpy
- transformers
- pytest (for unit testing)
- coverage (for test coverage reporting)
- optuna (for hyperparameter tuning)

Install all dependencies with:

```bash
pip install -r requirements.txt
```

**Note:**  
The `torch` package in `requirements.txt` is the CPU version of PyTorch.  
If you want to use a GPU, it is recommended to **install the appropriate CUDA-enabled version of PyTorch** for your system **before running** `pip install -r requirements.txt` for a quicker install.  
You can find the correct install command for your system and CUDA version at the [official PyTorch installation page](https://pytorch.org/get-started/locally/).

For example, to install PyTorch with CUDA 11.8 support:

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## Docker Usage

You can run this project in a Docker container for a fully isolated and reproducible environment.

### Build the Docker image

```bash
docker build -t <your-image-name> .
```

### Run the Docker container

```bash
docker run --rm -it <your-image-name>:latest
```

### Notes

- The provided `Dockerfile` uses the `python:3.11-slim` base image for a smaller footprint.
- It explicitly installs the **CPU-only** version of PyTorch to avoid large image sizes. If you need GPU support, modify the Dockerfile and requirements accordingly.
- The `.dockerignore` file is configured to exclude unnecessary files (such as datasets, checkpoints, and virtual environments) from the image. If you add new large files or folders, update `.dockerignore` to keep your image size small.
- If you encounter issues with image size, check that you are not copying large files or using the GPU version of torch by accident.

You can modify the `CMD` in the Dockerfile to run other scripts or pass arguments as needed.

## Testing

- The project includes comprehensive unit tests for all major modules: training, datasets, utility functions, loss visualization, tuning, and model/CLI behavior.
- Tests are written using `pytest` with `coverage` for reporting. Both are required and included in `requirements.txt`
- All unit tests are located in the `tests/` directory.
- To run all tests:
  ```bash
  pytest
  ```
- To check coverage:
  ```bash
  coverage run -m pytest
  coverage report -m
  ```
- You can also run a specific test file, for example:
  ```bash
  pytest tests/test_utils.py
  ```
- Test output will show which tests passed or failed, and coverage will report which lines are tested.
- Coverage includes data processing, plotting, model logic, CLI argument parsing, tuning, and more.
- Current unit test coverage is 98% (544 stmts / 10 miss).

## Future Improvements

- Add temperature scaling for more controllable sampling
- Implement training for transformer model
- Implement transformer model from scratch

## License

This project is licensed under the MIT License. See [LICENSE](https://github.com/Yosna/Multi-Model-AI-Text-Generator/blob/main/LICENSE) for details.
