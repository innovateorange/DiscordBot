# t5_router.py  (full file, replace the old one)
import json, re
from transformers import T5Tokenizer, T5ForConditionalGeneration
import torch

OPTIONAL_KEYS = ["role", "type", "date", "company", "location"]

class T5CommandRouter:
    """
    Turn free‑form job queries into a params dict:
      {"role": "...", "type": "...", ...}
    Missing fields are simply absent.
    """
    def __init__(self, model_name: str = "t5-small"):
        self.tok   = T5Tokenizer.from_pretrained(model_name)
        self.model = T5ForConditionalGeneration.from_pretrained(model_name)

    @torch.inference_mode()
    def route(self, text: str) -> dict:
        prompt = (
            "Extract job-search parameters from the sentence below and output ONLY "
            "a valid JSON object using any of these optional keys: "
            f'{", ".join(OPTIONAL_KEYS)}.\n\nSentence: {text}'
        )

        ids   = self.tok(prompt, return_tensors="pt", truncation=True)
        reply = self.model.generate(**ids, max_length=128)
        out   = self.tok.decode(reply[0], skip_special_tokens=True)

        match   = re.search(r"\{.*\}", out, flags=re.S)
        params  = json.loads(match.group(0)) if match else {}

        # keep only allowed keys & drop empties
        return {k: v for k, v in params.items() if k in OPTIONAL_KEYS and v}
