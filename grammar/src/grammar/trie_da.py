import struct
import pickle
from typing import List, Tuple, Optional, Dict, Set
from collections import defaultdict


class FST:
    """
    Finite State Transducer
    품사(POS)와 표제어(Lemma)를 압축 저장
    """

    def __init__(self):
        # 문자열 -> ID 매핑
        self.string_to_id: Dict[str, int] = {}
        self.id_to_string: Dict[int, str] = {}
        self.next_id: int = 0

    def encode(self, value: str) -> int:
        """문자열을 ID로 인코딩"""
        if value not in self.string_to_id:
            self.string_to_id[value] = self.next_id
            self.id_to_string[self.next_id] = value
            self.next_id += 1
        return self.string_to_id[value]

    def decode(self, value_id: int) -> str:
        """ID를 문자열로 디코딩"""
        return self.id_to_string.get(value_id, "")

    def size(self) -> int:
        """저장된 고유 문자열 수"""
        return self.next_id


class DoubleArrayTrie:
    """
    Double Array Trie 구현

    구조:
    - BASE 배열: 다음 상태로의 전이 계산
    - CHECK 배열: 유효성 검증
    - VALUE 배열: 종료 상태의 값 (FST ID 목록)

    상태 전이: next_state = BASE[current_state] + char_code
    검증: CHECK[next_state] == current_state
    """

    def __init__(self):
        # Double Array 구조
        self.base: List[int] = []
        self.check: List[int] = []
        self.value: List[Optional[List[Tuple[int, int]]]] = (
            []
        )  # [(pos_id, lemma_id), ...]
        self.fail: List[int] = []  # Aho-Corasick failure links

        # FST for 품사/표제어 압축
        self.pos_fst = FST()
        self.lemma_fst = FST()

        # 빌드용 임시 데이터
        self._build_data: List[Tuple[str, str, str]] = []  # (word, pos, lemma)
        self._built: bool = False

        # 검색 최적화 캐시
        self._search_cache: Dict[str, List[Tuple[int, int, List[Tuple[str, str]]]]] = {}
        self._exists_cache: Dict[str, bool] = {}

    def insert(self, word: str, pos: str, lemma: Optional[str] = None):
        """단어 삽입 (빌드 전)"""
        if self._built:
            raise RuntimeError("Trie already built. Cannot insert after build.")

        lemma = lemma or word
        self._build_data.append((word, pos, lemma))

    def build(self):
        """Double Array Trie 빌드"""
        if self._built:
            return

        if not self._build_data:
            print("Warning: No data to build Trie")
            return

        # 1. 데이터 정렬 및 그룹화
        word_patterns: Dict[str, List[Tuple[str, str]]] = defaultdict(list)
        for word, pos, lemma in self._build_data:
            if (pos, lemma) not in word_patterns[word]:
                word_patterns[word].append((pos, lemma))

        # 2. Trie 구조 구축
        trie = self._build_trie(word_patterns)

        # 3. Double Array 변환
        self._construct_double_array(trie)

        # 4. Failure Links 구축 (Aho-Corasick)
        self._build_failure_links()

        # 5. 메모리 해제
        self._build_data = []
        self._built = True

        print(
            f"Double Array Trie 빌드 완료: {len(word_patterns)} 단어, "
            f"배열 크기: {len(self.base)}, "
            f"품사: {self.pos_fst.size()}, 표제어: {self.lemma_fst.size()}"
        )

    def _build_trie(self, word_patterns: Dict[str, List[Tuple[str, str]]]) -> Dict:
        """임시 Trie 구조 구축"""
        root = {}

        for word, patterns in word_patterns.items():
            node = root
            for char in word:
                if char not in node:
                    node[char] = {}
                node = node[char]

            # 종료 노드에 패턴 저장
            if "__end__" not in node:
                node["__end__"] = []

            for pos, lemma in patterns:
                pos_id = self.pos_fst.encode(pos)
                lemma_id = self.lemma_fst.encode(lemma)
                node["__end__"].append((pos_id, lemma_id))

        return root

    def _construct_double_array(self, trie: Dict):
        """Trie를 Double Array로 변환 (버그 수정)"""
        # 초기화 - 더 큰 초기 크기로 시작
        initial_size = 50000
        self.base = [-1] * initial_size
        self.check = [-1] * initial_size
        self.value = [None] * initial_size

        # 루트 상태
        self.base[0] = 1
        self.check[0] = -1

        # BFS로 상태 할당
        queue = [(0, trie)]  # (state, node)
        used_states: Set[int] = {0}

        while queue:
            current_state, node = queue.pop(0)

            # 종료 노드 처리 - 자식이 없어도 처리해야 함!
            if "__end__" in node:
                self.value[current_state] = node["__end__"]

            # 자식 문자들 수집
            children = [(c, n) for c, n in node.items() if c != "__end__"]
            if not children:
                continue

            # BASE 값 찾기 (모든 자식을 수용할 수 있는 값)
            char_codes = [ord(c) for c, _ in children]

            # 필요한 최대 상태 계산
            max_needed_state = max(char_codes) + 1000  # 여유 공간

            # 배열 크기 확인 및 확장
            while len(self.base) < max_needed_state:
                self._expand_arrays()

            base_value = self._find_base(char_codes, used_states)

            # 배열 확장 후 재시도
            retry_count = 0
            while base_value == -1 and retry_count < 10:
                self._expand_arrays()
                base_value = self._find_base(char_codes, used_states)
                retry_count += 1

            if base_value == -1:
                raise RuntimeError(f"Cannot allocate BASE for state {current_state}")

            self.base[current_state] = base_value

            # 자식 상태 할당
            for char, child_node in children:
                char_code = ord(char)
                next_state = base_value + char_code

                # 배열 범위 체크 및 확장
                while next_state >= len(self.base):
                    self._expand_arrays()

                self.check[next_state] = current_state
                used_states.add(next_state)
                queue.append((next_state, child_node))

        # 배열 압축 (사용하지 않는 뒷부분 제거)
        self._compress_arrays()

    def _find_base(self, char_codes: List[int], used_states: Set[int]) -> int:
        """모든 자식을 수용할 수 있는 BASE 값 찾기 (개선)"""
        if not char_codes:
            return 1

        # 최소 문자 코드 기준으로 탐색 시작점 결정
        min_char = min(char_codes)
        max_char = max(char_codes)
        start_base = max(1, 1 - min_char)

        # 배열 길이 제한
        max_search = min(len(self.base) - max_char - 1, len(self.base) - 100)

        # 1부터 시작 (0은 루트)
        for base_candidate in range(start_base, max_search):
            # 모든 자식이 비어있는 위치에 배치 가능한지 확인
            valid = True

            for char_code in char_codes:
                next_state = base_candidate + char_code

                # 범위 체크
                if next_state >= len(self.base):
                    valid = False
                    break

                if next_state in used_states or self.check[next_state] != -1:
                    valid = False
                    break

            if valid:
                return base_candidate

        return -1

    def _expand_arrays(self):
        """배열 크기 확장 (안정화)"""
        current_size = len(self.base)
        expansion_size = max(10000, current_size // 2)  # 최소 10000씩 확장

        self.base.extend([-1] * expansion_size)
        self.check.extend([-1] * expansion_size)
        self.value.extend([None] * expansion_size)

    def _compress_arrays(self):
        """배열 압축 (미사용 부분 제거)"""
        # 마지막 사용 인덱스 찾기
        last_used = 0
        for i in range(len(self.check) - 1, -1, -1):
            if self.check[i] != -1:
                last_used = i
                break

        # 압축
        self.base = self.base[: last_used + 1]
        self.check = self.check[: last_used + 1]
        self.value = self.value[: last_used + 1]

    def _build_failure_links(self):
        """Aho-Corasick failure link 구축 (최적화)"""
        from collections import deque

        # failure link 배열 초기화
        self.fail = [0] * len(self.base)

        # 각 상태의 자식 문자들을 추적
        state_children: Dict[int, List[int]] = defaultdict(list)

        # 자식 관계 구축
        for state in range(len(self.check)):
            if self.check[state] != -1:
                parent = self.check[state]
                # 문자 코드 역계산
                if parent < len(self.base) and self.base[parent] != -1:
                    char_code = state - self.base[parent]
                    if 0 <= char_code < 0x10000:
                        state_children[parent].append(char_code)

        queue = deque()

        # 루트의 직접 자식들은 루트(0)로 fail
        for char_code in state_children.get(0, []):
            next_state = self.base[0] + char_code
            if 0 < next_state < len(self.check) and self.check[next_state] == 0:
                self.fail[next_state] = 0
                queue.append(next_state)

        # BFS로 나머지 failure links 구축
        while queue:
            state = queue.popleft()

            if state >= len(self.base) or self.base[state] == -1:
                continue

            # 실제 자식들만 순회
            for char_code in state_children.get(state, []):
                next_state = self.base[state] + char_code

                if next_state >= len(self.check) or self.check[next_state] != state:
                    continue

                queue.append(next_state)

                # failure link 찾기
                fail_state = self.fail[state]
                while fail_state != 0:
                    fail_next = self.base[fail_state] + char_code
                    if (
                        0 < fail_next < len(self.check)
                        and self.check[fail_next] == fail_state
                    ):
                        self.fail[next_state] = fail_next
                        break
                    fail_state = self.fail[fail_state]
                else:
                    # 루트에서 전이 확인
                    if self.base[0] != -1:
                        root_next = self.base[0] + char_code
                        if (
                            0 < root_next < len(self.check)
                            and self.check[root_next] == 0
                        ):
                            self.fail[next_state] = root_next
                        else:
                            self.fail[next_state] = 0
                    else:
                        self.fail[next_state] = 0

                # failure link가 가리키는 상태의 패턴 병합 (Python Trie와 동일)
                fail_target = self.fail[next_state]
                if (
                    fail_target != 0
                    and fail_target < len(self.value)
                    and self.value[fail_target] is not None
                ):
                    if self.value[next_state] is None:
                        self.value[next_state] = []
                    for pattern in self.value[fail_target]:
                        if pattern not in self.value[next_state]:
                            self.value[next_state].append(pattern)

    def exists(self, word: str) -> bool:
        """단어 존재 여부 확인"""
        if not self._built:
            self.build()

        # 캐시 확인
        if word in self._exists_cache:
            return self._exists_cache[word]

        result = self._traverse(word) is not None
        self._exists_cache[word] = result
        return result

    def _traverse(self, word: str) -> Optional[int]:
        """단어를 따라 트리를 순회하고 최종 상태 반환"""
        if not self._built:
            return None

        state = 0

        for char in word:
            char_code = ord(char)

            if state >= len(self.base) or self.base[state] == -1:
                return None

            next_state = self.base[state] + char_code

            if next_state >= len(self.check) or self.check[next_state] != state:
                return None

            state = next_state

        # 종료 상태인지 확인
        if state < len(self.value) and self.value[state] is not None:
            return state

        return None

    def get_patterns(self, word: str) -> List[Tuple[str, str]]:
        """단어의 품사-표제어 쌍 반환"""
        if not self._built:
            self.build()

        state = self._traverse(word)
        if state is None:
            return []

        patterns = []
        for pos_id, lemma_id in self.value[state]:
            pos = self.pos_fst.decode(pos_id)
            lemma = self.lemma_fst.decode(lemma_id)
            patterns.append((pos, lemma))

        return patterns

    def search(self, word: str) -> List[Tuple[str, str]]:
        """Alias for get_patterns (Compatibility)"""
        return self.get_patterns(word)

    def _verify_pattern(self, word: str, pos: str, lemma: str) -> bool:
        """특정 단어가 사전에 정확히 존재하는지 확인"""
        state = self._traverse(word)
        if state is None:
            return False

        # 해당 상태에 (pos, lemma) 패턴이 있는지 확인
        if state < len(self.value) and self.value[state] is not None:
            pos_id = self.pos_fst.string_to_id.get(pos)
            lemma_id = self.lemma_fst.string_to_id.get(lemma)

            if pos_id is not None and lemma_id is not None:
                return (pos_id, lemma_id) in self.value[state]

        return False

    def search_all_patterns(
        self, text: str
    ) -> List[Tuple[int, int, List[Tuple[str, str]]]]:
        """
        Aho-Corasick 알고리즘으로 모든 패턴 검색

        Returns:
            [(start, end, [(pos, lemma), ...]), ...]
        """
        if not self._built:
            self.build()

        # 캐시 확인
        if text in self._search_cache:
            return self._search_cache[text]

        results = []
        state = 0

        for i, char in enumerate(text):
            char_code = ord(char)

            # failure link 따라가기
            while state != 0:
                next_state = self.base[state] + char_code
                if 0 < next_state < len(self.check) and self.check[next_state] == state:
                    state = next_state
                    break
                state = self.fail[state]
            else:
                # 루트에서 전이 시도
                if self.base[0] != -1:
                    next_state = self.base[0] + char_code
                    if 0 < next_state < len(self.check) and self.check[next_state] == 0:
                        state = next_state
                    else:
                        state = 0
                        continue
                else:
                    state = 0
                    continue

            # 현재 상태와 failure link 체인에서 모든 패턴 수집
            temp_state = state
            found_patterns = []

            while temp_state != 0:
                if temp_state < len(self.value) and self.value[temp_state] is not None:
                    for pos_id, lemma_id in self.value[temp_state]:
                        pos = self.pos_fst.decode(pos_id)
                        lemma = self.lemma_fst.decode(lemma_id)
                        found_patterns.append((pos, lemma))
                temp_state = self.fail[temp_state]

            # 패턴 발견 시 시작 위치 계산 및 검증
            if found_patterns:
                pattern_groups = defaultdict(list)
                for pos_tag, lemma in found_patterns:
                    # 가능한 모든 길이 시도
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

        # 캐시 저장 (최대 1000개)
        if len(self._search_cache) < 1000:
            self._search_cache[text] = results

        return results

    def save(self, filepath: str):
        """Trie 저장"""
        if not self._built:
            self.build()

        data = {
            "base": self.base,
            "check": self.check,
            "value": self.value,
            "fail": self.fail,  # Aho-Corasick failure links
            "pos_fst": {
                "string_to_id": self.pos_fst.string_to_id,
                "id_to_string": self.pos_fst.id_to_string,
                "next_id": self.pos_fst.next_id,
            },
            "lemma_fst": {
                "string_to_id": self.lemma_fst.string_to_id,
                "id_to_string": self.lemma_fst.id_to_string,
                "next_id": self.lemma_fst.next_id,
            },
        }

        with open(filepath, "wb") as f:
            pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)

        print(f"Double Array Trie 저장 완료: {filepath}")

    def load(self, filepath: str):
        """Trie 로드"""
        with open(filepath, "rb") as f:
            data = pickle.load(f)

        self.base = data["base"]
        self.check = data["check"]
        self.value = data["value"]
        self.fail = data.get("fail", [0] * len(data["base"]))  # 하위 호환성

        # FST 복원
        self.pos_fst.string_to_id = data["pos_fst"]["string_to_id"]
        self.pos_fst.id_to_string = data["pos_fst"]["id_to_string"]
        self.pos_fst.next_id = data["pos_fst"]["next_id"]

        self.lemma_fst.string_to_id = data["lemma_fst"]["string_to_id"]
        self.lemma_fst.id_to_string = data["lemma_fst"]["id_to_string"]
        self.lemma_fst.next_id = data["lemma_fst"]["next_id"]

        self._built = True
        self._search_cache = {}
        self._exists_cache = {}

        print(f"Double Array Trie 로드 완료: {filepath}")

    def clear_cache(self):
        """검색 캐시 초기화"""
        self._search_cache = {}
        self._exists_cache = {}

    def get_stats(self) -> Dict:
        """통계 정보"""
        if not self._built:
            return {}

        return {
            "array_size": len(self.base),
            "memory_kb": (
                len(self.base) * 4  # int
                + len(self.check) * 4
                + len(self.value) * 8  # 포인터
            )
            / 1024,
            "pos_count": self.pos_fst.size(),
            "lemma_count": self.lemma_fst.size(),
            "cache_size": len(self._search_cache),
        }

    def __len__(self) -> int:
        """단어 수"""
        if not self._built:
            return len(set(word for word, _, _ in self._build_data))

        count = sum(1 for v in self.value if v is not None)
        return count

    def __contains__(self, word: str) -> bool:
        return self.exists(word)


# Fallback: Python Trie
class PythonTrieFallback:
    """Double Array Trie가 실패할 때 사용하는 기본 Trie"""

    def __init__(self):
        from .trie import Trie

        self._trie = Trie()
        self._built = False

    def insert(self, word: str, pos: str, lemma: Optional[str] = None):
        self._trie.insert(word, pos, lemma)

    def build(self):
        self._trie.build_aho_corasick()
        self._built = True

    def exists(self, word: str) -> bool:
        return self._trie.exists(word)

    def search_all_patterns(self, text: str):
        return self._trie.search_all_patterns(text)

    def get_patterns(self, word: str) -> List[Tuple[str, str]]:
        patterns = self._trie.search_all_patterns(word)
        result = []
        for start, end, pattern_list in patterns:
            if start == 0 and end == len(word):
                result.extend(pattern_list)
        return result

    def save(self, filepath: str):
        import pickle

        # Save as flat list to avoid recursion error
        # Trie class supports __iter__ which yields (word, pos, lemma)
        data = list(self._trie)

        with open(filepath, "wb") as f:
            pickle.dump(data, f)

    def load(self, filepath: str):
        import pickle

        with open(filepath, "rb") as f:
            data = pickle.load(f)

        # Rebuild Trie
        for word, pos, lemma in data:
            self._trie.insert(word, pos, lemma)

        self._built = True

    def clear_cache(self):
        pass

    def get_stats(self) -> Dict:
        return {}

    def __len__(self) -> int:
        return len(self._trie)

    def __contains__(self, word: str) -> bool:
        return self.exists(word)

    def __iter__(self):
        return iter(self._trie)


# Factory 함수
def create_trie(use_double_array: bool = True):
    """
    Trie 생성 (자동 선택)

    Args:
        use_double_array: True면 Double Array Trie, False면 Python Trie
    """
    if use_double_array:
        try:
            return DoubleArrayTrie()
        except Exception as e:
            print(f"⚠ Double Array Trie 생성 실패: {e}")
            return PythonTrieFallback()
    else:
        return PythonTrieFallback()


__all__ = ["DoubleArrayTrie", "FST", "PythonTrieFallback", "create_trie"]
