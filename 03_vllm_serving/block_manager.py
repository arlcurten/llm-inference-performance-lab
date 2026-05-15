"""Toy PagedAttention-style KV cache block manager.

This is intentionally small. It models the bookkeeping that matters for
interviews: logical blocks, physical blocks, block tables, refcounts,
copy-on-write, and free block management.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class PhysicalBlock:
    block_id: int
    tokens: list[int] = field(default_factory=list)
    ref_count: int = 0


@dataclass
class SequenceState:
    seq_id: str
    block_table: list[int] = field(default_factory=list)
    length: int = 0


class OutOfBlocksError(RuntimeError):
    pass


class BlockManager:
    def __init__(self, num_blocks: int, block_size: int) -> None:
        if num_blocks <= 0:
            raise ValueError("num_blocks must be positive")
        if block_size <= 0:
            raise ValueError("block_size must be positive")

        self.block_size = block_size
        self.blocks = {i: PhysicalBlock(block_id=i) for i in range(num_blocks)}
        self.free_blocks = list(range(num_blocks))
        self.sequences: dict[str, SequenceState] = {}

    def create_sequence(self, seq_id: str, tokens: list[int] | None = None) -> None:
        if seq_id in self.sequences:
            raise ValueError(f"sequence already exists: {seq_id}")

        self.sequences[seq_id] = SequenceState(seq_id=seq_id)
        for token in tokens or []:
            self.append_token(seq_id, token)

    def fork_sequence(self, parent_seq_id: str, child_seq_id: str) -> None:
        """Create a child sequence sharing the parent's physical blocks."""
        if child_seq_id in self.sequences:
            raise ValueError(f"sequence already exists: {child_seq_id}")

        parent = self._seq(parent_seq_id)
        child_table = list(parent.block_table)
        self.sequences[child_seq_id] = SequenceState(
            seq_id=child_seq_id,
            block_table=child_table,
            length=parent.length,
        )
        for block_id in child_table:
            self.blocks[block_id].ref_count += 1

    def append_token(self, seq_id: str, token: int) -> None:
        seq = self._seq(seq_id)

        if seq.length % self.block_size == 0:
            block_id = self._alloc_block()
            seq.block_table.append(block_id)
        else:
            logical_block = seq.length // self.block_size
            block_id = seq.block_table[logical_block]
            if self.blocks[block_id].ref_count > 1:
                block_id = self._copy_on_write(seq, logical_block)

        self.blocks[block_id].tokens.append(token)
        seq.length += 1

    def get_tokens(self, seq_id: str) -> list[int]:
        seq = self._seq(seq_id)
        out: list[int] = []
        remaining = seq.length
        for block_id in seq.block_table:
            take = min(self.block_size, remaining)
            out.extend(self.blocks[block_id].tokens[:take])
            remaining -= take
            if remaining <= 0:
                break
        return out

    def free_sequence(self, seq_id: str) -> None:
        seq = self._seq(seq_id)
        for block_id in seq.block_table:
            self._decref(block_id)
        del self.sequences[seq_id]

    def debug_snapshot(self) -> dict[str, object]:
        return {
            "free_blocks": list(self.free_blocks),
            "sequences": {
                seq_id: {
                    "length": seq.length,
                    "block_table": list(seq.block_table),
                }
                for seq_id, seq in self.sequences.items()
            },
            "blocks": {
                block_id: {
                    "tokens": list(block.tokens),
                    "ref_count": block.ref_count,
                }
                for block_id, block in self.blocks.items()
            },
        }

    def _seq(self, seq_id: str) -> SequenceState:
        try:
            return self.sequences[seq_id]
        except KeyError as exc:
            raise KeyError(f"unknown sequence: {seq_id}") from exc

    def _alloc_block(self) -> int:
        if not self.free_blocks:
            raise OutOfBlocksError("no free physical KV cache blocks")
        block_id = self.free_blocks.pop()
        block = self.blocks[block_id]
        block.tokens.clear()
        block.ref_count = 1
        return block_id

    def _decref(self, block_id: int) -> None:
        block = self.blocks[block_id]
        block.ref_count -= 1
        if block.ref_count < 0:
            raise RuntimeError(f"negative ref_count for block {block_id}")
        if block.ref_count == 0:
            block.tokens.clear()
            self.free_blocks.append(block_id)

    def _copy_on_write(self, seq: SequenceState, logical_block: int) -> int:
        old_block_id = seq.block_table[logical_block]
        old_block = self.blocks[old_block_id]

        new_block_id = self._alloc_block()
        new_block = self.blocks[new_block_id]
        new_block.tokens = list(old_block.tokens)

        seq.block_table[logical_block] = new_block_id
        self._decref(old_block_id)
        return new_block_id


if __name__ == "__main__":
    manager = BlockManager(num_blocks=4, block_size=2)
    manager.create_sequence("prompt", [10, 11, 12])
    manager.fork_sequence("prompt", "branch")
    manager.append_token("branch", 99)
    print(manager.debug_snapshot())

