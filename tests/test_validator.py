from src.models import Invoice, InvoiceLine
from src.validator import InvoiceValidator

class DummyLogger:
    def info(self, *args, **kwargs): pass

def test_valid_invoice():
    validator = InvoiceValidator(DummyLogger())
    invoice = Invoice("Loja A", "A-001", "2026-10-01",
                      [InvoiceLine("Papel", 2, 5, 10)], 10, 2.3, 12.3)
    assert validator.validate(invoice).status == "VALID"

def test_total_mismatch():
    validator = InvoiceValidator(DummyLogger())
    invoice = Invoice("Loja A", "A-002", "2026-10-01",
                      [InvoiceLine("Papel", 2, 5, 10)], 10, 2.3, 15)
    result = validator.validate(invoice)
    assert result.status == "NEEDS_REVIEW"
    assert any("Total inconsistente" in e for e in result.errors)

def test_duplicate_invoice_number():
    validator = InvoiceValidator(DummyLogger())
    first = Invoice("Loja A", "DUP-1", "2026-10-01", [], 10, 2.3, 12.3)
    second = Invoice("Loja B", "DUP-1", "2026-10-02", [], 10, 2.3, 12.3)
    validator.validate(first)
    result = validator.validate(second)
    assert any("duplicado" in e for e in result.errors)
