# Prefill vs Decode Notes

## Prefill

- Processes the full prompt in parallel.
- Dominated by larger matrix operations.
- Usually has better GPU utilization than single-token decode.
- Primary user-facing metric impact: TTFT.

## Decode

- Generates one token per sequence per step.
- Autoregressive dependency prevents parallelizing across time for one sequence.
- Often more memory-bound because weights and KV cache are repeatedly read.
- Primary user-facing metric impact: inter-token latency.

## Interview Line

Prefill is closer to a high-throughput batch GEMM workload. Decode is a repeated small-step workload where KV cache access, batching policy, and memory bandwidth become much more visible.

