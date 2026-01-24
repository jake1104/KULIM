
import re
from typing import List


class Preprocessor:
    """텍스트 전처리기"""
    
    # 문장 분리: 마침표, 느낌표, 물음표 + 공백
    _SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?。!?])\s+")
    
    # 토큰 패턴: 한글, 영문, 숫자, 한자, 특수문자 등을 구분
    _TOKEN_RE = re.compile(
        r"[가-힣]+|"           # 한글
        r"[A-Za-z]+|"          # 영문
        r"[0-9]+(?:\.[0-9]+)?|"  # 숫자 (소수점 포함)
        r"[一-龥龜]+|"         # 한자
        r"[,;:·]|"             # 구두점
        r"[.!?。!?]+|"       # 문장 종결
        r"[\"'(){}[\]―—~…]+|" # 인용/괄호/기타
        r"[^\w\s]+",           # 기타 특수문자
        re.UNICODE
    )
    
    _WHITESPACE_RE = re.compile(r"\s+")
    
    # 비통사적 합성어 패턴 (사전에서 처리 불가능한 생산적 패턴)
    # 이런 패턴들은 토큰화 단계에서 하나의 토큰으로 유지
    _COMPOUND_PATTERNS = [
        # 학교 관련 (지명 + 학교명)
        re.compile(r"^[가-힣]+대학교$"),     # ~대학교
        re.compile(r"^[가-힣]+고등학교$"),   # ~고등학교
        re.compile(r"^[가-힣]+중학교$"),     # ~중학교
        re.compile(r"^[가-힣]+초등학교$"),   # ~초등학교
        re.compile(r"^[가-힣]+유치원$"),     # ~유치원
        
        # 기관 관련
        re.compile(r"^[가-힣]+시립$"),       # ~시립
        re.compile(r"^[가-힣]+국립$"),       # ~국립
        re.compile(r"^[가-힣]+도립$"),       # ~도립
        
        # 동사 파생 명사 (생산적 파생)
        re.compile(r"^[가-힣]+(하다|되다|시키다)$"),  # ~하다, ~되다, ~시키다
        re.compile(r"^[가-힣]+거리$"),       # ~거리 (먹거리, 볼거리)
    ]
    
    # 통사적 합성어 감지 규칙
    # 이런 것들은 나중에 형태소 분석기가 자동으로 분리함
    @staticmethod
    def is_syntactic_compound(token: str) -> bool:
        """
        통사적 합성어인지 확인 (규칙으로 감지 가능)
        통사적 합성어는 일반 문법 규칙으로 결합된 것
        예: 학교 + 에 → 학교에 (명사 + 조사)
        """
        # 여기서는 특별히 처리할 필요 없음
        # 형태소 분석기가 자동으로 분리함
        return False

    def split_sentence(self, text: str) -> List[str]:
        """텍스트를 문장 단위로 분리"""
        text = text.strip()
        sentences = self._SENTENCE_SPLIT_RE.split(text)
        return [s for s in sentences if s.strip()]

    def tokenize(self, sentence: str) -> List[str]:
        """문장을 토큰으로 분리"""
        s = self._WHITESPACE_RE.sub(" ", sentence).strip()
        tokens = self._TOKEN_RE.findall(s)
        
        # 비통사적 합성어 패턴 체크
        # 이런 패턴에 매칭되면 하나의 토큰으로 유지
        result = []
        for token in tokens:
            is_compound = False
            for pattern in self._COMPOUND_PATTERNS:
                if pattern.match(token):
                    result.append(token)
                    is_compound = True
                    break
            
            if not is_compound:
                result.append(token)
        
        return result

    def preprocess(self, text: str) -> List[List[str]]:
        """텍스트 전처리: 문장 분리 + 토큰화"""
        sentences = self.split_sentence(text)
        return [self.tokenize(s) for s in sentences]
