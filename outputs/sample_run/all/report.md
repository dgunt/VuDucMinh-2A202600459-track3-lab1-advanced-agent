# Lab 16 Benchmark Report

## Metadata
- Dataset: hotpot_mini.json::all
- Mode: ollama
- Records: 16
- Agents: react, reflexion

## Summary
| Metric | ReAct | Reflexion | Delta |
|---|---:|---:|---:|
| EM | 0.875 | 1.0 | 0.125 |
| Avg attempts | 1 | 1.125 | 0.125 |
| Avg token estimate | 395.75 | 470.88 | 75.13 |
| Avg latency (ms) | 13358.88 | 16259.5 | 2900.62 |

## Failure modes
```json
{
  "react": {
    "none": 7,
    "entity_drift": 1
  },
  "reflexion": {
    "none": 8
  }
}
```

## Extensions implemented
- structured_evaluator
- reflection_memory
- benchmark_report_json

## Discussion
Reflexion improved exact match by allowing the agent to inspect failed attempts and retry with reflection memory. The largest gains appeared in multi-hop cases where the first attempt stopped too early or selected the wrong second-hop entity. The trade-off was higher token usage and latency due to additional evaluator and reflector calls. On a local Ollama setup, this overhead was measurable but acceptable for benchmarking. A larger benchmark on at least 100 HotpotQA examples is still needed to validate whether the improvement generalizes beyond the mini dataset.
