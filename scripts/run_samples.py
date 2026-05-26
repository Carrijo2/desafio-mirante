import json
from pathlib import Path

from app.graph.modernization_graph import run_modernization

ROOT = Path(__file__).resolve().parents[1]
SAMPLES = ROOT / "app" / "samples"
OUTPUTS = ROOT / "outputs" / "annexes"


def main() -> None:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    schema_context = (SAMPLES / "schema.sql").read_text(encoding="utf-8")

    for sql_file in sorted(SAMPLES.glob("annex_*.sql")):
        state = run_modernization(
            source_code=sql_file.read_text(encoding="utf-8"),
            schema_context=schema_context,
            metadata={"sample": sql_file.stem},
        )
        target_dir = OUTPUTS / sql_file.stem
        target_dir.mkdir(parents=True, exist_ok=True)
        (target_dir / "generated.py").write_text(
            state.get("generated_code") or "",
            encoding="utf-8",
        )
        (target_dir / "report.json").write_text(
            json.dumps(state.get("report", {}), indent=2, ensure_ascii=True),
            encoding="utf-8",
        )
        print(f"{sql_file.name}: {state.get('status')}")


if __name__ == "__main__":
    main()
