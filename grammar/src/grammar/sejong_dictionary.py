from typing import Dict, List, Tuple
import os
import csv


# 세종 품사 태그 매핑
SEJONG_POS_MAP = {
    # 명사류
    "NNG": "NNG",  # 일반 명사
    "NNP": "NNP",  # 고유 명사
    "NNB": "NNB",  # 의존 명사
    "NR": "NR",  # 수사
    "NP": "NP",  # 대명사
    # 동사
    "VV": "VV",  # 동사
    "VA": "VA",  # 형용사
    "VX": "VX",  # 보조 용언
    "VCP": "VCP",  # 긍정 지정사
    "VCN": "VCN",  # 부정 지정사
    # 관형사, 부사
    "MM": "MM",  # 관형사
    "MAG": "MAG",  # 일반 부사
    "MAJ": "MAJ",  # 접속 부사
    # 조사
    "JKS": "JKS",  # 주격 조사
    "JKC": "JKC",  # 보격 조사
    "JKG": "JKG",  # 관형격 조사
    "JKO": "JKO",  # 목적격 조사
    "JKB": "JKB",  # 부사격 조사
    "JKV": "JKV",  # 호격 조사
    "JKQ": "JKQ",  # 인용격 조사
    "JX": "JX",  # 보조사
    "JC": "JC",  # 접속 조사
    # 어미
    "EP": "EP",  # 선어말 어미
    "EF": "EF",  # 종결 어미
    "EC": "EC",  # 연결 어미
    "ETN": "ETN",  # 명사형 전성 어미
    "ETM": "ETM",  # 관형형 전성 어미
    # 접두사, 접미사
    "XPN": "XPN",  # 체언 접두사
    "XSN": "XSN",  # 명사 파생 접미사
    "XSV": "XSV",  # 동사 파생 접미사
    "XSA": "XSA",  # 형용사 파생 접미사
    # 기타
    "SF": "SF",  # 마침표, 물음표, 느낌표
    "SP": "SP",  # 쉼표, 가운뎃점, 콜론, 빗금
    "SS": "SS",  # 따옴표, 괄호표, 줄표
    "SE": "SE",  # 줄임표
    "SO": "SO",  # 붙임표
    "SW": "SW",  # 기타 기호
    "SL": "SL",  # 외국어
    "SH": "SH",  # 한자
    "SN": "SN",  # 숫자
}


class SejongDictionary:
    """
    세종 전자사전 파서 (CSV 기반)
    """

    def __init__(self):
        self.words = {}

    def load_builtin_dictionary(
        self, load_defaults: bool = True
    ) -> Dict[str, List[Tuple[str, str]]]:
        """
        사전 로드
        :param load_defaults: True이면 내장 CSV/상수 로드. False면 빈 상태 시작.
        """
        if not load_defaults:
            self.words = {}
            return {}

        csv_path = os.path.join(os.path.dirname(__file__), "data", "dictionary.csv")

        if not os.path.exists(csv_path):
            print(f"Warning: Dictionary file not found at {csv_path}")
            return {}

        words = {}

        try:
            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                next(reader, None)  # Skip header

                for row in reader:
                    if len(row) < 3:
                        continue
                    word, pos, lemma = row

                    if word not in words:
                        words[word] = []
                    # 중복 제거
                    if (pos, lemma) not in words[word]:
                        words[word].append((pos, lemma))

            self.words = words
            return words

        except Exception as e:
            print(f"Error loading dictionary: {e}")
            return {}

    def get_stats(self) -> Dict:
        """사전 통계"""
        if not self.words:
            self.load_builtin_dictionary()

        pos_count = {}
        for word, patterns in self.words.items():
            for pos, lemma in patterns:
                pos_count[pos] = pos_count.get(pos, 0) + 1

        return {
            "total_words": len(self.words),
            "total_patterns": sum(len(p) for p in self.words.values()),
            "pos_distribution": pos_count,
        }
