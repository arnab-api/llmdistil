from dataclasses import dataclass, fields

import numpy as np
import torch
from dataclasses_json import DataClassJsonMixin
from src.models import ModelandTokenizer


@dataclass(frozen=False)
class AttentionInformation(DataClassJsonMixin):
    prompt: str
    tokenized_prompt: list[str]
    attention_matrices: np.ndarray

    def _init__(
        self, prompt: str, tokenized_prompt: list[str], attention_matrices: torch.tensor
    ):
        assert (
            len(tokenized_prompt) == attention_matrices.shape[-1]
        ), "Tokenized prompt and attention matrices must have the same length"
        assert (
            len(attention_matrices.shape) == 4
        ), "Attention matrices must be of shape (layers, heads, tokens, tokens)"
        assert (
            attention_matrices.shape[-1] == attention_matrices.shape[-2]
        ), "Attention matrices must be square"

        self.prompt = prompt
        self.tokenized_prompt = tokenized_prompt
        self.attention_matrices = attention_matrices

    def get_attn_matrix(self, layer: int, head: int) -> torch.tensor:
        return self.attention_matrices[layer, head]


@torch.inference_mode()
def get_attention_matrices(
    prompt: str, mt: ModelandTokenizer, value_weighted: bool = False
) -> torch.tensor:
    """
    Parameters:
        prompt: str, input prompt
        mt: ModelandTokenizer, model and tokenizer
        value_weighted: bool.
            - False => will reuturn attention masks for each key-value pair (after softmax). This is the attention mask actually produced inside the model
            - True => will consider the value matrices to give a sense of the actual contribution of source tokens to the target token residual.
    Returns:
        attention matrices: torch.tensor of shape (layers, heads, tokens, tokens)
    """
    # ! doesn't support batching yet. not really needed in this project
    assert isinstance(prompt, str), "Prompt must be a string"

    inputs = mt.tokenizer(prompt, return_tensors="pt").to(mt.device)
    output = mt.model(
        **inputs, output_attentions=True
    )  # batch_size x n_tokens x vocab_size, only want last token prediction
    attentions = torch.vstack(output.attentions)  # (layers, heads, tokens, tokens)
    if value_weighted:
        values = torch.vstack(
            [output.past_key_values[i][1] for i in range(mt.n_layer)]
        )  # (layers, heads, tokens, head_dim)
        attentions = torch.einsum("abcd,abd->abcd", attentions, values.norm(dim=-1))
    return AttentionInformation(
        prompt=prompt,
        tokenized_prompt=[mt.tokenizer.decode(tok) for tok in inputs.input_ids[0]],
        attention_matrices=attentions.detach().cpu().to(torch.float32).numpy(),
    )
