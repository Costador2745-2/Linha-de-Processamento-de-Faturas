import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()

class LLMClient:
    """Cliente para Ollama local. Não requer chave API nem serviço pago."""
    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "ollama").lower().strip()
        self.base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
        self.model = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
        self.timeout = int(os.getenv("LLM_TIMEOUT", "180"))

    @property
    def enabled(self) -> bool:
        return self.provider == "ollama"

    def _generate(self, system_prompt: str, user_prompt: str, json_mode: bool = False):
        if not self.enabled:
            raise RuntimeError("LLM_PROVIDER não está configurado para ollama")
        payload = {
            "model": self.model,
            "stream": False,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "options": {"temperature": 0}
        }
        if json_mode:
            payload["format"] = "json"
        try:
            response = requests.post(
                f"{self.base_url}/api/chat", json=payload, timeout=self.timeout
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise RuntimeError(
                "Não foi possível contactar o Ollama. Confirme que está instalado, "
                "em execução e que descarregou o modelo com 'ollama pull llama3.2:3b'."
            ) from exc
        content = response.json().get("message", {}).get("content", "")
        if not content:
            raise RuntimeError("Ollama devolveu uma resposta vazia.")
        return content

    def json_completion(self, system_prompt: str, user_prompt: str) -> dict:
        content = self._generate(system_prompt, user_prompt, json_mode=True)
        try:
            return json.loads(content)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"O modelo não devolveu JSON válido: {content[:300]}") from exc

    def text_completion(self, system_prompt: str, user_prompt: str) -> str:
        return self._generate(system_prompt, user_prompt, json_mode=False)
