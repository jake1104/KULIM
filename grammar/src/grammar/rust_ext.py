from typing import List, Tuple, Optional

try:
    # Try importing as sub-module first (maturin config: grammar.kulim_rust)
    from . import kulim_rust
    from .kulim_rust import RustTrie

    HAS_RUST = True
except ImportError:
    try:
        # Fallback to direct import (legacy or development)
        import kulim_rust
        from kulim_rust import RustTrie

        HAS_RUST = True
    except ImportError:
        HAS_RUST = False
        RustTrie = None


class RustTrieWrapper:
    """
    Rust Trie 래퍼
    Rust가 없으면 Python fallback
    """

    def __init__(self, use_rust: bool = True):
        self.use_rust = use_rust and HAS_RUST

        if self.use_rust:
            self.rust_trie = RustTrie()
        else:
            # Python fallback
            self.py_dict = {}

    def save(self, path: str):
        """Rust Trie 저장"""
        if self.use_rust:
            try:
                # Use standalone function
                kulim_rust.save_trie(self.rust_trie, path)
            except Exception as e:
                print(f"Rust Trie save failed: {e}")

    def load(self, path: str):
        """Rust Trie 로드"""
        if self.use_rust:
            try:
                # Use standalone function, returns new RustTrie instance
                self.rust_trie = kulim_rust.load_trie(path)
            except Exception as e:
                print(f"Rust Trie load failed: {e}")

    def insert(self, word: str, pos: str, lemma: str):
        """단어 삽입"""
        if self.use_rust:
            self.rust_trie.insert(word, pos, lemma)
        else:
            if word not in self.py_dict:
                self.py_dict[word] = []
            self.py_dict[word].append((pos, lemma))

    def search(self, word: str) -> List[Tuple[str, str]]:
        """검색"""
        if self.use_rust:
            return self.rust_trie.search(word)
        else:
            return self.py_dict.get(word, [])

    def exists(self, word: str) -> bool:
        """존재 확인"""
        if self.use_rust:
            return self.rust_trie.exists(word)
        else:
            return word in self.py_dict

    def search_all_patterns(
        self, text: str
    ) -> List[Tuple[int, int, List[Tuple[str, str]]]]:
        """
        모든 패턴 검색 (Aho-Corasick 유사)

        Returns:
            [(start_idx, length, [(pos, lemma), ...]), ...]
        """
        if self.use_rust:
            # Rust 구현 사용 (lib.rs에 추가됨)
            try:
                return self.rust_trie.search_all_patterns(text)
            except AttributeError:
                # 구버전 Rust 모듈인 경우 fallback
                pass

            # Rust에 search_all_patterns가 없는 경우 Python fallback
            results = []
            n = len(text)
            for i in range(n):
                for j in range(i + 1, min(i + 10, n + 1)):  # 최대 길이 제한
                    word = text[i:j]
                    if self.rust_trie.exists(word):
                        patterns = self.rust_trie.search(word)
                        if patterns:
                            results.append((i, len(word), patterns))
            return results
        else:
            results = []
            n = len(text)
            for i in range(n):
                for j in range(i + 1, min(i + 10, n + 1)):
                    word = text[i:j]
                    if word in self.py_dict:
                        results.append((i, len(word), self.py_dict[word]))
            return results

    def analyze(self, text: str) -> List[Tuple[str, str, str]]:
        """
        Rust Viterbi 분석
        Returns:
             [(surface, pos, lemma), ...]
        """
        if self.use_rust:
            try:
                return self.rust_trie.analyze(text)
            except AttributeError:
                print("Warning: Rust analyze method not found")
                return []
            except Exception as e:
                print(f"Rust analyze error: {e}")
                return []
        return []

    def search_batch(self, words: List[str]) -> List[List[Tuple[str, str]]]:
        """배치 검색"""
        if self.use_rust:
            return self.rust_trie.search_batch(words)
        else:
            return [self.search(word) for word in words]

    def get_stats(self) -> dict:
        """통계"""
        if self.use_rust:
            # Rust Trie의 get_stats 반환값에 따라 조정 필요
            try:
                nodes, patterns = self.rust_trie.get_stats()
                return {"nodes": nodes, "patterns": patterns, "backend": "rust"}
            except:
                return {"backend": "rust", "status": "stats_unavailable"}
        else:
            return {
                "words": len(self.py_dict),
                "patterns": sum(len(p) for p in self.py_dict.values()),
                "backend": "python",
            }


def get_rust_info() -> dict:
    """Rust 정보"""
    return {
        "available": HAS_RUST,
        "module": "kulim_rust" if HAS_RUST else None,
        "message": (
            "Rust extension loaded" if HAS_RUST else "Rust not available, using Python"
        ),
    }


if __name__ == "__main__":
    # 테스트
    print("Rust 확장 모듈 테스트\n")
    print(f"Rust 사용 가능: {HAS_RUST}")

    if HAS_RUST:
        trie = RustTrieWrapper(use_rust=True)
        trie.insert("친구", "NNG", "친구")
        trie.insert("학교", "NNG", "학교")

        print(f"\n검색 '친구': {trie.search('친구')}")
        print(f"존재 '친구': {trie.exists('친구')}")
        print(f"통계: {trie.get_stats()}")
    else:
        print("\nRust 모듈이 설치되지 않았습니다.")
        print("빌드 방법:")
        print("  1. Rust 설치: https://rustup.rs/")
        print("  2. pip install maturin")
        print("  3. cd grammar/beta/v03/rust")
        print("  4. maturin develop --release")
