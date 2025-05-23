import torch
import torch.nn as nn
import torch.nn.functional as F
import os


class BaseLanguageModel(nn.Module):
    """
    Base class for all language models in the project.

    This abstract base class provides common functionality for language models:
    - Device management (CPU/GPU)
    - Checkpoint handling
    - Loss computation
    - Token generation

    All specific language model implementations should inherit from this class.
    """

    def __init__(self, vocab_size: int, model_name: str) -> None:
        """
        Initialize the base language model.

        Args:
            vocab_size: Size of the vocabulary (number of unique tokens)
            model_name: Name of the model, used for checkpoint paths
        """
        super().__init__()
        self.name = model_name
        self.dir_path = os.path.join("checkpoints", model_name)
        self.plot_dir = os.path.join("plots", model_name)
        self.ckpt_dir = os.path.join(self.dir_path, "checkpoint_1")
        self.ckpt_path = os.path.join(self.ckpt_dir, "checkpoint.pt")
        self.meta_path = os.path.join(self.ckpt_dir, "metadata.json")
        self.cfg_path = "config.json"

        # Automatically use GPU if available
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.vocab_size = vocab_size

    def compute_loss(
        self,
        idx: torch.Tensor,
        logits: torch.Tensor,
        targets: torch.Tensor | None = None,
        loss: torch.Tensor | None = None,
    ):
        """
        Compute the cross entropy loss between model predictions and targets.

        Args:
            B: batch size, T: sequence length, C: vocabulary size
            idx: Input token indices of shape (B, T)
            logits: Model predictions of shape (B, T, C)
            targets: Target token indices of shape (B, T), optional
            loss: Pre-computed loss tensor, optional

        Returns:
            tuple: (logits, loss) where loss is None if no targets are provided
        """
        B, T = idx.shape

        if targets is not None:
            # Reshape for cross entropy: (B,T,C) -> (B*T,C)
            # This flattens the batch and sequence dimensions
            # A single prediction per token is received
            logits = logits.view(B * T, -1)
            targets = targets.view(B * T)
            loss = F.cross_entropy(logits, targets)

        return logits, loss

    def new_token(self, logits: torch.Tensor) -> torch.Tensor:
        """
        Generate the next token in the sequence using the model's predictions.

        Args:
            logits: Model predictions of shape (B, T, C) where:
                B: batch size
                T: sequence length
                C: vocabulary size

        Returns:
            torch.Tensor: Next token index of shape (B, 1)
        """
        # Focus on the last time step
        logits = logits[:, -1, :]
        # Convert logits to probabilities
        probs = F.softmax(logits, dim=-1)
        # Sample from the probability distribution
        next_idx = torch.multinomial(probs, num_samples=1)

        return next_idx
