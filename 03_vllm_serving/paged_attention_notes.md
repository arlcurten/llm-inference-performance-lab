# PagedAttention and KV Cache Notes

## KV Cache

During autoregressive decoding, each layer stores previous key and value tensors so future tokens do not recompute attention over the full prefix.

Memory grows with:

- number of layers
- sequence length
- hidden size / number of KV heads
- batch size
- dtype size

## Fragmentation Problem

Requests have different prompt lengths and finish at different times. A naive contiguous allocation strategy can waste memory when sequences grow, shrink, or terminate unevenly.

## PagedAttention Idea

PagedAttention treats KV cache memory like paged virtual memory:

- logical blocks describe a sequence's token positions
- physical blocks are fixed-size GPU memory chunks
- a block table maps logical blocks to physical blocks
- refcounts allow prompt sharing
- copy-on-write allows branches to diverge without corrupting shared prefixes

The key system win is better KV cache utilization, which helps serving throughput under mixed request lengths.

