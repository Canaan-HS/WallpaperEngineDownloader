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

    def _can_call(self, slot_info: dict, arg_count: int) -> bool:
        """
        檢查一個函式是否可以被指定數量的引數呼叫。

        Args:
            slot_info (dict): 包含函式引數資訊的字典。
            arg_count (int): 嘗試呼叫時提供的引數數量。

        Returns:
            bool: 如果引數數量在函式要求的範圍內，則回傳 True，否則為 False。
        """
        return slot_info["min_args"] <= arg_count <= slot_info["max_args"]

    def connect(self, func, once=False, label=""):
        """
        將一個函式（slot）連接到此信號。

        此方法會自動分析函式的簽章，以確定其可接受的引數數量範圍。
        如果 `once` 設定為 True，此函式只會被呼叫一次，然後自動斷開連接。

        Args:
            func (callable): 要連接的函式。
            once (bool, optional): 函式是否只執行一次。預設為 False。
            label (str, optional): 自訂指定標籤。

        Raises:
            TypeError: 如果 `func` 不是一個可呼叫的對象。

        Example:
            def on_event(data):
                print(f"Event occurred with data: {data}")

            signal = Signal()
            signal.connect(on_event)
        """
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

        self._slots[label.strip() or func.__name__] = {
            "func": func,
            "min_args": min_args,
            "max_args": max_args,
            "once": once,
        }

    def emit(self, target=None, *args, **kwargs):
        """
        發出信號，呼叫所有已連接或指定名稱的函式。

        如果沒有指定 `target`，則會呼叫所有已連接的函式，並傳遞 `args` 和 `kwargs`。
        在呼叫之前，會先檢查引數數量是否與函式簽章相符。
        如果指定了 `target`，則只會呼叫與該名稱匹配的函式。

        Args:
            target (str, optional): 指定要呼叫的函式名稱。如果為 None，則呼叫所有函式。
            *args: 傳遞給已連接函式的非關鍵字引數。
            **kwargs: 傳遞給已連接函式的關鍵字引數。

        Example:
            def handler_a():
                print("Handler A called!")

            def handler_b(message):
                print(f"Handler B called with message: {message}")

            signal = Signal()
            signal.connect(handler_a)
            signal.connect(handler_b)

            # 呼叫所有函式
            signal.emit(None, "Hello, World!")

            # 只呼叫 handler_a
            signal.emit("handler_a")
        """
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

    def request(self, target=None, *args, **kwargs):
        """
        發送一個請求給指定的 slot，並回傳該 slot 的結果。

        Args:
            target (str, optional): 指定要呼叫的函式名稱。如果為 None，則呼叫所有函式，並無回傳。
            *args: 傳遞給已連接函式的非關鍵字引數。
            **kwargs: 傳遞給已連接函式的關鍵字引數。
        """
        if target is None:
            self.emit(target, *args, **kwargs)  # 廣播不回傳
        else:
            slot_info = self._slots.get(target)
            if slot_info:
                result = slot_info["func"](*args, **kwargs)
                if slot_info.get("once"):
                    del self._slots[target]
                return result
        return None


class _Node:
    __slots__ = ("children", "indexes")

    def __init__(self):
        self.children = {}
        self.indexes = None


class BuildSuffixTree:
    def __init__(self, data_list: list):
        """
        在後綴樹中搜尋所有包含指定子字串的原始字串。

        此方法會將查詢字串轉換為小寫，然後遍歷後綴樹。
        如果找到與查詢字串匹配的路徑，它會收集該路徑下方所有節點儲存的原始字串索引，
        並回傳對應的字串列表。如果未找到匹配，則回傳空列表。
        此搜尋是大小寫不敏感的。

        Args:
            query (str): 你要搜尋的子字串。

        Returns:
            list: 包含指定子字串的所有原始字串列表。
                  如果沒有找到任何結果，則回傳一個空列表。

        Example:
            >>> tree = BuildSuffixTree(["apple", "Banana", "grape"])
            >>> tree.search("an")
            ['Banana']
            >>> tree.search("pe")
            ['apple', 'grape']
            >>> tree.search("xyz")
            []
        """
        self._root = _Node()
        self._original_data = data_list
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
    def search(self, query) -> list:
        query_lower = query.lower()
        node = self._root
        for char in query_lower:
            if char not in node.children:
                return []  # 查無此子字串
            node = node.children[char]
        matched_indexes = self._collect_indexes_from_node(node)
        return [self._original_data[i] for i in matched_indexes]
