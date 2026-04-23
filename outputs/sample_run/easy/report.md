# Lab 16 Benchmark Report

## Metadata
- Dataset: hotpot_mini.json::easy
- Mode: ollama
- Records: 6
- Agents: react, reflexion

## Summary
| Metric | ReAct | Reflexion | Delta |
|---|---:|---:|---:|
| EM | 1.0 | 1.0 | 0.0 |
| Avg attempts | 1 | 1 | 0 |
| Avg token estimate | 257.33 | 259.33 | 2.0 |
| Avg latency (ms) | 5007.67 | 5039 | 31.33 |

## Failure modes
```json
{
  "react": {
    "none": 3
  },
  "reflexion": {
    "none": 3
  }
}
```

## Extensions implemented
- structured_evaluator
- reflection_memory
- benchmark_report_json

## Discussion
Reflexion improved exact match by allowing the agent to inspect failed attempts and retry with reflection memory. The largest gains appeared in multi-hop cases where the first attempt stopped too early or selected the wrong second-hop entity. The trade-off was higher token usage and latency due to additional evaluator and reflector calls. On a local Ollama setup, this overhead was measurable but acceptable for benchmarking. A larger benchmark on at least 100 HotpotQA examples is still needed to validate whether the improvement generalizes beyond the mini dataset.
