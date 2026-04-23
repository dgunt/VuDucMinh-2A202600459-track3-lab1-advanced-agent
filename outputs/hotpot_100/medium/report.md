# Lab 16 Benchmark Report

## Metadata
- Dataset: hotpot_100.json::medium
- Mode: ollama
- Records: 70
- Agents: react, reflexion

## Summary
| Metric | ReAct | Reflexion | Delta |
|---|---:|---:|---:|
| EM | 0.8571 | 0.9714 | 0.1143 |
| Avg attempts | 1 | 1.1429 | 0.1429 |
| Avg token estimate | 503.6 | 618.86 | 115.26 |
| Avg latency (ms) | 22283.11 | 27103.77 | 4820.66 |

## Failure modes
```json
{
  "react": {
    "none": 30,
    "wrong_final_answer": 5
  },
  "reflexion": {
    "none": 34,
    "wrong_final_answer": 1
  }
}
```

## Extensions implemented
- structured_evaluator
- reflection_memory
- benchmark_report_json

## Discussion
Reflexion improved exact match by allowing the agent to inspect failed attempts and retry with reflection memory. The largest gains appeared in multi-hop cases where the first attempt stopped too early or selected the wrong second-hop entity. The trade-off was higher token usage and latency due to additional evaluator and reflector calls. On a local Ollama setup, this overhead was measurable but acceptable for benchmarking. A larger benchmark on at least 100 HotpotQA examples is still needed to validate whether the improvement generalizes beyond the mini dataset.
