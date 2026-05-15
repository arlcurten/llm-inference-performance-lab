# Continuous Batching Notes

## Static Batching

- Form a batch.
- Run until every request in the batch completes.
- Long requests can hold slots while shorter requests finish early.
- GPU work can become uneven when request lengths vary.

## Continuous Batching

- Re-schedule at token boundaries.
- Remove completed requests immediately.
- Admit new requests into newly freed slots.
- Improves throughput and GPU utilization for serving workloads with variable request lengths.

## Interview Line

Continuous batching turns decode into a dynamic scheduling problem. It does not remove autoregressive dependency for a single request, but it keeps the GPU busier across many requests.

