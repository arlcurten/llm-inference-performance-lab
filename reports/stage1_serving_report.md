# Stage 1 Serving Report

Status: in progress.

## Questions This Stage Must Answer

- What changes between prefill and decode?
- Why does KV cache become a serving bottleneck?
- How does block-based KV cache management reduce fragmentation?
- Why does continuous batching improve utilization?
- When does speculative decoding help?

## Current Artifacts

- Toy KV block manager with refcount and copy-on-write.
- Mock speculative decoding simulator.

