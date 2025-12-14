
import numpy as np
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass


@dataclass
class Morpheme:
    """형태소 정보"""

    surface: str  # 표면형
    pos: str  # 품사
    lemma: str  # 기본형
    start: int  # 시작 위치
    end: int  # 끝 위치
    cost: float  # 비용


class DPMorphemeAnalyzer:
    """
    동적 프로그래밍 기반 형태소 분석

    알고리즘:
    - dp[i] = text[0:i]까지의 최소 비용
    - Viterbi와 유사하지만, 품사 전이가 아닌 형태소 비용 기반

    비용 함수:
    1. 사전 등재 여부 (가중치 높음)
    2. 형태소 길이 (너무 짧거나 길면 패널티)
    3. 품사 전이 확률 (HMM 기반)
    4. 미등록어 패널티
    5. 복합어 보너스
    """

    def __init__(self, trie, hmm=None, use_gpu=False):
        """
        Args:
            trie: Trie 객체 (사전)
            hmm: HMM 모델 (선택)
            use_gpu: GPU 사용 (CuPy)
        """
        self.trie = trie
        self.hmm = hmm
        self.use_gpu = use_gpu

        # 품사 전이 가중치 (간소화)
        self.pos_transition_weight = 5.0

        # 비용 가중치
        self.weights = {
            "in_dict": -10.0,  # 사전 등재 (큰 보너스)
            "length_short": 3.0,  # 짧은 형태소 패널티
            "length_long": 2.0,  # 긴 형태소 패널티
            "unknown": 20.0,  # 미등록어 패널티
            "compound": -5.0,  # 복합어 보너스
        }

    def analyze(self, text: str, top_k: int = 1) -> List[List[Morpheme]]:
        """
        DP로 형태소 분석

        Args:
            text: 입력 텍스트
            top_k: 상위 k개 결과 반환

        Returns:
            상위 k개 분석 결과
        """
        if not text:
            return [[]]

        n = len(text)

        # DP 테이블
        # dp[i] = text[0:i]까지의 최소 비용과 경로
        dp = [float("inf")] * (n + 1)
        path = [None] * (n + 1)
        dp[0] = 0.0

        # 모든 위치에서 가능한 형태소 후보 탐색
        for i in range(n):
            if dp[i] == float("inf"):
                continue  # 도달 불가

            # i부터 시작하는 모든 가능한 형태소
            for j in range(i + 1, min(i + 16, n + 1)):  # 최대 15자
                surface = text[i:j]

                # Trie에서 패턴 검색
                patterns = self._get_patterns(surface)

                if patterns:
                    # 사전 등재 형태소
                    for pos, lemma in patterns:
                        cost = self._compute_cost(
                            surface=surface,
                            pos=pos,
                            lemma=lemma,
                            start=i,
                            end=j,
                            text=text,
                            prev_pos=self._get_prev_pos(path, i),
                        )

                        total_cost = dp[i] + cost

                        if total_cost < dp[j]:
                            dp[j] = total_cost
                            path[j] = Morpheme(
                                surface=surface,
                                pos=pos,
                                lemma=lemma,
                                start=i,
                                end=j,
                                cost=cost,
                            )
                else:
                    # 미등록어 처리
                    cost = self._compute_unknown_cost(surface, i, j, text)
                    total_cost = dp[i] + cost

                    if total_cost < dp[j]:
                        dp[j] = total_cost
                        path[j] = Morpheme(
                            surface=surface,
                            pos=self._guess_pos(surface),
                            lemma=surface,
                            start=i,
                            end=j,
                            cost=cost,
                        )

        # 역추적
        result = self._backtrack(path, n)

        if top_k == 1:
            return [result]
        else:
            # 상위 k개 경로 (간소화 - beam search 필요)
            return [result]

    def _get_patterns(self, word: str) -> List[Tuple[str, str]]:
        """Trie에서 패턴 조회"""
        if hasattr(self.trie, "search"):
            result = self.trie.search(word)
            if result:
                return result

        # search_all_patterns 사용
        if hasattr(self.trie, "search_all_patterns"):
            all_patterns = self.trie.search_all_patterns(word)
            if all_patterns:
                # 전체 단어와 일치하는 패턴만
                for start, end, patterns in all_patterns:
                    if start == 0 and end == len(word):
                        return patterns

        return []

    def _compute_cost(
        self,
        surface: str,
        pos: str,
        lemma: str,
        start: int,
        end: int,
        text: str,
        prev_pos: Optional[str],
    ) -> float:
        """
        형태소 비용 계산

        낮을수록 좋은 분석
        """
        cost = 0.0
        length = len(surface)

        # 1. 사전 등재 보너스
        cost += self.weights["in_dict"]

        # 2. 길이 패널티
        if length == 1:
            cost += self.weights["length_short"]
        elif length > 10:
            cost += self.weights["length_long"]

        # 3. 품사 전이
        if prev_pos and self.hmm:
            transition = self.hmm.get_transition(prev_pos, pos)
            cost -= transition * self.pos_transition_weight
        elif prev_pos:
            # 간단한 전이 규칙
            cost += self._simple_transition_cost(prev_pos, pos)

        # 4. 복합어 보너스
        if self._is_compound(surface, pos):
            cost += self.weights["compound"]

        return cost

    def _compute_unknown_cost(
        self, surface: str, start: int, end: int, text: str
    ) -> float:
        """미등록어 비용"""
        cost = self.weights["unknown"]

        # 길이가 긴 미등록어는 더 큰 패널티
        if len(surface) > 5:
            cost += 10.0

        # 한글이 아니면 패널티 감소 (외래어, 숫자 등)
        if not all("가" <= ch <= "힣" for ch in surface):
            cost -= 10.0

        return cost

    def _simple_transition_cost(self, prev_pos: str, curr_pos: str) -> float:
        """간단한 품사 전이 비용"""
        # 선호하는 전이
        good_transitions = [
            ("NNG", "JKS"),  # 명사 + 주격조사
            ("NNG", "JKO"),  # 명사 + 목적격조사
            ("NNG", "JKB"),  # 명사 + 부사격조사
            ("VV", "EP"),  # 동사 + 선어말어미
            ("VV", "EC"),  # 동사 + 연결어미
            ("VV", "EF"),  # 동사 + 종결어미
            ("VA", "EP"),  # 형용사 + 선어말어미
            ("VA", "EF"),  # 형용사 + 종결어미
            ("MAG", "VV"),  # 부사 + 동사
            ("MAG", "VA"),  # 부사 + 형용사
        ]

        if (prev_pos, curr_pos) in good_transitions:
            return -2.0  # 보너스

        # 같은 대분류 전이는 중립
        if prev_pos[0] == curr_pos[0]:
            return 0.0

        # 그 외는 약간 패널티
        return 1.0

    def _is_compound(self, surface: str, pos: str) -> bool:
        """복합어 판단 (간소화)"""
        # 2음절 이상 명사면 복합어 가능성
        if pos.startswith("N") and len(surface) >= 2:
            return True
        return False

    def _guess_pos(self, surface: str) -> str:
        """미등록어 품사 추정"""
        # 한글이 아니면
        if not all("가" <= ch <= "힣" for ch in surface):
            if surface.isdigit():
                return "SN"  # 숫자
            elif surface.isalpha():
                return "SL"  # 외국어
            else:
                return "SW"  # 기호

        # 한글이면 명사로 추정
        return "NNG"

    def _get_prev_pos(self, path: List, pos: int) -> Optional[str]:
        """이전 형태소의 품사"""
        if pos == 0:
            return None

        # 역으로 추적
        current = pos
        while current > 0:
            if path[current] is not None:
                return path[current].pos
            current -= 1

        return None

    def _backtrack(self, path: List, end: int) -> List[Morpheme]:
        """경로 역추적"""
        result = []
        current = end

        while current > 0:
            if path[current] is None:
                break

            morpheme = path[current]
            result.append(morpheme)
            current = morpheme.start

        result.reverse()
        return result

    def get_cost_breakdown(self, morphemes: List[Morpheme]) -> Dict:
        """비용 분석"""
        total_cost = sum(m.cost for m in morphemes)

        return {
            "total_cost": total_cost,
            "avg_cost_per_morpheme": total_cost / len(morphemes) if morphemes else 0,
            "morpheme_count": len(morphemes),
            "morphemes": [(m.surface, m.pos, m.cost) for m in morphemes],
        }


if __name__ == "__main__":
    # 테스트
    print("DP 형태소 분석기 테스트\n")

    # 가상 Trie (실제로는 build_comprehensive_trie 사용)
    class DummyTrie:
        def __init__(self):
            self.words = {
                "친구": [("NNG", "친구")],
                "가": [("JKS", "가")],
                "학교": [("NNG", "학교")],
                "에": [("JKB", "에")],
                "가다": [("VV", "가다")],
                "갔": [("VV", "가다")],
                "습니다": [("EF", "습니다")],
                ".": [("SF", ".")],
            }

        def search(self, word):
            return self.words.get(word, None)

    trie = DummyTrie()
    analyzer = DPMorphemeAnalyzer(trie)

    # 테스트 문장
    test_sentences = [
        "친구가학교에갔습니다.",  # 띄어쓰기 없음
        "친구학교",  # 복합어
    ]

    for sent in test_sentences:
        print(f"\n문장: {sent}")
        results = analyzer.analyze(sent)

        for result in results:
            morphemes_str = " + ".join(f"{m.surface}/{m.pos}" for m in result)
            print(f"결과: {morphemes_str}")

            # 비용 분석
            breakdown = analyzer.get_cost_breakdown(result)
            print(
                f"비용: 총={breakdown['total_cost']:.2f}, "
                f"평균={breakdown['avg_cost_per_morpheme']:.2f}"
            )
