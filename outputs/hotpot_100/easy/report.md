# Lab 16 Benchmark Report

## Metadata
- Dataset: hotpot_100.json::easy
- Mode: ollama
- Records: 60
- Agents: react, reflexion

## Summary
| Metric | ReAct | Reflexion | Delta |
|---|---:|---:|---:|
| EM | 0.9 | 1.0 | 0.1 |
| Avg attempts | 1 | 1.0667 | 0.0667 |
| Avg token estimate | 304.73 | 320.2 | 15.47 |
| Avg latency (ms) | 8857.97 | 9142.63 | 284.66 |

## Failure modes
```json
{
  "react": {
    "none": 27,
    "wrong_final_answer": 3
  },
  "reflexion": {
    "none": 30
  }
}
```

## Extensions implemented
- structured_evaluator
- reflection_memory
- benchmark_report_json

## Discussion
Reflexion improved exact match by allowing the agent to inspect failed attempts and retry with reflection memory. The largest gains appeared in multi-hop cases where the first attempt stopped too early or selected the wrong second-hop entity. The trade-off was higher token usage and latency due to additional evaluator and reflector calls. On a local Ollama setup, this overhead was measurable but acceptable for benchmarking. A larger benchmark on at least 100 HotpotQA examples is still needed to validate whether the improvement generalizes beyond the mini dataset.
