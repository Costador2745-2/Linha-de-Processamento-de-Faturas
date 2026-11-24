from ..llm import LLMClient

SYSTEM_PROMPT = """És um agente de reporting para contabilidade.
Escreve um resumo curto e fiel aos dados recebidos. Distingue faturas válidas de faturas
que precisam de revisão. Nunca afirmes que uma correção foi aplicada se apenas foi sugerida."""

class ReporterAgent:
    def __init__(self, llm: LLMClient, logger):
        self.llm, self.logger = llm, logger

    def run(self, record) -> str:
        self.logger.info("Agente 3 (Reporter) cria relatório para %s", record.source_file)
        payload = {
            "file": record.source_file,
            "invoice": record.invoice.to_dict(),
            "validation": {
                "status": record.validation.status,
                "errors": record.validation.errors,
                "warnings": record.validation.warnings,
            },
            "exception_analysis": record.exception_analysis,
        }
        if self.llm.enabled:
            try:
                import json
                return self.llm.text_completion(SYSTEM_PROMPT, json.dumps(payload, ensure_ascii=False))
            except Exception as exc:
                self.logger.exception("Falha no Reporter; será usado resumo local: %s", exc)
        if record.validation.status == "VALID":
            return f"{record.source_file}: fatura aceite. Não foram detetadas inconsistências."
        reasons = " ".join(record.validation.errors)
        human = (record.exception_analysis or {}).get("human_review", True)
        return f"{record.source_file}: fatura necessita de revisão humana ({'sim' if human else 'não'}). Problemas: {reasons}"
