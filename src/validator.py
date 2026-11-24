from datetime import date
from . import models

class InvoiceValidator:
    """Validador determinístico: não utiliza IA para decidir regras de negócio."""
    def __init__(self, logger, tolerance: float = 0.02):
        self.logger, self.tolerance = logger, tolerance
        self.seen_invoice_numbers = set()

    def validate(self, invoice: models.Invoice) -> models.ValidationResult:
        errors, warnings = [], []
        required = {
            "fornecedor": invoice.supplier,
            "número da fatura": invoice.invoice_number,
            "data": invoice.date,
            "subtotal": invoice.subtotal,
            "imposto": invoice.tax,
            "total": invoice.total,
        }
        for label, value in required.items():
            if value is None or value == "":
                errors.append(f"Campo obrigatório em falta: {label}.")

        if invoice.date:
            try:
                date.fromisoformat(invoice.date)
            except ValueError:
                errors.append(f"Data inválida: {invoice.date}.")

        if invoice.invoice_number:
            if invoice.invoice_number in self.seen_invoice_numbers:
                errors.append(f"Número de fatura duplicado: {invoice.invoice_number}.")
            else:
                self.seen_invoice_numbers.add(invoice.invoice_number)

        if invoice.lines:
            if any(line.line_total is None for line in invoice.lines):
                errors.append("Uma ou mais linhas não têm valor total.")
            else:
                lines_sum = sum(line.line_total for line in invoice.lines)
                if invoice.subtotal is not None and abs(lines_sum - invoice.subtotal) > self.tolerance:
                    errors.append(
                        f"Soma das linhas ({lines_sum:.2f}) diferente do subtotal ({invoice.subtotal:.2f})."
                    )
        else:
            warnings.append("A fatura não contém linhas de detalhe identificadas.")

        if invoice.subtotal is not None and invoice.tax is not None and invoice.total is not None:
            expected = invoice.subtotal + invoice.tax
            if abs(expected - invoice.total) > self.tolerance:
                errors.append(
                    f"Total inconsistente: subtotal + imposto = {expected:.2f}, mas total = {invoice.total:.2f}."
                )

        status = "VALID" if not errors else "NEEDS_REVIEW"
        self.logger.info("Validador: estado=%s, erros=%d, avisos=%d", status, len(errors), len(warnings))
        return models.ValidationResult(status=status, errors=errors, warnings=warnings)
