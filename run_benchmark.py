from __future__ import annotations

import json
from pathlib import Path

import typer
from rich import print

from src.reflexion_lab.agents import ReActAgent, ReflexionAgent
from src.reflexion_lab.reporting import build_report, save_report
from src.reflexion_lab.schemas import QAExample
from src.reflexion_lab.utils import load_dataset, save_jsonl

app = typer.Typer(add_completion=False)


def run_split(
    examples: list[QAExample],
    split_name: str,
    base_out_dir: Path,
    dataset_name: str,
    reflexion_attempts: int,
) -> dict:
    split_out_dir = base_out_dir / split_name
    split_out_dir.mkdir(parents=True, exist_ok=True)

    react = ReActAgent()
    reflexion = ReflexionAgent(max_attempts=reflexion_attempts)

    react_records = [react.run(example) for example in examples]
    reflexion_records = [reflexion.run(example) for example in examples]
    all_records = react_records + reflexion_records

    save_jsonl(split_out_dir / "react_runs.jsonl", react_records)
    save_jsonl(split_out_dir / "reflexion_runs.jsonl", reflexion_records)

    report = build_report(
        all_records,
        dataset_name=f"{dataset_name}::{split_name}",
        mode="ollama",
    )
    json_path, md_path = save_report(report, split_out_dir)

    print(f"[green]Saved[/green] {json_path}")
    print(f"[green]Saved[/green] {md_path}")

    return report.summary


@app.command()
def main(
    dataset: str = "data/hotpot_mini.json",
    out_dir: str = "outputs/sample_run",
    reflexion_attempts: int = 3,
) -> None:
    examples = load_dataset(dataset)
    dataset_name = Path(dataset).name
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    easy_examples = [e for e in examples if e.difficulty == "easy"]
    medium_examples = [e for e in examples if e.difficulty == "medium"]
    hard_examples = [e for e in examples if e.difficulty == "hard"]

    summaries: dict[str, dict] = {}

    # Report tổng tất cả dataset
    summaries["all"] = run_split(
        examples=examples,
        split_name="all",
        base_out_dir=out_path,
        dataset_name=dataset_name,
        reflexion_attempts=reflexion_attempts,
    )

    # Report cho từng độ khó
    if easy_examples:
        summaries["easy"] = run_split(
            examples=easy_examples,
            split_name="easy",
            base_out_dir=out_path,
            dataset_name=dataset_name,
            reflexion_attempts=reflexion_attempts,
        )

    if medium_examples:
        summaries["medium"] = run_split(
            examples=medium_examples,
            split_name="medium",
            base_out_dir=out_path,
            dataset_name=dataset_name,
            reflexion_attempts=reflexion_attempts,
        )

    if hard_examples:
        summaries["hard"] = run_split(
            examples=hard_examples,
            split_name="hard",
            base_out_dir=out_path,
            dataset_name=dataset_name,
            reflexion_attempts=reflexion_attempts,
        )

    print("\n[bold cyan]Benchmark summaries by split[/bold cyan]")
    print(json.dumps(summaries, indent=2))


if __name__ == "__main__":
    app()