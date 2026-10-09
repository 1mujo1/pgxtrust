"""Answer backends. Each backend turns a rendered prompt into a raw reply string.

* ``OracleBackend`` - answers with the gold letter. Used only for dry runs: it proves the pipeline
  (rendering, retrieval, parsing, scoring, logging) without any model or cost. It must score 100%.
* ``RandomBackend`` - seeded uniform guess. Dry-run sanity check: should score about 25%.
* ``ClaudeBackend`` - Anthropic API (requires ANTHROPIC_API_KEY; ``pip install anthropic``).
* ``LlamaBackend`` - Hugging Face transformers, greedy decoding (run on Colab GPU).

Heavy libraries are imported lazily so tests and dry runs need neither.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from .items import Item
from .prompts import LETTERS


@dataclass
class Reply:
    text: str
    error: str = ""  # API/transport failure after retries; NOT scored
    refusal: bool = False  # the model declined; scored as wrong, reported separately


class OracleBackend:
    name = "oracle"
    model_id = "oracle"

    def answer(self, prompt: str, item: Item) -> Reply:
        return Reply(LETTERS[item.gold_index])


class RandomBackend:
    name = "random"
    model_id = "random"

    def __init__(self, seed: int = 20261009):
        self.rng = random.Random(seed)

    def answer(self, prompt: str, item: Item) -> Reply:
        return Reply(LETTERS[self.rng.randrange(len(item.options))])


class ClaudeBackend:
    """Claude via the Anthropic Messages API.

    Decoding notes (Claude Sonnet 5.5): sampling parameters such as temperature are rejected, so
    reproducibility rests on the pinned model ID. Thinking is turned off with
    ``{"type": "between_tools"}`` at low effort, because answers are a single letter.
    No server-side model fallback is enabled: a fallback would mix another model's answers into
    this model's results. Refusals are recorded as refusals.
    """

    name = "claude"

    def __init__(self, model_id: str = "claude-sonnet-5-5", max_tokens: int = 16):
        import anthropic  # lazy: only needed for real runs

        self.anthropic = anthropic
        self.client = anthropic.Anthropic(max_retries=4)
        self.model_id = model_id
        self.max_tokens = max_tokens

    def answer(self, prompt: str, item: Item) -> Reply:
        try:
            response = self.client.messages.create(
                model=self.model_id,
                max_tokens=self.max_tokens,
                thinking={"type": "between_tools"},
                output_config={"effort": "low"},
                messages=[{"role": "user", "content": prompt}],
            )
        except (self.anthropic.RateLimitError, self.anthropic.APIConnectionError) as err:
            return Reply("", error=f"{type(err).__name__}: {err}")
        except self.anthropic.APIStatusError as err:
            return Reply("", error=f"{type(err).__name__} {err.status_code}: {err.message}")
        if response.stop_reason == "refusal":
            return Reply("", refusal=True)
        text = "".join(b.text for b in response.content if b.type == "text")
        return Reply(text)


class LlamaBackend:
    """Local Hugging Face model with greedy decoding (deterministic). Needs a GPU + HF token."""

    name = "llama"

    def __init__(self, model_id: str = "meta-llama/Llama-3.1-8B-Instruct",
                 max_new_tokens: int = 5, quant: str = "none"):
        """quant='4bit' loads with bitsandbytes NF4 so the 8B model fits a free Colab T4
        (~15 GB). This is a declared deviation: it is recorded in model_id and run settings."""
        import torch  # lazy
        from transformers import AutoModelForCausalLM, AutoTokenizer

        self.torch = torch
        self.model_id = model_id + ("-4bit" if quant == "4bit" else "")
        self.max_new_tokens = max_new_tokens
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        if quant == "4bit":
            from transformers import BitsAndBytesConfig

            config = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                                        bnb_4bit_compute_dtype=torch.float16)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_id, quantization_config=config, device_map="auto"
            )
        elif quant == "none":
            self.model = AutoModelForCausalLM.from_pretrained(
                model_id, torch_dtype=torch.bfloat16, device_map="auto"
            )
        else:
            raise ValueError(f"unknown quant {quant!r}")

    def answer(self, prompt: str, item: Item) -> Reply:
        messages = [{"role": "user", "content": prompt}]
        inputs = self.tokenizer.apply_chat_template(
            messages, add_generation_prompt=True, return_tensors="pt"
        ).to(self.model.device)
        with self.torch.no_grad():
            out = self.model.generate(
                inputs, max_new_tokens=self.max_new_tokens, do_sample=False,
                pad_token_id=self.tokenizer.eos_token_id,
            )
        return Reply(self.tokenizer.decode(out[0, inputs.shape[1]:], skip_special_tokens=True))


def make_backend(name: str, model_id: str | None = None, quant: str = "none"):
    if name == "oracle":
        return OracleBackend()
    if name == "random":
        return RandomBackend()
    if name == "claude":
        return ClaudeBackend(model_id or "claude-sonnet-5-5")
    if name == "llama":
        return LlamaBackend(model_id or "meta-llama/Llama-3.1-8B-Instruct", quant=quant)
    raise ValueError(f"unknown backend {name!r}")
