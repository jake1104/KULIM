
import time
import sys
from collections import OrderedDict, defaultdict
from typing import Any, Optional


class LRUCache:
    """LRU (Least Recently Used) 캐시"""

    def __init__(self, capacity: int):
        self.cache: OrderedDict = OrderedDict()
        self.capacity = capacity
        self.hits = 0
        self.misses = 0

    def get(self, key) -> Optional[Any]:
        if key not in self.cache:
            self.misses += 1
            return None
        self.hits += 1
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key, value) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)

    def clear(self) -> None:
        self.cache.clear()
        self.hits = 0
        self.misses = 0

    def get_hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    def __len__(self) -> int:
        return len(self.cache)


class TTLCache:
    """TTL (Time To Live) + LRU 캐시"""

    def __init__(self, capacity: int, ttl: float):
        self.cache: OrderedDict = OrderedDict()
        self.capacity = capacity
        self.ttl = ttl  # seconds
        self.hits = 0
        self.misses = 0

    def get(self, key) -> Optional[Any]:
        if key not in self.cache:
            self.misses += 1
            return None
        value, timestamp = self.cache[key]
        if time.time() - timestamp > self.ttl:
            del self.cache[key]
            self.misses += 1
            return None
        self.hits += 1
        self.cache.move_to_end(key)
        return value

    def put(self, key, value) -> None:
        timestamp = time.time()
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = (value, timestamp)
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)

    def clear(self) -> None:
        self.cache.clear()
        self.hits = 0
        self.misses = 0

    def get_hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    def __len__(self) -> int:
        return len(self.cache)


class LFUCache:
    """
    LFU (Least Frequently Used) 캐시

    접근 빈도가 가장 낮은 항목부터 제거
    """

    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache: dict = {}
        self.freq: dict = {}
        self.freq_list: dict = defaultdict(OrderedDict)
        self.min_freq: int = 0
        self.hits = 0
        self.misses = 0

    def get(self, key) -> Optional[Any]:
        if key not in self.cache:
            self.misses += 1
            return None

        self.hits += 1
        self._update_freq(key)
        return self.cache[key]

    def put(self, key, value) -> None:
        if self.capacity <= 0:
            return

        if key in self.cache:
            self.cache[key] = value
            self._update_freq(key)
            return

        if len(self.cache) >= self.capacity:
            self._evict()

        self.cache[key] = value
        self.freq[key] = 1
        self.freq_list[1][key] = None
        self.min_freq = 1

    def _update_freq(self, key):
        freq = self.freq[key]
        del self.freq_list[freq][key]

        if not self.freq_list[freq] and self.min_freq == freq:
            self.min_freq += 1

        self.freq[key] = freq + 1
        self.freq_list[freq + 1][key] = None

    def _evict(self):
        key, _ = self.freq_list[self.min_freq].popitem(last=False)
        del self.cache[key]
        del self.freq[key]

    def clear(self) -> None:
        self.cache.clear()
        self.freq.clear()
        self.freq_list.clear()
        self.min_freq = 0
        self.hits = 0
        self.misses = 0

    def get_hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    def __len__(self) -> int:
        return len(self.cache)

    def get_stats(self) -> dict:
        freq_distribution = {}
        for f, keys in self.freq_list.items():
            freq_distribution[f] = len(keys)

        return {
            "size": len(self.cache),
            "capacity": self.capacity,
            "min_freq": self.min_freq,
            "freq_distribution": freq_distribution,
            "hit_rate": self.get_hit_rate(),
        }


class HierarchicalCache:
    """
    계층적 캐시 (L1 + L2)

    L1: 작고 빠른 LRU 캐시
    L2: 큰 LFU 캐시

    캐시 히트율 80% 목표
    """

    def __init__(self, l1_size: int = 100, l2_size: int = 1000):
        self.l1 = LRUCache(l1_size)  # 빠른 접근
        self.l2 = LFUCache(l2_size)  # 빈도 기반
        self.hits = 0
        self.misses = 0

    def get(self, key) -> Optional[Any]:
        # L1 확인
        result = self.l1.get(key)
        if result is not None:
            self.hits += 1
            return result

        # L2 확인
        result = self.l2.get(key)
        if result is not None:
            self.hits += 1
            # L1으로 승격
            self.l1.put(key, result)
            return result

        self.misses += 1
        return None

    def put(self, key, value) -> None:
        # L1과 L2 모두에 저장
        self.l1.put(key, value)
        self.l2.put(key, value)

    def clear(self) -> None:
        self.l1.clear()
        self.l2.clear()
        self.hits = 0
        self.misses = 0

    def get_hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    def get_stats(self) -> dict:
        return {
            "l1_size": len(self.l1),
            "l2_size": len(self.l2),
            "l1_hit_rate": self.l1.get_hit_rate(),
            "l2_hit_rate": self.l2.get_hit_rate(),
            "total_hit_rate": self.get_hit_rate(),
        }

    def __len__(self) -> int:
        return len(self.l1) + len(self.l2)


class AdaptiveCache:
    """
    적응형 캐시

    메모리 압박 시 자동으로 크기 조절
    메모리 효율 극대화
    """

    def __init__(self, max_memory_mb: int = 100):
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.cache: OrderedDict = OrderedDict()
        self.hits = 0
        self.misses = 0

    def get(self, key) -> Optional[Any]:
        if key not in self.cache:
            self.misses += 1
            return None

        self.hits += 1
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key, value) -> None:
        # 메모리 체크
        current_memory = self._get_cache_memory()

        if current_memory > self.max_memory_bytes:
            self._evict_half()

        if key in self.cache:
            self.cache.move_to_end(key)

        self.cache[key] = value

    def _get_cache_memory(self) -> int:
        """캐시 메모리 사용량 추정 (바이트)"""
        total = 0
        for k, v in self.cache.items():
            total += sys.getsizeof(k)
            total += sys.getsizeof(v)
        return total

    def _evict_half(self):
        """캐시의 절반 제거 (LRU 방식)"""
        items = list(self.cache.items())
        keep_count = len(items) // 2

        self.cache = OrderedDict(items[keep_count:])

    def clear(self) -> None:
        self.cache.clear()
        self.hits = 0
        self.misses = 0

    def get_hit_rate(self) -> float:
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    def get_stats(self) -> dict:
        return {
            "size": len(self.cache),
            "memory_bytes": self._get_cache_memory(),
            "memory_mb": self._get_cache_memory() / (1024 * 1024),
            "max_memory_mb": self.max_memory_bytes / (1024 * 1024),
            "hit_rate": self.get_hit_rate(),
        }

    def __len__(self) -> int:
        return len(self.cache)


# Factory 함수
def create_cache(strategy: str = "hierarchical", **kwargs):
    """
    캐시 생성 팩토리

    Args:
        strategy: 'lru', 'lfu', 'ttl', 'hierarchical', 'adaptive'
        **kwargs: 각 캐시 타입별 파라미터

    Returns:
        캐시 인스턴스
    """
    if strategy == "lru":
        return LRUCache(kwargs.get("capacity", 1000))
    elif strategy == "lfu":
        return LFUCache(kwargs.get("capacity", 1000))
    elif strategy == "ttl":
        return TTLCache(kwargs.get("capacity", 1000), kwargs.get("ttl", 300))
    elif strategy == "hierarchical":
        return HierarchicalCache(
            kwargs.get("l1_size", 100), kwargs.get("l2_size", 1000)
        )
    elif strategy == "adaptive":
        return AdaptiveCache(kwargs.get("max_memory_mb", 100))
    else:
        # 기본값
        return HierarchicalCache()


if __name__ == "__main__":
    # 테스트
    print("=== Hierarchical Cache Test ===")
    cache = HierarchicalCache(l1_size=3, l2_size=5)

    # 데이터 저장
    for i in range(10):
        cache.put(f"key{i}", f"value{i}")

    # 접근 패턴
    for key in ["key5", "key6", "key7", "key5", "key5"]:
        result = cache.get(key)
        print(f"get({key}) = {result}")

    print(f"\nStats: {cache.get_stats()}")
    print(f"Hit rate: {cache.get_hit_rate():.2%}")

    print("\n=== Adaptive Cache Test ===")
    adaptive = AdaptiveCache(max_memory_mb=1)

    for i in range(100):
        adaptive.put(f"key{i}", "x" * 1000)

    print(f"Stats: {adaptive.get_stats()}")
