"""Small speculative decoding simulator.

The models here are deterministic mocks. The point is to make the accept,
reject, rollback, and target-resample control flow visible before wiring this
idea to a real draft/target model pair.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class TokenModel(Protocol):
    def next_token(self, prefix: list[int]) -> int:
        ...


@dataclass
class CycleModel:
    vocab_size: int
    offset: int = 1

    def next_token(self, prefix: list[int]) -> int:
        last = prefix[-1] if prefix else 0
        return (last + self.offset) % self.vocab_size


@dataclass
class ScriptedDraftModel:
    scripted: list[int]
    fallback: TokenModel
    position: int = 0

    def next_token(self, prefix: list[int]) -> int:
        if self.position < len(self.scripted):
            token = self.scripted[self.position]
            self.position += 1
            return token
        return self.fallback.next_token(prefix)


@dataclass
class SpeculativeStats:
    target_calls: int = 0
    draft_calls: int = 0
    accepted_tokens: int = 0
    rejected_tokens: int = 0


def draft_k_tokens(model: TokenModel, prefix: list[int], k: int, stats: SpeculativeStats) -> list[int]:
    draft: list[int] = []
    work = list(prefix)
    for _ in range(k):
        token = model.next_token(work)
        stats.draft_calls += 1
        draft.append(token)
        work.append(token)
    return draft


def verify_draft(
    target_model: TokenModel,
    prefix: list[int],
    draft_tokens: list[int],
    stats: SpeculativeStats,
) -> tuple[list[int], bool]:
    """Return accepted tokens and whether the full draft was accepted."""
    accepted: list[int] = []
    work = list(prefix)

    for draft_token in draft_tokens:
        target_token = target_model.next_token(work)
        stats.target_calls += 1
        if draft_token != target_token:
            stats.rejected_tokens += 1
            return accepted + [target_token], False
        accepted.append(draft_token)
        stats.accepted_tokens += 1
        work.append(draft_token)

    return accepted, True


def speculative_decode(
    draft_model: TokenModel,
    target_model: TokenModel,
    prefix: list[int],
    max_new_tokens: int,
    draft_len: int,
) -> tuple[list[int], SpeculativeStats]:
    if max_new_tokens < 0:
        raise ValueError("max_new_tokens must be non-negative")
    if draft_len <= 0:
        raise ValueError("draft_len must be positive")

    output = list(prefix)
    stats = SpeculativeStats()

    while len(output) - len(prefix) < max_new_tokens:
        remaining = max_new_tokens - (len(output) - len(prefix))
        k = min(draft_len, remaining)
        draft_tokens = draft_k_tokens(draft_model, output, k, stats)
        accepted_or_resampled, full_accept = verify_draft(target_model, output, draft_tokens, stats)

        for token in accepted_or_resampled[:remaining]:
            output.append(token)

        if full_accept and len(output) - len(prefix) < max_new_tokens:
            bonus_token = target_model.next_token(output)
            stats.target_calls += 1
            output.append(bonus_token)

    return output, stats


def main() -> None:
    target = CycleModel(vocab_size=10, offset=1)
    draft = ScriptedDraftModel(scripted=[1, 2, 8, 4, 5, 6], fallback=target)

    output, stats = speculative_decode(
        draft_model=draft,
        target_model=target,
        prefix=[0],
        max_new_tokens=8,
        draft_len=3,
    )
    print("output:", output)
    print("stats:", stats)


if __name__ == "__main__":
    main()

