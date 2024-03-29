import logging
import re
from typing import Any, Callable, Literal, Optional, overload

import baukit
import torch
import transformers

# from mamba_ssm.models.mixer_seq_simple import MambaLMHeadModel as Mamba
# use `mamba-simple`, the official implementation is to messy
from mamba_minimal.model import Mamba

# from mamba_ssm.ops.triton.layernorm import rms_norm_fn
from transformers import AutoModelForCausalLM, AutoTokenizer

logger = logging.getLogger(__name__)


class ModelandTokenizer:
    def __init__(
        self,
        model: Optional[transformers.AutoModel] = None,
        tokenizer: Optional[transformers.AutoTokenizer] = None,
        model_path: Optional[
            str
        ] = "EleutherAI/gpt-j-6B",  # if model is provided, this will be ignored and rewritten
        torch_dtype=torch.float16,
    ) -> None:
        assert (
            model is not None or model_path is not None
        ), "Either model or model_name must be provided"
        if model is not None:
            assert tokenizer is not None, "Tokenizer must be provided with the model"
            self.name = model.config._name_or_path
        else:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            if "mamba" in model_path.lower():
                model = Mamba.from_pretrained(model_path).to(torch_dtype).to("cuda")
                tokenizer = AutoTokenizer.from_pretrained(
                    "EleutherAI/gpt-neox-20b",  # Mamba was trained on the Pile with this exact tokenizer
                )
            else:
                model, tokenizer = (
                    AutoModelForCausalLM.from_pretrained(
                        model_path,
                        low_cpu_mem_usage=True,
                        torch_dtype=torch_dtype,
                    ).to(device),
                    AutoTokenizer.from_pretrained(
                        model_path,
                        # padding_side='left'
                    ),
                )
            tokenizer.pad_token = tokenizer.eos_token
            model.eval()
            logger.info(
                f"loaded model <{model_path}> | size: {get_model_size(model) :.3f} MB | dtype: {torch_dtype} | device: {device}"
            )
            self.name = model_path

        self.model = model
        self.tokenizer = tokenizer
        self.model.eval()
        self.device = next(self.model.parameters()).device

        (
            self.parse_config()
            if isinstance(model, Mamba)
            else self.parse_config(model.config)
        )
        self.cache_forwards()

    def parse_config(self, model_config=None) -> None:
        fields = {
            "n_layer": None,
            "n_embd": None,
            "layer_name_format": None,
            "layer_names": None,
            "embedder_name": None,
            "final_layer_norm_name": None,
            "lm_head_name": None,
        }
        if (
            is_mamba_variant(self.model) or "mamba" in self.name.lower()
        ):  # Not a Transformer
            fields["n_layer"] = len(self.model.layers)
            fields["n_embd"] = self.model.embedding.weight.shape[-1]
            fields["layer_name_format"] = "layers.{}"
            fields["embedder_name"] = "embedding"
            fields["final_layer_norm_name"] = "norm_f"
            fields["lm_head_name"] = "lm_head"
        else:
            fields["attn_module_name_format"] = None
            fields["mlp_module_name_format"] = None
            if is_llama_variant(self.model):
                fields["n_layer"] = model_config.num_hidden_layers
                fields["n_embd"] = model_config.hidden_size
                fields["layer_name_format"] = "model.layers.{}"
                fields["mlp_module_name_format"] = "model.layers.{}.mlp"
                fields["attn_module_name_format"] = "model.layers.{}.self_attn"
                fields["embedder_name"] = "model.embed_tokens"
                fields["final_layer_norm_name"] = "model.norm"
                fields["lm_head_name"] = "model.lm_head"

            elif is_gpt_variant(self.model):
                fields["n_layer"] = model_config.n_layer
                fields["n_embd"] = model_config.n_embd
                fields["layer_name_format"] = "transformer.h.{}"
                fields["mlp_module_name_format"] = "transformer.h.{}.mlp"
                fields["attn_module_name_format"] = "transformer.h.{}.attn"
                fields["embedder_name"] = "transformer.wte"
                fields["final_layer_norm_name"] = "transformer.ln_f"
                fields["lm_head_name"] = "transformer.lm_head"

        if fields["layer_name_format"] is not None and fields["n_layer"] is not None:
            fields["layer_names"] = [
                fields["layer_name_format"].format(i) for i in range(fields["n_layer"])
            ]

        for key, value in fields.items():
            if value is None:
                print(f"!!! Warning: {key} could not be set !!!")
            setattr(self, key, value)

    @property
    def lm_head(self) -> torch.nn.Sequential:
        lm_head = baukit.get_module(self.model, self.lm_head_name)
        ln_f = baukit.get_module(self.model, self.final_layer_norm_name)
        # ln_f = FinalLayerNorm(ln_f, mamba=isinstance(self.model, Mamba))
        return LMHead(final_layer_norm=ln_f, lm_head=lm_head)

    def cache_forwards(self):
        """
        Caches the forward pass of all the modules.
        Usuful to reset the model to its original state after an overwrite.
        """
        self._module_forwards: dict = {}
        for name, module in self.model.named_modules():
            if hasattr(module, "forward"):
                self._module_forwards[name] = module.forward

    def reset_forward(self) -> None:
        """
        Resets the forward pass of all the modules to their original state.
        """
        for name, module in self.model.named_modules():
            if hasattr(module, "forward"):
                module.forward = self._module_forwards[name]


# class FinalLayerNorm(torch.nn.Module):
#     def __init__(self, ln_f: torch.nn.Module, mamba: bool = False):
#         super().__init__()
#         self.ln_f = ln_f
#         self.mamba = mamba

#     def forward(self, x: torch.Tensor, residual=Optional[torch.Tensor]):
#         if self.mamba == False:
#             return self.ln_f(untuple(x))
#         else:
#             if residual is None:
#                 try:
#                     x, residual = x
#                 except:
#                     raise ValueError("x must be a tuple of (x, residual)")
#             return rms_norm_fn(
#                 x=x,
#                 weight=self.ln_f.weight,
#                 bias=self.ln_f.bias,
#                 eps=self.ln_f.eps,
#                 residual=residual,
#                 prenorm=False,
#                 residual_in_fp32=self.ln_f.weight.dtype == torch.float32,
#             )


class LMHead(torch.nn.Module):
    def __init__(self, final_layer_norm: torch.nn.Module, lm_head: torch.nn.Module):
        super().__init__()
        self.lm_head = lm_head
        self.final_layer_norm = final_layer_norm

    def forward(
        self,
        x: torch.Tensor,
        # residual: Optional[torch.Tensor] = None
    ):
        x = self.final_layer_norm(
            x,
            # residual
        )
        return self.lm_head(x)


def get_model_size(
    model: torch.nn.Module, unit: Literal["B", "KB", "MB", "GB"] = "MB"
) -> float:
    param_size = 0
    for param in model.parameters():
        param_size += param.nelement() * param.element_size()
    buffer_size = 0
    for buffer in model.buffers():
        buffer_size += buffer.nelement() * buffer.element_size()

    size_all = param_size + buffer_size
    denom = {"B": 1, "KB": 2**10, "MB": 2**20, "GB": 2**30}[unit]
    return size_all / denom


def unwrap_model(mt: ModelandTokenizer | torch.nn.Module) -> torch.nn.Module:
    if isinstance(mt, ModelandTokenizer):
        return mt.model
    if isinstance(mt, torch.nn.Module):
        return mt
    raise ValueError("mt must be a ModelandTokenizer or a torch.nn.Module")


def unwrap_tokenizer(mt: ModelandTokenizer | AutoTokenizer) -> AutoTokenizer:
    if isinstance(mt, ModelandTokenizer):
        return mt.tokenizer
    return mt


def untuple(object: Any):
    if isinstance(object, tuple):
        return object[0]
    return object


from src.utils.typing import Model, Tokenizer


def maybe_prefix_eos(tokenizer, prompt: str) -> str:
    """Prefix prompt with EOS token if model has no special start token."""
    tokenizer = unwrap_tokenizer(tokenizer)
    if hasattr(tokenizer, "eos_token"):
        prefix = tokenizer.eos_token
        if not prompt.startswith(prefix):
            prompt = prefix + " " + prompt
    return prompt


def is_pythia_variant(model: Model | ModelandTokenizer) -> bool:
    """Determine if model is GPT variant."""
    if isinstance(model, ModelandTokenizer):
        model = unwrap_model(model)
    try:
        return "pythia" in model.config._name_or_path.lower()
    except:
        return False


def is_gpt_variant(mt: Model | ModelandTokenizer) -> bool:
    """Determine if model/tokenizer is GPT variant."""
    if isinstance(mt, ModelandTokenizer):
        mt = unwrap_model(mt)

    # pythia models also have GPTNeoXForCausalLM architecture, but they have slightly  different structure
    # so we need to check for them separately
    if is_pythia_variant(mt):
        return False
    return isinstance(
        mt,
        transformers.GPT2LMHeadModel
        | transformers.GPTJForCausalLM
        | transformers.GPTNeoForCausalLM
        | transformers.GPTNeoXForCausalLM
        | transformers.GPT2TokenizerFast
        | transformers.GPTNeoXTokenizerFast,
    )


def is_llama_variant(mt: Model | ModelandTokenizer) -> bool:
    """Determine if model/tokenizer is GPT variant."""
    if isinstance(mt, ModelandTokenizer):
        mt = unwrap_model(mt)
    if isinstance(mt, transformers.LlamaForCausalLM):
        return True
    if hasattr(mt, "config"):
        config = mt.config
        if hasattr(config, "_name_or_path"):
            name = config._name_or_path
            return "llama" in name.lower() or "mistral" in name.lower()
    return False


def is_mamba_variant(mt: Model | ModelandTokenizer) -> bool:
    """Determine if model/tokenizer is GPT variant."""
    if isinstance(mt, ModelandTokenizer):
        mt = unwrap_model(mt)
    return isinstance(mt, Mamba)


def is_mamba_fast(mt: ModelandTokenizer) -> bool:
    """Determine if model/tokenizer is GPT variant."""
    if isinstance(mt, ModelandTokenizer):
        mt = unwrap_model(mt)
    return is_mamba_variant(mt) and hasattr(mt, "backbone")


def any_parameter(model: ModelandTokenizer | Model) -> torch.nn.Parameter | None:
    """Get any example parameter for the model."""
    model = unwrap_model(model)
    return next(iter(model.parameters()), None)


def determine_embedding_layer_path(model: ModelandTokenizer | Model) -> str:
    model = unwrap_model(model)
    if is_gpt_variant(model):
        return "transformer.wte"
    elif isinstance(model, transformers.LlamaForCausalLM):
        return "model.embed_tokens"
    elif isinstance(model, Mamba):
        prefix = "backbone." if hasattr(model, "backbone") else ""
        return prefix + "embedding"
    elif is_pythia_variant(model):
        return "gpt_neox.embed_in"
    else:
        raise ValueError(f"unknown model type: {type(model).__name__}")


def determine_final_layer_norm_path(model: ModelandTokenizer | Model) -> str:
    model = unwrap_model(model)
    if is_gpt_variant(model):
        return "transformer.ln_f"
    elif isinstance(model, transformers.LlamaForCausalLM):
        return "model.norm"
    elif isinstance(model, Mamba):
        prefix = "backbone." if hasattr(model, "backbone") else ""
        return prefix + "norm_f"
    elif is_pythia_variant(model):
        return "gpt_neox.final_layer_norm"
    else:
        raise ValueError(f"unknown model type: {type(model).__name__}")


def determine_lm_head_path(model: ModelandTokenizer | Model) -> str:
    model = unwrap_model(model)
    if is_gpt_variant(model):
        return "lm_head"
    elif isinstance(model, transformers.LlamaForCausalLM):
        return "model.lm_head"
    elif isinstance(model, Mamba):
        return "lm_head"
    elif is_pythia_variant(model):
        return "embed_out"
    else:
        raise ValueError(f"unknown model type: {type(model).__name__}")


def determine_layers(model: ModelandTokenizer | Model) -> tuple[int, ...]:
    """Return all hidden layer names for the given model."""
    model = unwrap_model(model)
    assert isinstance(model, Model)

    if isinstance(
        model, transformers.GPTNeoXForCausalLM | transformers.LlamaForCausalLM
    ):
        n_layer = model.config.num_hidden_layers
    elif isinstance(model, Mamba):
        n_layer = (
            len(model.backbone.layers)
            if hasattr(model, "backbone")
            else len(model.layers)
        )
    else:
        n_layer = model.config.n_layer

    return (*range(n_layer),)


from src.utils.typing import Layer, Sequence


@overload
def determine_layer_paths(
    model: ModelandTokenizer | Model,
    layers: Optional[Sequence[Layer]] = ...,
    *,
    return_dict: Literal[False] = ...,
) -> Sequence[str]:
    """Determine layer path for each layer."""
    ...


@overload
def determine_layer_paths(
    model: ModelandTokenizer | Model,
    layers: Optional[Sequence[Layer]] = ...,
    *,
    return_dict: Literal[True],
) -> dict[Layer, str]:
    """Determine mapping from layer to layer path."""
    ...


def determine_layer_paths(
    model: ModelandTokenizer | Model,
    layers: Optional[Sequence[Layer]] = None,
    *,
    return_dict: bool = False,
) -> Sequence[str] | dict[Layer, str]:
    """Determine the absolute paths to the given layers in the model.

    Args:
        model: The model.
        layers: The specific layer (numbers/"emb") to look at. Defaults to all of them.
            Can be a negative number.
        return_dict: If True, return mapping from layer to layer path,
            otherwise just return list of layer paths in same order as `layers`.

    Returns:
        Mapping from layer number to layer path.

    """
    model = unwrap_model(model)

    if layers is None:
        layers = determine_layers(model)

    assert isinstance(model, Model), type(model)

    layer_paths: dict[Layer, str] = {}
    for layer in layers:
        if layer == "emb":
            layer_paths[layer] = determine_embedding_layer_path(model)
            continue
        if layer == "ln_f":
            layer_paths[layer] = determine_final_layer_norm_path(model)
            continue

        layer_index = layer
        if layer_index < 0:
            layer_index = len(determine_layers(model)) + layer

        if isinstance(model, transformers.GPTNeoXForCausalLM):
            layer_path = f"gpt_neox.layers.{layer_index}"
        elif isinstance(model, transformers.LlamaForCausalLM):
            layer_path = f"model.layers.{layer_index}"
        elif isinstance(model, Mamba):
            prefix = "backbone." if hasattr(model, "backbone") else ""
            layer_path = prefix + f"layers.{layer_index}"
        else:
            layer_path = f"transformer.h.{layer_index}"
        layer_paths[layer] = layer_path

    return layer_paths if return_dict else tuple(layer_paths[la] for la in layers)


def determine_hidden_size(model: ModelandTokenizer | Model) -> int:
    """Determine hidden rep size for the model."""
    model = unwrap_model(model)

    if isinstance(model, Mamba):
        prefix = "backbone." if hasattr(model, "backbone") else ""
        embed = baukit.get_module(model, prefix + "embedding")
        return embed.weight.shape[-1]

    return model.config.hidden_size


def determine_device(model: ModelandTokenizer | Model) -> torch.device | None:
    """Determine device model is running on."""
    parameter = any_parameter(model)
    return parameter.device if parameter is not None else None


def determine_dtype(model: ModelandTokenizer | Model) -> torch.dtype | None:
    """Determine dtype of model."""
    parameter = any_parameter(model)
    return parameter.dtype if parameter is not None else None
