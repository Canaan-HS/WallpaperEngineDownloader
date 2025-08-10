from ..bootstrap import time, deque, inspect, functools


def Elapsed_Time(func=None, *, label=""):
    """
    加上裝飾器 @Elapsed_Time
    """
    if func is None:
        return lambda f: Elapsed_Time(f, label=label)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start_time
        source = func.__name__ if not label else label
        print(f"調用: {source} | 耗時: {elapsed:.4f} 秒")
        return result

    return wrapper


class Signal:
    def __init__(self):
        self._slots = {}

    def _can_call(self, slot_info, arg_count):
        return slot_info["min_args"] <= arg_count <= slot_info["max_args"]

    def connect(self, func, once=False):
        sig = inspect.signature(func)
        params = sig.parameters.values()

        required_params = [
            p
            for p in params
            if p.default is inspect.Parameter.empty
            and p.kind
            in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
        ]
        min_args = len(required_params)

        if any(p.kind == inspect.Parameter.VAR_POSITIONAL for p in params):
            max_args = float("inf")
        else:
            max_args = len(
                [
                    p
                    for p in params
                    if p.kind
                    in (inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD)
                ]
            )

        self._slots[func.__name__] = {
            "func": func,
            "min_args": min_args,
            "max_args": max_args,
            "once": once,
        }

    def emit(self, target=None, *args, **kwargs):
        if target is None:
            to_remove = []
            for name, slot_info in self._slots.items():
                if self._can_call(slot_info, len(args)):
                    slot_info["func"](*args, **kwargs)
                    if slot_info.get("once"):
                        to_remove.append(name)
            for name in to_remove:
                del self._slots[name]
        else:
            slot_info = self._slots.get(target)
            if slot_info:
                slot_info["func"](*args, **kwargs)
                if slot_info.get("once"):
                    del self._slots[target]


class _Node:
    __slots__ = ("children", "indexes")

    def __init__(self):
        self.children = {}
        self.indexes = None


class BuildSuffixTree:
    def __init__(self, data_list):
        self._root = _Node()
        self._original_data = list(data_list)
        for idx, word in enumerate(self._original_data):
            word_lower = word.lower()
            for i in range(len(word_lower)):
                node = self._root
                for char in word_lower[i:]:
                    if char not in node.children:
                        node.children[char] = _Node()
                    node = node.children[char]
                if node.indexes is None:
                    node.indexes = set()
                node.indexes.add(idx)

    # 為結果收集函式增加快取
    @functools.lru_cache(maxsize=1024)
    def _collect_indexes_from_node(self, node):
        indexes = set()
        queue = deque([node])
        while queue:
            current_node = queue.popleft()
            if current_node.indexes is not None:
                indexes.update(current_node.indexes)
            for child_node in current_node.children.values():
                queue.append(child_node)
        return frozenset(indexes)

    # 清除快取
    def clear_tree(self):
        self._collect_indexes_from_node.cache_clear()

    # 搜尋
    def search(self, query):
        query_lower = query.lower()
        node = self._root
        for char in query_lower:
            if char not in node.children:
                return []  # 查無此子字串
            node = node.children[char]
        matched_indexes = self._collect_indexes_from_node(node)
        return [self._original_data[i] for i in matched_indexes]
