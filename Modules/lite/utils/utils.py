from ..bootstrap import time, deque, functools


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
        self._slots = []

    def connect(self, func):
        self._slots.append(func)

    def emit(self, *args, **kwargs):
        for slot in self._slots:
            slot(*args, **kwargs)


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
