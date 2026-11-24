from pathlib import Path
from src.pipeline import InvoicePipeline

if __name__ == "__main__":
    base = Path(__file__).parent
    pipeline = InvoicePipeline()
    records = pipeline.run_directory(base / "data" / "invoices", base / "outputs")
    accepted = sum(r.validation.status == "VALID" for r in records)
    print("\n========== RESULTADO FINAL ==========")
    print(f"Faturas processadas: {len(records)}")
    print(f"Aceites: {accepted}")
    print(f"A necessitar de revisão: {len(records) - accepted}")
    print("Ficheiros gerados em: outputs/")
