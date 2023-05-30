import os
import json
from config.definitions import ROOT_DIR


class TreeUniqueValues:
    def __init__(self, collection):
        self.flattened_dict = {}
        self.collection = collection
        with open(os.path.join(ROOT_DIR, "collections", self.collection, "tree.json"), "r") as tree_file:
            self.tree = json.load(tree_file)
        self.__flatten_dict_recursive(self.tree)

    def __flatten_dict_recursive(self, tree, level=0):
        if tree is None:
            return
        for key in tree.keys():
            if key not in self.flattened_dict.keys():
                self.flattened_dict[key] = [0] * 7
            self.flattened_dict[key][level] += 1
            self.__flatten_dict_recursive(tree[key], level + 1)

    def flat_dict(self):
        return self.flattened_dict


def flatten_dict(collection):
    flat_dict = TreeUniqueValues(collection)
    return flat_dict.flat_dict()