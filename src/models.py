from dataclasses import dataclass, field, asdict
from typing import Any

@dataclass
class InvoiceLine:
    description: str
    quantity: float | None
    unit_price: float | None
    line_total: float | None

@dataclass
class Invoice:
    supplier: str | None
    invoice_number: str | None
    date: str | None
    lines: list[InvoiceLine] = field(default_factory=list)
    subtotal: float | None = None
    tax: float | None = None
    total: float | None = None
    currency: str = "EUR"
    extraction_notes: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Invoice":
        lines = [InvoiceLine(**line) for line in data.get("lines", [])]
        allowed = {k: data.get(k) for k in
                   ("supplier", "invoice_number", "date", "subtotal", "tax", "total", "currency")}
        allowed["lines"] = lines
        allowed["extraction_notes"] = data.get("extraction_notes", [])
        return cls(**allowed)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass
class ValidationResult:
    status: str
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

@dataclass
class ProcessingRecord:
    source_file: str
    invoice: Invoice
    validation: ValidationResult
    exception_analysis: dict[str, Any] | None = None
    report: str = ""
