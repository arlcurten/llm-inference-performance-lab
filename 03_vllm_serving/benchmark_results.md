# vLLM Benchmark Results

Status: not run yet.

## Model Candidates

- `meta-llama/Llama-3.2-1B-Instruct`
- `Qwen/Qwen2.5-1.5B-Instruct`
- small Gemma instruct model

## Metrics To Record

| Run | Model | Input Len | Output Len | Concurrency | TTFT | ITL | E2E Latency | Tokens/s | Requests/s | GPU Memory |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |

## Notes

- Track how latency changes as concurrency increases.
- Separate prefill-heavy prompts from decode-heavy long generation.
- Keep raw command lines and profiler settings under each run.

