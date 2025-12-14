from collections import deque, defaultdict
from typing import Dict, List, Optional, Tuple, Deque

from .cache import LRUCache


class TrieNode:
    """Trie 노드"""

    __slots__ = ("children", "is_end", "patterns", "fail")

    def __init__(self):
        self.children: Dict[str, "TrieNode"] = {}
        self.is_end: bool = False
        self.patterns: List[Tuple[str, str]] = []  # [(pos, lemma), ...]
        self.fail: Optional["TrieNode"] = None


class Trie:
    """Aho-Corasick 알고리즘 기반 Trie"""

    def __init__(self):
        self.root = TrieNode()
        self._ac_built = False
        self._match_cache = LRUCache(capacity=1000)
        self._word_count = 0  # 단어 수 추적

    def insert(self, word: str, pos: str, lemma: Optional[str] = None):
        """단어를 Trie에 삽입"""
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]

        # 새로운 단어인 경우 카운트 증가
        if not node.is_end:
            self._word_count += 1

        node.is_end = True
        pattern = (pos, lemma or word)
        if pattern not in node.patterns:
            node.patterns.append(pattern)
        self._ac_built = False

    def build_aho_corasick(self):
        """Aho-Corasick failure link 구축 (BFS)"""
        if self._ac_built:
            return

        queue: Deque[TrieNode] = deque()
        self.root.fail = self.root

        # 루트의 자식들 초기화
        for child in self.root.children.values():
            child.fail = self.root
            queue.append(child)

        # BFS로 failure link 구축
        while queue:
            current = queue.popleft()

            for char, child in current.children.items():
                queue.append(child)

                # failure link 찾기
                fail_node = current.fail
                while fail_node != self.root and char not in fail_node.children:
                    fail_node = fail_node.fail

                if char in fail_node.children and fail_node.children[char] != child:
                    child.fail = fail_node.children[char]
                else:
                    child.fail = self.root

                # failure link가 가리키는 노드의 패턴 병합
                if child.fail.is_end:
                    for pattern in child.fail.patterns:
                        if pattern not in child.patterns:
                            child.patterns.append(pattern)

        self._ac_built = True
        self._match_cache = LRUCache(capacity=1000)

    def search_all_patterns(
        self, text: str
    ) -> List[Tuple[int, int, List[Tuple[str, str]]]]:
        """
        Aho-Corasick으로 모든 패턴 검색

        Returns:
            [(start, end, [(pos, lemma), ...]), ...]
        """
        # 캐시 확인
        cached = self._match_cache.get(text)
        if cached is not None:
            return cached

        self.build_aho_corasick()
        results = []
        node = self.root

        for i, ch in enumerate(text):
            # failure link 따라가기
            while node != self.root and ch not in node.children:
                node = node.fail

            if ch in node.children:
                node = node.children[ch]
            else:
                node = self.root
                continue

            # 현재 노드와 failure link로 연결된 모든 패턴 수집
            temp_node = node
            found_patterns = []

            while temp_node != self.root:
                if temp_node.is_end and temp_node.patterns:
                    found_patterns.extend(temp_node.patterns)
                temp_node = temp_node.fail

            # 패턴 발견시 시작 위치 계산
            if found_patterns:
                pattern_groups: Dict[int, List[Tuple[str, str]]] = defaultdict(list)
                for pos_tag, lemma in found_patterns:
                    for length in range(1, i + 2):
                        if i - length + 1 < 0:
                            continue
                        substring = text[i - length + 1 : i + 1]
                        if self._verify_pattern(substring, pos_tag, lemma):
                            pattern_groups[length].append((pos_tag, lemma))
                            break

                for length, patterns in pattern_groups.items():
                    start = i - length + 1
                    end = i + 1
                    results.append((start, end, patterns))

        # 캐시 저장
        self._match_cache.put(text, results)
        return results

    def _verify_pattern(self, word: str, pos: str, lemma: str) -> bool:
        """특정 단어가 사전에 있는지 확인"""
        node = self.root
        for ch in word:
            if ch not in node.children:
                return False
            node = node.children[ch]

        return node.is_end and (pos, lemma) in node.patterns

    def exists(self, word: str) -> bool:
        """단어가 Trie에 존재하는지 확인"""
        node = self.root
        for ch in word:
            if ch not in node.children:
                return False
            node = node.children[ch]
        return node.is_end

    def __len__(self) -> int:
        """Trie에 저장된 단어 수 반환"""
        return self._word_count

    def __contains__(self, word: str) -> bool:
        """in 연산자 지원"""
        return self.exists(word)

    def __iter__(self):
        """저장된 모든 단어와 패턴을 반환 (Generator)"""
        # DFS traversal
        stack: List[Tuple[str, TrieNode]] = [("", self.root)]

        while stack:
            prefix, node = stack.pop()

            if node.is_end:
                for pattern in node.patterns:
                    # pattern: (pos, lemma)
                    # yield (word, pos, lemma)
                    yield (prefix, pattern[0], pattern[1])

            for char, child in node.children.items():
                stack.append((prefix + char, child))
