import json
from ..llm import LLMClient

SYSTEM_PROMPT = """És um agente de tratamento de exceções de faturas.
Analisa evidências, mas nunca inventes nem alteres silenciosamente valores.
Só propõe correção quando a evidência textual é explícita e inequívoca.
Se não for seguro corrigir, recomenda revisão humana.
Devolve JSON com: assessment, possible_corrections (lista), human_review (boolean),
reasoning (string). Uma proposta não é uma correção aplicada."""

class ExceptionAgent:
    def __init__(self, llm: LLMClient, logger):
        self.llm, self.logger = llm, logger

    def run(self, original_text: str, invoice: dict, errors: list[str]) -> dict:
        self.logger.info("Agente 2 (Exceções) analisa %d problema(s)", len(errors))
        if self.llm.enabled:
            try:
                result = self.llm.json_completion(
                    SYSTEM_PROMPT,
                    json.dumps({"original_invoice": original_text, "extracted_data": invoice,
                                "validation_errors": errors}, ensure_ascii=False)
                )
                result.setdefault("possible_corrections", [])
                result.setdefault("human_review", True)
                return result
            except Exception as exc:
                self.logger.exception("Falha no Agente 2: %s", exc)
        return {
            "assessment": "Foram encontrados problemas que exigem análise.",
            "possible_corrections": [],
            "human_review": True,
            "reasoning": "Modo local: não foi aplicada qualquer correção automática; é necessária confirmação humana."
        }
