"""
KULIM POS Tag Set (TTAK.KO-11.0010/R1)
=======================================
한국정보통신기술협회(TTA) 표준: 한국어 형태소 및 품사 태그 부착 지침
(Standard Guidelines for Korean Morphological Analysis and POS Tagging)

Reference: TTAK.KO-11.0010/R1
"""

# 체언 (N)
NNG = "NNG"  # 일반 명사 (Common Noun)
NNP = "NNP"  # 고유 명사 (Proper Noun)
NNB = "NNB"  # 의존 명사 (Bound Noun)
NR = "NR"  # 수사 (Numeral)
NP = "NP"  # 대명사 (Pronoun)

# 용언 (V)
VV = "VV"  # 동사 (Verb)
VA = "VA"  # 형용사 (Adjective)
VX = "VX"  # 보조 용언 (Auxiliary Verb/Adjective)
VCP = "VCP"  # 긍정 지정사 (Positive Copula) - 이다
VCN = "VCN"  # 부정 지정사 (Negative Copula) - 아니다

# 수식언 (M)
MM = "MM"  # 관형사 (Determiner)
MAG = "MAG"  # 일반 부사 (General Adverb)
MAJ = "MAJ"  # 접속 부사 (Conjunctive Adverb)

# 독립언 (I)
IC = "IC"  # 감탄사 (Interjection)

# 관계언 (J)
JKS = "JKS"  # 주격 조사 (Subject Case Particle)
JKC = "JKC"  # 보격 조사 (Complement Case Particle)
JKG = "JKG"  # 관형격 조사 (Adnominal Case Particle)
JKO = "JKO"  # 목적격 조사 (Object Case Particle)
JKB = "JKB"  # 부사격 조사 (Adverbial Case Particle)
JKV = "JKV"  # 호격 조사 (Vocative Case Particle)
JKQ = "JKQ"  # 인용격 조사 (Quote Case Particle)
JX = "JX"  # 보조사 (Auxiliary Particle)
JC = "JC"  # 접속 조사 (Conjunctive Particle)

# 선어말어미 (E)
EP = "EP"  # 선어말어미 (Pre-final Ending)

# 어말어미 (E)
EF = "EF"  # 종결 어미 (Final Ending)
EC = "EC"  # 연결 어미 (Connective Ending)
ETN = "ETN"  # 명사형 전성 어미 (Nominalizer Ending)
ETM = "ETM"  # 관형사형 전성 어미 (Adnominalizer Ending)

# 접두사 (X)
XPN = "XPN"  # 체언 접두사 (Noun Prefix)

# 접미사 (X)
XSN = "XSN"  # 명사 파생 접미사 (Noun Suffix)
XSV = "XSV"  # 동사 파생 접미사 (Verb Suffix)
XSA = "XSA"  # 형용사 파생 접미사 (Adjective Suffix)

# 어근 (X)
XR = "XR"  # 어근 (Root)

# 기호 (S)
SF = "SF"  # 마침표, 물음표, 느낌표 (Terminal Punctuation)
SP = "SP"  # 쉼표, 가운뎃점, 콜론, 빗금 (Comma, Colon, Slash)
SS = "SS"  # 따옴표, 괄호, 줄표 (Quote, Parenthesis, Dash)
SE = "SE"  # 줄임표 (Ellipsis)
SO = "SO"  # 붙임표 (Hyphen)
SW = "SW"  # 기타 기호 (Other Symbols - Math, Currency)

# 외국어 및 기타
SL = "SL"  # 외국어 (Foreign Language)
SH = "SH"  # 한자 (Chinese Character)
SN = "SN"  # 숫자 (Number)

# 분석 불능
NA = "NA"  # 분석 불능 (Not Analyzed)


# 태그 그룹 (Convenience Sets)
NOUNS = {NNG, NNP, NNB, NR, NP}
VERBS = {VV, VA, VX, VCP, VCN}
ADVERBS = {MAG, MAJ}
PARTICLES = {JKS, JKC, JKG, JKO, JKB, JKV, JKQ, JX, JC}
ENDINGS = {EP, EF, EC, ETN, ETM}
SYMBOLS = {SF, SP, SS, SE, SO, SW}


def get_description(tag: str) -> str:
    """태그 설명 반환"""
    descriptions = {
        NNG: "일반 명사",
        NNP: "고유 명사",
        NNB: "의존 명사",
        NR: "수사",
        NP: "대명사",
        VV: "동사",
        VA: "형용사",
        VX: "보조 용언",
        VCP: "긍정 지정사",
        VCN: "부정 지정사",
        MM: "관형사",
        MAG: "일반 부사",
        MAJ: "접속 부사",
        IC: "감탄사",
        JKS: "주격 조사",
        JKC: "보격 조사",
        JKG: "관형격 조사",
        JKO: "목적격 조사",
        JKB: "부사격 조사",
        JKV: "호격 조사",
        JKQ: "인용격 조사",
        JX: "보조사",
        JC: "접속 조사",
        EP: "선어말어미",
        EF: "종결 어미",
        EC: "연결 어미",
        ETN: "명사형 전성 어미",
        ETM: "관형사형 전성 어미",
        XPN: "체언 접두사",
        XSN: "명사 파생 접미사",
        XSV: "동사 파생 접미사",
        XSA: "형용사 파생 접미사",
        XR: "어근",
        SF: "마침표/물음표/느낌표",
        SP: "쉼표/가운뎃점/콜론",
        SS: "따옴표/괄호",
        SE: "줄임표",
        SO: "붙임표",
        SW: "기타 기호",
        SL: "외국어",
        SH: "한자",
        SN: "숫자",
        NA: "분석 불능",
    }
    return descriptions.get(tag, "미등록 태그")
