import re
from pathlib import Path
from ..models import Invoice
from ..llm import LLMClient

SYSTEM_PROMPT = """És um agente de extração de faturas. Extrai apenas informação explicitamente presente.
Não inventes valores. Se um campo não estiver presente, usa null.
Responde apenas com JSON válido com estas chaves:
supplier, invoice_number, date (YYYY-MM-DD quando possível), currency,
lines (lista de {description, quantity, unit_price, line_total}),
subtotal, tax, total, extraction_notes (lista de strings).
Os valores monetários e quantidades devem ser números, não texto."""

class ExtractionAgent:
    def __init__(self, llm: LLMClient, logger):
        self.llm, self.logger = llm, logger

    def run(self, text: str, source_name: str = "") -> Invoice:
        self.logger.info("Agente 1 (Extrator) recebeu %s", source_name)
        if self.llm.enabled:
            try:
                data = self.llm.json_completion(SYSTEM_PROMPT, text)
                invoice = Invoice.from_dict(data)
                self.logger.info("Agente 1 extraiu os dados de %s via LLM", source_name)
                return invoice
            except Exception as exc:
                self.logger.exception("Falha LLM na extração; será usado parser local: %s", exc)
        invoice = self._fallback_parse(text)
        self.logger.info("Agente 1 extraiu os dados de %s via parser local", source_name)
        return invoice

    def _fallback_parse(self, text: str) -> Invoice:
        def field(pattern, cast=str):
            match = re.search(pattern, text, re.I | re.M)
            if not match:
                return None
            value = match.group(1).strip()
            try:
                return cast(value.replace(",", "."))
            except (ValueError, TypeError):
                return None

        supplier = field(r"^Fornecedor:\s*(.+)$")
        number = field(r"^Fatura:\s*(.+)$")
        date = field(r"^Data:\s*(\d{4}-\d{2}-\d{2})$")
        subtotal = field(r"^Subtotal:\s*([0-9]+(?:[.,][0-9]{1,2})?)$", float)
        tax = field(r"^Imposto:\s*([0-9]+(?:[.,][0-9]{1,2})?)$", float)
        total = field(r"^Total:\s*([0-9]+(?:[.,][0-9]{1,2})?)$", float)
        lines = []
        for row in re.findall(r"^Linha:\s*(.+?)\s*\|\s*([0-9.,]+)\s*\|\s*([0-9.,]+)\s*\|\s*([0-9.,]+)\s*$",
                              text, re.I | re.M):
            desc, qty, unit, amount = row
            lines.append({
                "description": desc.strip(),
                "quantity": float(qty.replace(",", ".")),
                "unit_price": float(unit.replace(",", ".")),
                "line_total": float(amount.replace(",", ".")),
            })
        return Invoice.from_dict({
            "supplier": supplier, "invoice_number": number, "date": date,
            "lines": lines, "subtotal": subtotal, "tax": tax, "total": total,
            "currency": "EUR", "extraction_notes": ["Extração por parser local de demonstração"],
        })
