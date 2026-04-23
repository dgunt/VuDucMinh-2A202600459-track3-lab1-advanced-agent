# Lab 16 Benchmark Report

## Metadata
- Dataset: hotpot_100.json::all
- Mode: ollama
- Records: 200
- Agents: react, reflexion

## Summary
| Metric | ReAct | Reflexion | Delta |
|---|---:|---:|---:|
| EM | 0.86 | 0.95 | 0.09 |
| Avg attempts | 1 | 1.22 | 0.22 |
| Avg token estimate | 404.02 | 619.07 | 215.05 |
| Avg latency (ms) | 13591.79 | 21960.18 | 8368.39 |

## Failure modes
```json
{
  "react": {
    "none": 86,
    "wrong_final_answer": 14
  },
  "reflexion": {
    "none": 95,
    "wrong_final_answer": 5
  }
}
```

## Extensions implemented
- structured_evaluator
- reflection_memory
- benchmark_report_json

## Discussion
Reflexion improved exact match by allowing the agent to inspect failed attempts and retry with reflection memory. The largest gains appeared in multi-hop cases where the first attempt stopped too early or selected the wrong second-hop entity. The trade-off was higher token usage and latency due to additional evaluator and reflector calls. On a local Ollama setup, this overhead was measurable but acceptable for benchmarking. A larger benchmark on at least 100 HotpotQA examples is still needed to validate whether the improvement generalizes beyond the mini dataset.
