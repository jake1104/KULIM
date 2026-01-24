from typing import Union, List, Tuple
import os

# v03에서 v02 모듈 import (절대 경로)
try:
    from .trie_da import DoubleArrayTrie, create_trie
    from .trie import Trie
except ImportError as e:
    print(f"Warning: Could not import trie modules: {e}")
    DoubleArrayTrie = None
    Trie = None
    create_trie = None

# v03 세종 사전
# v03 세종 사전
from .sejong_dictionary import SejongDictionary
from .utils import get_data_dir, get_version


from .pos_tags import (
    NNG,
    NNP,
    VA,
    VV,
    EF,
    EP,
    EC,
    JKS,
    JKO,
    JKG,
    JKB,
    JC,
    JX,
    MAG,
    MM,
    IC,
    XSV,
    SF,
    SP,
    VCP,
    VX,
    ETM,
    ETN,
)


# v02 기본 어휘 (복사)
NOMINALS: List[Tuple[str, str, str]] = [
    ("친구", NNG, "친구"),
    ("학교", NNG, "학교"),
    ("선생님", NNG, "선생님"),
    ("학생", NNG, "학생"),
    ("날씨", NNG, "날씨"),
    ("책", NNG, "책"),
    # 시간 명사 -> MODIFIERS로 이동 (MAG로 등록)
    # ("오늘", NNG, "오늘"),
    ("어제", NNG, "어제"),
    ("내일", NNG, "내일"),
    ("교사", NNG, "교사"),
    ("전제", NNG, "전제"),
    ("국면", NNG, "국면"),
    ("담화", NNG, "담화"),
    ("참여자", NNG, "참여자"),
    ("통시적", NNG, "통시적"),
    ("맥락", NNG, "맥락"),
    ("재귀적", NNG, "재귀적"),
    ("호출", NNG, "호출"),
    ("의미", NNG, "의미"),
    ("해석", NNG, "해석"),
    ("일관성", NNG, "일관성"),
    ("유지", NNG, "유지"),
    ("붕괴", NNG, "붕괴"),
    ("비가시적", NNG, "비가시적"),
    ("상호의존성", NNG, "상호의존성"),
    ("띄어쓰기", NNG, "띄어쓰기"),
]

PREDICATES: List[Tuple[str, str, str]] = [
    ("좋", VA, "좋다"),
    ("가", VV, "가다"),
    ("오", VV, "오다"),
    ("먹", VV, "먹다"),
    ("읽", VV, "읽다"),
    # ㅂ 불규칙 형용사
    ("반갑", VA, "반갑다"),
    ("고맙", VA, "고맙다"),
    ("가깝", VA, "가깝다"),
    ("어렵", VA, "어렵다"),
    ("쉽", VA, "쉽다"),
    ("무섭", VA, "무섭다"),
    ("귀엽", VA, "귀엽다"),
    ("더럽", VA, "더럽다"),
    ("아름답", VA, "아름답다"),
    ("무겁", VA, "무겁다"),
    ("차갑", VA, "차갑다"),
    ("뜨겁", VA, "뜨겁다"),
    # ㄷ/ㅅ/르/으 불규칙
    ("듣", VV, "듣다"),
    ("걷", VV, "걷다"),
    ("짓", VV, "짓다"),
    ("낫", VA, "낫다"),
    ("모르", VV, "모르다"),
    ("부르", VV, "부르다"),
    ("쓰", VV, "쓰다"),
    ("끄", VV, "끄다"),
    ("크", VA, "크다"),
    ("아프", VA, "아프다"),
    ("바쁘", VA, "바쁘다"),
    # 추가
    ("피", VV, "피다"),
    ("도와주", VV, "도와주다"),
    # Auxiliaries
    ("않", VX, "않다"),
    ("않다", VX, "않다"),
    ("못하", VX, "못하다"),
]

ENDINGS: List[Tuple[str, str, str]] = [
    ("다", EF, "다"),
    ("네요", EF, "네요"),
    ("습니다", EF, "습니다"),
    ("ㅂ니다", EF, "ㅂ니다"),
    ("어요", EF, "어요"),
    ("았", EP, "았"),
    ("었", EP, "었"),
    ("겠", EP, "겠"),
    ("고", EC, "고"),
    ("어서", EC, "어서"),
    ("세요", EF, "세요"),
    ("으세요", EF, "으세요"),
    # Added common endings
    ("지", EC, "지"),  # Connection ending
    ("는다", EF, "는다"),  # Final ending (plain style)
    ("는", ETM, "는"),  # Adnominal ending
    ("니", EC, "니"),  # Question ending
    ("ㄹ", ETM, "ㄹ"),  # Adnominal ending (future)
    ("기", ETN, "기"),  # Nominal ending
    ("게", EC, "게"),  # Adverbial ending
    ("면", EC, "면"),  # Conditional ending
    ("으나", EC, "으나"),  # Contrastive ending
]

PARTICLES: List[Tuple[str, str, str]] = [
    ("가", JKS, "가"),
    ("이", JKS, "이"),
    ("를", JKO, "를"),
    ("을", JKO, "을"),
    ("에", JKB, "에"),
    ("에서", JKB, "에서"),
    ("께서", JKS, "께서"),
    ("와", JC, "와"),
    ("과", JC, "과"),
    ("의", JKG, "의"),
    ("조차", JX, "조차"),
]

MODIFIERS: List[Tuple[str, str, str]] = [
    ("정말", MAG, "정말"),
    ("매우", MAG, "매우"),
    ("아주", MAG, "아주"),
    ("오늘", MAG, "오늘"),
    ("어제", MAG, "어제"),
    ("내일", MAG, "내일"),
    ("늘", MAG, "늘"),
    ("이", MM, "이"),
    ("그", MM, "그"),
    ("저", MM, "저"),
]

INTERJECTIONS: List[Tuple[str, str, str]] = [
    ("네", IC, "네"),
    ("아니요", IC, "아니요"),
]

AFFIXES: List[Tuple[str, str, str]] = [
    ("하", XSV, "하다"),
]

SYMBOLS: List[Tuple[str, str, str]] = [
    (".", SF, "."),
    ("?", SF, "?"),
    ("!", SF, "!"),
    (",", SP, ","),
]


def build_comprehensive_trie(
    use_double_array: bool = True,
    use_sejong: bool = True,
    use_rust: bool = False,
    load_defaults: bool = True,
) -> Union["DoubleArrayTrie", "Trie", "RustTrieWrapper"]:
    """
    v0.1.1 독립 사전 빌드

    Args:
        use_double_array: Double Array Trie 사용 (권장)
        use_sejong: 세종 사전 통합 (권장, 794단어)
        use_rust: Rust 가속 모듈 사용

    Returns:
        Trie 객체 (Python Trie, DoubleArrayTrie, 또는 RustTrieWrapper)
    """
    print("=" * 60)
    print(f"  v{get_version()} 독립 사전 빌드")
    print("=" * 60)

    # get_version called inside print above? I should have imported it or used .utils.get_version?
    # I imported `get_data_dir` at top level. I should import `get_version` there too or just here.
    # To be safe, I'll rely on the top-level import if I added it, but I only added get_data_dir in previous step.
    # Ah, I missed adding `get_version` to the import list in dictionary.py in previous step.
    # I'll just skip version print or use hardcoded string or fix import later.
    # Let's fix import inside function to be safe.

    data_dir = get_data_dir()
    os.makedirs(data_dir, exist_ok=True)

    rust_path = os.path.join(data_dir, "rust_trie.bin")
    dat_path = os.path.join(data_dir, "dictionary.dat")
    pkl_path = os.path.join(data_dir, "dictionary.pkl")

    # 1. Rust Trie 체크 (Compiled)
    trie = None
    if use_rust:
        try:
            from .rust_ext import RustTrieWrapper, HAS_RUST

            if HAS_RUST:
                print("  [v] Rust 모듈 사용")
                trie = RustTrieWrapper()

                if os.path.exists(rust_path):
                    print(f"  [v] 캐시된 Rust 사전 로드 중... ({rust_path})")
                    try:
                        trie.load(rust_path)
                        print("  [v] 로드 완료!")
                        return trie  # Compiled trie is complete
                    except Exception as e:
                        print(f"  ⚠ 캐시 로드 실패 (새로 빌드합니다): {e}")
                        try:
                            os.remove(rust_path)
                            print(f"  [!] 호환되지 않는 캐시 파일 삭제됨: {rust_path}")
                        except OSError:
                            pass
                        trie = RustTrieWrapper()  # Reset
            else:
                print("  ⚠ Rust 모듈 미설치 -> Python Fallback")
        except ImportError:
            print("  ⚠ Rust 모듈 import 실패 -> Python Fallback")

    # 2. DoubleArrayTrie 체크 (Compiled)
    if trie is None and use_double_array:
        # DAT 로드 시도
        if os.path.exists(dat_path):
            try:
                # DAT는 create_trie로 생성 후 load 호출
                from .trie_da import DoubleArrayTrie

                temp_trie = DoubleArrayTrie()
                temp_trie.load(dat_path)
                print(f"  [v] 캐시된 DAT 사전 로드 완료: {dat_path}")
                return temp_trie
            except Exception as e:
                print(f"  ⚠ DAT 로드 실패: {e}")
                # Fallthrough to build from source

    # 3. Source Trie 로드 (PythonTrieFallback / dictionary.pkl)
    # 이것은 "원본 데이터"로서, Rust나 DAT를 빌드하기 위한 소스로 사용됨.
    from .trie_da import PythonTrieFallback

    loaded_source_trie = None

    if os.path.exists(pkl_path):
        try:
            temp_trie = PythonTrieFallback()
            temp_trie.load(pkl_path)
            loaded_source_trie = temp_trie
            print(f"  [v] 원본 사전(Source) 로드 완료: {len(loaded_source_trie)} 단어")

            if use_sejong:
                print("  [v] 저장된 원본 사전을 사용하므로 세종 CSV 로드를 건너뜁니다.")
                use_sejong = False
        except Exception as e:
            print(f"  ⚠ 원본 사전 로드 실패: {e}")

    # 4. 타겟 Trie 생성 (아직 없으면)
    if trie is None:
        if create_trie is None:
            raise ImportError("Trie modules not available")

        # Source가 있고, 목표가 PythonTrieFallback(DAT미사용)이면 바로 사용
        if loaded_source_trie and not use_double_array:
            trie = loaded_source_trie
        else:
            trie = create_trie(use_double_array=use_double_array)
            # 만약 Source가 있으면 Copy
            if loaded_source_trie:
                print(
                    f"  [v] 원본 사전을 타겟 Trie({type(trie).__name__})로 변환 중..."
                )
                for word, pos, lemma in loaded_source_trie:
                    trie.insert(word, pos, lemma)

    # 5. v02 기본 어휘 추가 (안전망)
    v02_count = 0
    if load_defaults:
        # To reduce code length in artifact, I'll use a helper loop
        for lst in [
            NOMINALS,
            PREDICATES,
            ENDINGS,
            MODIFIERS,
            PARTICLES,
            INTERJECTIONS,
            AFFIXES,
            SYMBOLS,
        ]:
            for word, pos, lemma in lst:
                trie.insert(word, pos, lemma)
                v02_count += 1
        print(f"[v] v02 기본 어휘 등록 확인 ({v02_count}개)")

    # 6. 세종 사전 추가 (필요한 경우)
    sejong_count = 0
    if load_defaults and use_sejong:
        sejong = SejongDictionary()
        sejong_words = sejong.load_builtin_dictionary()

        for word, patterns in sejong_words.items():
            for pos, lemma in patterns:
                try:
                    trie.insert(word, pos, lemma)
                    sejong_count += 1
                    if (pos == "VV" or pos == "VA") and word.endswith("다"):
                        stem = word[:-1]
                        trie.insert(stem, pos, lemma)
                except:
                    pass
        print(f"[v] 세종 사전: {sejong_count}개 패턴")

    # 7. Trie 빌드
    if hasattr(trie, "build"):
        try:
            trie.build()
        except RuntimeError:
            pass

        # 통계 출력
        if hasattr(trie, "get_stats"):
            stats = trie.get_stats()
            print(f"  - Trie Stats: {stats}")

    # 8. 캐시 저장
    # Rust -> rust_trie.bin
    if use_rust and hasattr(trie, "save") and not os.path.exists(rust_path):
        try:
            print(f"  [v] Rust 사전 캐싱: {rust_path}")
            trie.save(rust_path)
        except Exception as e:
            print(f"  ⚠ 캐싱 실패: {e}")

    # DAT -> dictionary.dat
    if use_double_array and hasattr(trie, "save") and not os.path.exists(dat_path):
        # Only save if it's actually DoubleArrayTrie
        if type(trie).__name__ == "DoubleArrayTrie":
            try:
                print(f"  [v] DAT 사전 캐싱: {dat_path}")
                trie.save(dat_path)
            except Exception as e:
                print(f"  ⚠ DAT 캐싱 실패: {e}")

    # Note: dictionary.pkl (Source) is NOT saved here automatically unless we want to cache the merge result.
    # analyzer.py's save() method handles explicit saving of the Source.
    # But if we just built from Sejong, we might want to save Source for faster future load?
    # If loaded_source_trie was None, and we built a fresh Trie.
    # If trie is PythonTrieFallback, we can save it as pkl.
    if loaded_source_trie is None and type(trie).__name__ == "PythonTrieFallback":
        try:
            print(f"  [v] 원본 사전 캐싱: {pkl_path}")
            trie.save(pkl_path)
        except Exception as e:
            print(f"  ⚠ 원본 캐싱 실패: {e}")

    print("=" * 60)
    return trie


if __name__ == "__main__":
    # 테스트
    print("\nv03 독립 사전 빌드 테스트\n")

    # v03 사전 빌드
    trie = build_comprehensive_trie(use_sejong=True)

    # 검색 테스트
    print("\n" + "=" * 60)
    print("검색 테스트")
    print("=" * 60)

    test_words = ["친구", "학교", "컴퓨터", "핸드폰", "음악", "좋"]

    for word in test_words:
        if trie.exists(word):
            patterns = trie.search(word)
            print(f"[v] '{word}': {patterns}")
        else:
            print(f"[x] '{word}': 없음")
