import unittest

from block_manager import BlockManager, OutOfBlocksError


class BlockManagerTest(unittest.TestCase):
    def test_appends_across_logical_blocks(self) -> None:
        manager = BlockManager(num_blocks=4, block_size=2)
        manager.create_sequence("a", [1, 2, 3])

        self.assertEqual(manager.get_tokens("a"), [1, 2, 3])
        self.assertEqual(len(manager.sequences["a"].block_table), 2)

    def test_fork_shares_blocks_until_write(self) -> None:
        manager = BlockManager(num_blocks=6, block_size=4)
        manager.create_sequence("parent", [1, 2, 3])
        manager.fork_sequence("parent", "child")

        shared_block = manager.sequences["parent"].block_table[0]
        self.assertEqual(manager.blocks[shared_block].ref_count, 2)

        manager.append_token("child", 99)

        parent_block = manager.sequences["parent"].block_table[0]
        child_block = manager.sequences["child"].block_table[0]
        self.assertNotEqual(parent_block, child_block)
        self.assertEqual(manager.get_tokens("parent"), [1, 2, 3])
        self.assertEqual(manager.get_tokens("child"), [1, 2, 3, 99])
        self.assertEqual(manager.blocks[parent_block].ref_count, 1)
        self.assertEqual(manager.blocks[child_block].ref_count, 1)

    def test_full_new_block_does_not_copy_on_write(self) -> None:
        manager = BlockManager(num_blocks=6, block_size=2)
        manager.create_sequence("parent", [1, 2])
        manager.fork_sequence("parent", "child")

        manager.append_token("child", 3)

        self.assertEqual(manager.get_tokens("parent"), [1, 2])
        self.assertEqual(manager.get_tokens("child"), [1, 2, 3])
        self.assertEqual(len(manager.sequences["child"].block_table), 2)

    def test_free_sequence_releases_blocks(self) -> None:
        manager = BlockManager(num_blocks=3, block_size=2)
        manager.create_sequence("a", [1, 2, 3])
        before = len(manager.free_blocks)

        manager.free_sequence("a")

        self.assertGreater(len(manager.free_blocks), before)
        self.assertNotIn("a", manager.sequences)

    def test_out_of_blocks(self) -> None:
        manager = BlockManager(num_blocks=1, block_size=1)
        manager.create_sequence("a", [1])

        with self.assertRaises(OutOfBlocksError):
            manager.append_token("a", 2)


if __name__ == "__main__":
    unittest.main()

