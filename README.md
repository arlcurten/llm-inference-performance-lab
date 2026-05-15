# LLM Inference Performance Lab

This repo is a hands-on lab for connecting LLM inference performance from system level to kernel level to distributed inference.

The goal is not to build a production serving stack. The goal is to produce clear evidence that we understand where inference bottlenecks come from and how to analyze them.

## Roadmap

### Stage 1: LLM Serving, vLLM, KV Cache

Focus:

- Prefill vs decode
- TTFT, ITL, latency, throughput
- KV cache pressure
- PagedAttention-style block management
- Continuous batching
- Speculative decoding

Artifacts:

- `03_vllm_serving/benchmark_results.md`
- `03_vllm_serving/prefill_decode_notes.md`
- `03_vllm_serving/paged_attention_notes.md`
- `03_vllm_serving/block_manager.py`
- `03_vllm_serving/block_manager_tests.py`
- `03_vllm_serving/continuous_batching_notes.md`
- `03_vllm_serving/speculative_decoding_sim.py`
- `03_vllm_serving/speculative_decoding_notes.md`

### Stage 2: Triton Kernel, Profiling, FlashAttention

Focus:

- Fused softmax
- GEMM tiling
- Nsight Compute
- Nsight Systems
- Online softmax
- FlashAttention memory traffic analysis

### Stage 3: Tensor Parallel and Distributed Inference

Focus:

- ColumnParallelLinear
- RowParallelLinear
- Tensor parallel MLP
- all-reduce / all-gather
- communication overlap

## Current Checkpoint

Stage 1 has initial runnable toy implementations for:

- PagedAttention-style KV block management
- Speculative decoding control flow

Run:

```bash
python -m unittest discover -s 03_vllm_serving -p '*tests.py'
python 03_vllm_serving/speculative_decoding_sim.py
```

