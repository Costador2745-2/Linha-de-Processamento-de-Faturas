import json
from pathlib import Path
from dataclasses import asdict
from .llm import LLMClient
from .logger_config import configure_logging
from .agents.extractor import ExtractionAgent
from .agents.exception_handler import ExceptionAgent
from .agents.reporter import ReporterAgent
from .validator import InvoiceValidator
from .models import ProcessingRecord

class InvoicePipeline:
    def __init__(self):
        self.logger = configure_logging()
        self.llm = LLMClient()
        self.extractor = ExtractionAgent(self.llm, self.logger)
        self.validator = InvoiceValidator(self.logger)
        self.exception_agent = ExceptionAgent(self.llm, self.logger)
        self.reporter = ReporterAgent(self.llm, self.logger)

    def process_file(self, path: Path) -> ProcessingRecord:
        text = path.read_text(encoding="utf-8")
        invoice = self.extractor.run(text, path.name)
        validation = self.validator.validate(invoice)
        exception_analysis = None
        if validation.errors:
            exception_analysis = self.exception_agent.run(text, invoice.to_dict(), validation.errors)
        record = ProcessingRecord(path.name, invoice, validation, exception_analysis)
        record.report = self.reporter.run(record)
        return record

    def run_directory(self, input_dir: Path, output_dir: Path):
        output_dir.mkdir(parents=True, exist_ok=True)
        paths = sorted(input_dir.glob("*.txt"))
        records = [self.process_file(path) for path in paths]
        serializable = []
        for r in records:
            serializable.append({
                "source_file": r.source_file,
                "invoice": r.invoice.to_dict(),
                "validation": asdict(r.validation),
                "exception_analysis": r.exception_analysis,
                "report": r.report,
            })
        (output_dir / "results.json").write_text(
            json.dumps(serializable, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        self._write_csv(records, output_dir / "results.csv")
        report = self._summary(records)
        (output_dir / "accounting_report.md").write_text(report, encoding="utf-8")
        return records

    @staticmethod
    def _write_csv(records, path):
        import csv
        with path.open("w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["Ficheiro", "Fornecedor", "N.º fatura", "Data", "Subtotal",
                             "Imposto", "Total", "Estado", "Problemas", "Revisão humana"])
            for r in records:
                writer.writerow([
                    r.source_file, r.invoice.supplier, r.invoice.invoice_number, r.invoice.date,
                    r.invoice.subtotal, r.invoice.tax, r.invoice.total, r.validation.status,
                    " | ".join(r.validation.errors),
                    (r.exception_analysis or {}).get("human_review", False)
                ])

    @staticmethod
    def _summary(records):
        accepted = sum(r.validation.status == "VALID" for r in records)
        review = len(records) - accepted
        lines = ["# Relatório de processamento de faturas", "",
                 f"- Faturas processadas: **{len(records)}**",
                 f"- Aceites: **{accepted}**",
                 f"- A necessitar de revisão: **{review}**", "",
                 "## Resultado por fatura", ""]
        for r in records:
            lines += [f"### {r.source_file}", r.report, ""]
            for error in r.validation.errors:
                lines.append(f"- Problema: {error}")
            if r.exception_analysis:
                lines.append(f"- Revisão humana: {r.exception_analysis.get('human_review', True)}")
        lines += ["", "> Nota: uma proposta de correção não equivale a uma correção aplicada."]
        return "\n".join(lines)
