from collections import deque, defaultdict


class Scene:
    def __init__(self, path: str):
        self.path = path
        self.entities = set()
        self.stack_last_actions = deque()
        self.stack_undo_actions = deque()

    def read_entities_from_file(self, path):
        pass
