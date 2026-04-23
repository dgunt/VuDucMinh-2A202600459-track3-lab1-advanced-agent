# Lab 16 Benchmark Report

## Metadata
- Dataset: hotpot_100.json::hard
- Mode: ollama
- Records: 70
- Agents: react, reflexion

## Summary
| Metric | ReAct | Reflexion | Delta |
|---|---:|---:|---:|
| EM | 0.8 | 0.9429 | 0.1429 |
| Avg attempts | 1 | 1.4 | 0.4 |
| Avg token estimate | 429.69 | 821.06 | 391.37 |
| Avg latency (ms) | 17269.11 | 35457 | 18187.89 |

## Failure modes
```json
{
  "react": {
    "none": 28,
    "wrong_final_answer": 7
  },
  "reflexion": {
    "none": 33,
    "wrong_final_answer": 2
  }
}
```

## Extensions implemented
- structured_evaluator
- reflection_memory
- benchmark_report_json

## Discussion
Reflexion improved exact match by allowing the agent to inspect failed attempts and retry with reflection memory. The largest gains appeared in multi-hop cases where the first attempt stopped too early or selected the wrong second-hop entity. The trade-off was higher token usage and latency due to additional evaluator and reflector calls. On a local Ollama setup, this overhead was measurable but acceptable for benchmarking. A larger benchmark on at least 100 HotpotQA examples is still needed to validate whether the improvement generalizes beyond the mini dataset.
