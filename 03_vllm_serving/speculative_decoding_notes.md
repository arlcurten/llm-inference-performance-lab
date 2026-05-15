# Speculative Decoding Notes

## Core Flow

1. A small draft model proposes `K` tokens.
2. The target model verifies those tokens in one pass.
3. Accept the longest correct prefix.
4. On the first mismatch, reject the draft token and use the target token.
5. Continue from the corrected prefix.

## Why It Helps

The target model is expensive. If multiple draft tokens are accepted per target verification pass, we get more output tokens per expensive target invocation.

## Important Caveat

Speculative decoding reduces latency only when the draft model is much cheaper and its acceptance rate is high enough. Otherwise, draft overhead can dominate.

