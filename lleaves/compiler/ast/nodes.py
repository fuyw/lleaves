from dataclasses import dataclass
from typing import List

from lleaves.compiler.utils import DecisionType


class Node:
    @property
    def is_leaf(self):
        return isinstance(self, LeafNode)


@dataclass
class Tree:
    idx: int
    root_node: Node
    features: list
    class_id: int

    def __str__(self):
        return f"tree_{self.idx}"


@dataclass
class Forest:
    trees: List[Tree]
    features: list
    n_classes: int
    objective_func: str
    objective_func_config: str

    @property
    def n_args(self):
        return len(self.features)


class DecisionNode(Node):
    # the threshold in bit-representation if this node is categorical
    cat_threshold = None

    # child nodes
    left = None
    right = None

    def __init__(
        self,
        idx: int,
        split_feature: int,
        threshold: int,
        decision_type_id: int,
        left_idx: int,
        right_idx: int,
    ):
        self.idx = idx
        self.split_feature = split_feature
        self.threshold = threshold
        self.decision_type = DecisionType(decision_type_id)
        self.right_idx = right_idx
        self.left_idx = left_idx

    def add_children(self, left, right):
        self.left = left
        self.right = right

    def finalize_categorical(self, cat_threshold):
        self.cat_threshold = cat_threshold
        self.threshold = int(self.threshold)

    def validate(self):
        if self.decision_type.is_categorical:
            assert self.cat_threshold is not None
        else:
            assert self.threshold

    def __str__(self):
        return f"node_{self.idx}"


@dataclass
class LeafNode(Node):
    idx: int
    value: float

    def __str__(self):
        return f"leaf_{self.idx}"
