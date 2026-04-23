# Lab 16 Benchmark Report

## Metadata
- Dataset: hotpot_mini.json::hard
- Mode: ollama
- Records: 4
- Agents: react, reflexion

## Summary
| Metric | ReAct | Reflexion | Delta |
|---|---:|---:|---:|
| EM | 0.5 | 1.0 | 0.5 |
| Avg attempts | 1 | 2 | 1 |
| Avg token estimate | 395.5 | 1327 | 931.5 |
| Avg latency (ms) | 15135.5 | 49454 | 34318.5 |

## Failure modes
```json
{
  "react": {
    "entity_drift": 1,
    "none": 1
  },
  "reflexion": {
    "none": 2
  }
}
```

## Extensions implemented
- structured_evaluator
- reflection_memory
- benchmark_report_json

## Discussion
Reflexion improved exact match by allowing the agent to inspect failed attempts and retry with reflection memory. The largest gains appeared in multi-hop cases where the first attempt stopped too early or selected the wrong second-hop entity. The trade-off was higher token usage and latency due to additional evaluator and reflector calls. On a local Ollama setup, this overhead was measurable but acceptable for benchmarking. A larger benchmark on at least 100 HotpotQA examples is still needed to validate whether the improvement generalizes beyond the mini dataset.
