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
    NNB,
    NR,
    NP,
    VA,
    VV,
    VX,
    VCP,
    VCN,
    EF,
    EP,
    EC,
    ETM,
    ETN,
    JKS,
    JKO,
    JKG,
    JKB,
    JKV,
    JC,
    JX,
    MAG,
    MM,
    IC,
    XPN,
    XSN,
    XSV,
    XSA,
    SF,
    SP,
)


# v02 기본 어휘 (확장: 국립국어원 표준국어대사전 기반高频 어휘)
NOMINALS: List[Tuple[str, str, str]] = [
    # 사람/관계
    ("사람", NNG, "사람"), ("친구", NNG, "친구"), ("가족", NNG, "가족"),
    ("어머니", NNG, "어머니"), ("아버지", NNG, "아버지"), ("형", NNG, "형"),
    ("누나", NNG, "누나"), ("동생", NNG, "동생"), ("남편", NNG, "남편"),
    ("아내", NNG, "아내"), ("아이", NNG, "아이"), ("어른", NNG, "어른"),
    ("사장", NNG, "사장"), ("선생님", NNG, "선생님"), ("학생", NNG, "학생"),
    ("의사", NNG, "의사"), ("선수", NNG, "선수"), ("회원", NNG, "회원"),
    ("고객", NNG, "고객"), ("군인", NNG, "군인"), ("경찰", NNG, "경찰"),
    ("소방관", NNG, "소방관"), ("기자", NNG, "기자"), ("작가", NNG, "작가"),
    ("가수", NNG, "가수"), ("배우", NNG, "배우"), ("감독", NNG, "감독"),
    ("교사", NNG, "교사"), ("교수", NNG, "교수"), ("친척", NNG, "친척"),
    ("이웃", NNG, "이웃"), ("손님", NNG, "손님"), ("주인", NNG, "주인"),
    ("여자", NNG, "여자"), ("남자", NNG, "남자"), ("어른", NNG, "어른"),
    ("아가", NNG, "아가"), ("아가씨", NNG, "아가씨"), ("아저씨", NNG, "아저씨"),
    ("아줌마", NNG, "아줌마"),
    # 장소/기관
    ("집", NNG, "집"), ("학교", NNG, "학교"), ("회사", NNG, "회사"),
    ("병원", NNG, "병원"), ("가게", NNG, "가게"), ("시장", NNG, "시장"),
    ("공원", NNG, "공원"), ("도서관", NNG, "도서관"), ("식당", NNG, "식당"),
    ("영화관", NNG, "영화관"), ("극장", NNG, "극장"), ("공항", NNG, "공항"),
    ("역", NNG, "역"), ("정류장", NNG, "정류장"), ("주차장", NNG, "주차장"),
    ("운동장", NNG, "운동장"), ("운동", NNG, "운동"),
    ("사무실", NNG, "사무실"), ("교실", NNG, "교실"), ("화장실", NNG, "화장실"),
    ("부엌", NNG, "부엌"), ("방", NNG, "방"), ("거실", NNG, "거실"),
    ("도시", NNG, "도시"), ("시골", NNG, "시골"), ("나라", NNG, "나라"),
    ("서울", NNP, "서울"), ("한국", NNP, "한국"), ("부산", NNP, "부산"),
    ("대전", NNP, "대전"), ("광주", NNP, "광주"), ("인천", NNP, "인천"),
    ("대구", NNP, "대구"), ("울산", NNP, "울산"),     ("제주", NNP, "제주"), ("경주", NNP, "경주"),
    ("강남", NNP, "강남"), ("강북", NNP, "강북"),
    ("송파", NNP, "송파"), ("강동", NNP, "강동"),
    ("서초", NNP, "서초"), ("관악", NNP, "관악"),
    ("종로", NNP, "종로"), ("마포", NNP, "마포"),
    ("압구정", NNP, "압구정"), ("여의도", NNP, "여의도"),
    ("홍대", NNP, "홍대"), ("신촌", NNP, "신촌"),
    ("잠실", NNP, "잠실"), ("구로", NNP, "구로"),
    ("영등포", NNP, "영등포"), ("용산", NNP, "용산"),
    ("분당", NNP, "분당"), ("일산", NNP, "일산"),
    ("평촌", NNP, "평촌"), ("판교", NNP, "판교"),
    ("수원", NNP, "수원"), ("성남", NNP, "성남"),
    ("안양", NNP, "안양"), ("고양", NNP, "고양"),
    ("용인", NNP, "용인"), ("화성", NNP, "화성"),
    ("평택", NNP, "평택"), ("의정부", NNP, "의정부"),
    ("청주", NNP, "청주"), ("천안", NNP, "천안"),
    ("전주", NNP, "전주"), ("순천", NNP, "순천"),
    ("창원", NNP, "창원"), ("진주", NNP, "진주"),
    ("통영", NNP, "통영"), ("거제", NNP, "거제"),
    ("한라산", NNP, "한라산"), ("설악산", NNP, "설악산"),
    ("지리산", NNP, "지리산"), ("북한산", NNP, "북한산"),
    ("도봉산", NNP, "도봉산"), ("관악산", NNP, "관악산"),
    ("한강", NNP, "한강"), ("낙동강", NNP, "낙동강"),
    ("금강", NNP, "금강"), ("영산강", NNP, "영산강"),
    ("제주도", NNP, "제주도"), ("울릉도", NNP, "울릉도"),
    ("거제도", NNP, "거제도"), ("남해", NNP, "남해"),
    ("동해", NNP, "동해"), ("서해", NNP, "서해"),
    ("삼성", NNP, "삼성"), ("엘지", NNP, "엘지"),
    ("현대", NNP, "현대"), ("기아", NNP, "기아"),
    ("네이버", NNP, "네이버"), ("카카오", NNP, "카카오"),
    ("배달의민족", NNP, "배달의민족"), ("쿠팡", NNP, "쿠팡"),
    ("일본", NNP, "일본"), ("중국", NNP, "중국"), ("미국", NNP, "미국"),
    ("영국", NNP, "영국"), ("프랑스", NNP, "프랑스"), ("독일", NNP, "독일"),
    # 사물/물건
    ("책", NNG, "책"), ("책상", NNG, "책상"), ("의자", NNG, "의자"),
    ("컴퓨터", NNG, "컴퓨터"), ("핸드폰", NNG, "핸드폰"), ("전화", NNG, "전화"),
    ("텔레비전", NNG, "텔레비전"), ("라디오", NNG, "라디오"), ("가방", NNG, "가방"),
    ("옷", NNG, "옷"), ("신발", NNG, "신발"), ("모자", NNG, "모자"),
    ("시계", NNG, "시계"), ("안경", NNG, "안경"), ("문", NNG, "문"),
    ("창문", NNG, "창문"), ("열쇠", NNG, "열쇠"), ("우산", NNG, "우산"),
    ("칼", NNG, "칼"), ("가위", NNG, "가위"), ("그릇", NNG, "그릇"),
    ("접시", NNG, "접시"), ("컵", NNG, "컵"), ("물건", NNG, "물건"),
    ("선물", NNG, "선물"),
    ("자동차", NNG, "자동차"), ("버스", NNG, "버스"), ("지하철", NNG, "지하철"),
    ("비행기", NNG, "비행기"), ("기차", NNG, "기차"), ("자전거", NNG, "자전거"),
    ("오토바이", NNG, "오토바이"),
    # 음식
    ("밥", NNG, "밥"), ("김치", NNG, "김치"), ("물", NNG, "물"),
    ("고기", NNG, "고기"), ("생선", NNG, "생선"), ("채소", NNG, "채소"),
    ("과일", NNG, "과일"), ("음식", NNG, "음식"), ("빵", NNG, "빵"),
    ("우유", NNG, "우유"), ("주스", NNG, "주스"), ("차", NNG, "차"),
    ("커피", NNG, "커피"), ("술", NNG, "술"), ("맥주", NNG, "맥주"),
    ("소주", NNG, "소주"), ("떡", NNG, "떡"), ("국", NNG, "국"),
    ("반찬", NNG, "반찬"), ("간식", NNG, "간식"), ("사탕", NNG, "사탕"),
    ("초콜릿", NNG, "초콜릿"), ("아이스크림", NNG, "아이스크림"),
    # 자연/날씨
    ("날씨", NNG, "날씨"), ("하늘", NNG, "하늘"), ("땅", NNG, "땅"),
    ("바다", NNG, "바다"), ("산", NNG, "산"), ("강", NNG, "강"),
    ("호수", NNG, "호수"), ("비", NNG, "비"), ("눈", NNG, "눈"),
    ("바람", NNG, "바람"), ("구름", NNG, "구름"), ("해", NNG, "해"),
    ("달", NNG, "달"), ("별", NNG, "별"), ("태양", NNG, "태양"),
    ("꽃", NNG, "꽃"), ("나무", NNG, "나무"), ("풀", NNG, "풀"),
    ("동물", NNG, "동물"), ("개", NNG, "개"), ("고양이", NNG, "고양이"),
    ("새", NNG, "새"), ("물고기", NNG, "물고기"), ("말", NNG, "말"),
    ("소", NNG, "소"), ("돼지", NNG, "돼지"), ("닭", NNG, "닭"),
    # 시간
    ("시간", NNG, "시간"), ("분", NNB, "분"), ("초", NNB, "초"),
    ("시", NNB, "시"), ("년", NNB, "년"), ("월", NNB, "월"),
    ("일", NNB, "일"), ("주", NNG, "주"), ("달", NNB, "달"),
    ("날", NNG, "날"), ("오늘", NNG, "오늘"), ("어제", NNG, "어제"),
    ("내일", NNG, "내일"), ("아침", NNG, "아침"), ("점심", NNG, "점심"),
    ("저녁", NNG, "저녁"), ("밤", NNG, "밤"), ("낮", NNG, "낮"),
    ("새벽", NNG, "새벽"), ("오전", NNG, "오전"), ("오후", NNG, "오후"),
    ("요일", NNG, "요일"), ("월요일", NNG, "월요일"), ("화요일", NNG, "화요일"),
    ("수요일", NNG, "수요일"), ("목요일", NNG, "목요일"), ("금요일", NNG, "금요일"),
    ("토요일", NNG, "토요일"), ("일요일", NNG, "일요일"),
    ("겨울", NNG, "겨울"), ("봄", NNG, "봄"), ("여름", NNG, "여름"), ("가을", NNG, "가을"),
    # 추상명사
    ("생각", NNG, "생각"), ("마음", NNG, "마음"), ("사랑", NNG, "사랑"),
    ("희망", NNG, "희망"), ("꿈", NNG, "꿈"), ("행복", NNG, "행복"),
    ("슬픔", NNG, "슬픔"), ("기쁨", NNG, "기쁨"), ("화", NNG, "화"),
    ("문제", NNG, "문제"), ("답", NNG, "답"), ("이유", NNG, "이유"),
    ("방법", NNG, "방법"), ("결과", NNG, "결과"), ("이야기", NNG, "이야기"),
    ("말", NNG, "말"), ("소리", NNG, "소리"), ("노래", NNG, "노래"),
    ("음악", NNG, "음악"), ("영화", NNG, "영화"), ("연극", NNG, "연극"),
    ("공부", NNG, "공부"), ("일", NNG, "일"), ("숙제", NNG, "숙제"),
    ("시험", NNG, "시험"), ("시합", NNG, "시합"), ("경기", NNG, "경기"),
    ("약속", NNG, "약속"), ("여행", NNG, "여행"), ("휴가", NNG, "휴가"),
    ("인생", NNG, "인생"), ("세상", NNG, "세상"), ("세계", NNG, "세계"),
    ("역사", NNG, "역사"), ("문화", NNG, "문화"), ("예술", NNG, "예술"),
    ("과학", NNG, "과학"), ("기술", NNG, "기술"), ("정보", NNG, "정보"),
    ("뉴스", NNG, "뉴스"), ("신문", NNG, "신문"), ("편지", NNG, "편지"),
    ("이름", NNG, "이름"), ("주소", NNG, "주소"), ("번호", NNG, "번호"),
    ("가격", NNG, "가격"), ("돈", NNG, "돈"), ("값", NNG, "값"),
    ("사건", NNG, "사건"), ("사고", NNG, "사고"), ("소식", NNG, "소식"),
    ("진실", NNG, "진실"), ("거짓말", NNG, "거짓말"),
    ("의미", NNG, "의미"), ("해석", NNG, "해석"), ("맥락", NNG, "맥락"),
    ("전제", NNG, "전제"), ("국면", NNG, "국면"), ("담화", NNG, "담화"),
    ("참여자", NNG, "참여자"), ("통시적", NNG, "통시적"),
    ("재귀적", NNG, "재귀적"), ("호출", NNG, "호출"),
    ("일관성", NNG, "일관성"), ("유지", NNG, "유지"),
    ("붕괴", NNG, "붕괴"), ("비가시적", NNG, "비가시적"),
    ("상호의존성", NNG, "상호의존성"), ("띄어쓰기", NNG, "띄어쓰기"),
    # 대명사
    ("나", NP, "나"), ("저", NP, "저"), ("너", NP, "너"),
    ("우리", NP, "우리"), ("당신", NP, "당신"), ("그", NP, "그"),
    ("그녀", NP, "그녀"), ("여기", NP, "여기"), ("거기", NP, "거기"),
    ("저기", NP, "저기"), ("이것", NP, "이것"), ("그것", NP, "그것"),
    ("저것", NP, "저것"), ("무엇", NP, "무엇"), ("누구", NP, "누구"),
    ("어디", NP, "어디"), ("언제", NP, "언제"),
    ("아무", NP, "아무"),
    # 수사
    ("하나", NR, "하나"), ("둘", NR, "둘"), ("셋", NR, "셋"),
    ("넷", NR, "넷"), ("다섯", NR, "다섯"), ("여섯", NR, "여섯"),
    ("일곱", NR, "일곱"), ("여덟", NR, "여덟"), ("아홉", NR, "아홉"),
    ("열", NR, "열"), ("스물", NR, "스물"), ("서른", NR, "서른"),
    ("마흔", NR, "마흔"), ("쉰", NR, "쉰"), ("예순", NR, "예순"),
    ("일흔", NR, "일흔"), ("여든", NR, "여든"), ("아흔", NR, "아흔"),
    ("백", NR, "백"), ("천", NR, "천"), ("만", NR, "만"),
    ("일", NR, "일"), ("이", NR, "이"), ("삼", NR, "삼"),
    ("사", NR, "사"), ("오", NR, "오"), ("육", NR, "육"),
    ("칠", NR, "칠"), ("팔", NR, "팔"), ("구", NR, "구"), ("십", NR, "십"),
]

PREDICATES: List[Tuple[str, str, str]] = [
    # 동사 VV
    ("가", VV, "가다"), ("오", VV, "오다"), ("먹", VV, "먹다"),
    ("마시", VV, "마시다"), ("읽", VV, "읽다"), ("쓰", VV, "쓰다"),
    ("배우", VV, "배우다"), ("일하", VV, "일하다"), ("공부하", VV, "공부하다"),
    ("만들", VV, "만들다"), ("사", VV, "사다"), ("팔", VV, "팔다"),
    ("주", VV, "주다"), ("받", VV, "받다"), ("보내", VV, "보내다"),
    ("가지", VV, "가다"), ("쉬", VV, "쉬다"),
    ("자", VV, "자다"), ("일어나", VV, "일어나다"), ("앉", VV, "앉다"),
    ("서", VV, "서다"), ("걷", VV, "걷다"), ("뛰", VV, "뛰다"),
    ("날", VV, "날다"), ("타", VV, "타다"), ("운전하", VV, "운전하다"),
    ("말하", VV, "말하다"), ("이야기하", VV, "이야기하다"), ("묻", VV, "묻다"),
    ("대답하", VV, "대답하다"), ("부르", VV, "부르다"), ("노래하", VV, "노래하다"),
    ("춤추", VV, "춤추다"), ("웃", VV, "웃다"), ("울", VV, "울다"),
    ("웃", VV, "웃다"), ("울", VV, "울다"),
    ("보", VV, "보다"), ("듣", VV, "듣다"), ("느끼", VV, "느끼다"),
    ("만나", VV, "만나다"), ("기다리", VV, "기다리다"),
    ("찾", VV, "찾다"), ("잃어버리", VV, "잃어버리다"),
    ("넣", VV, "넣다"), ("꺼내", VV, "꺼내다"),
    ("열", VV, "열다"), ("닫", VV, "닫다"), ("켜", VV, "켜다"),
    ("끄", VV, "끄다"), ("켜", VV, "켜다"),
    ("놓", VV, "놓다"), ("두", VV, "두다"), ("넣", VV, "넣다"),
    ("빼", VV, "빼다"), ("더하", VV, "더하다"), ("빼", VV, "빼다"),
    ("모르", VV, "모르다"), ("알", VV, "알다"), ("생각하", VV, "생각하다"),
    ("결정하", VV, "결정하다"), ("선택하", VV, "선택하다"),
    ("도와주", VV, "도와주다"), ("도움", VV, "도움"),
    ("피", VV, "피다"), ("키우", VV, "키우다"),
    ("살", VV, "살다"), ("죽", VV, "죽다"),
    ("나", VV, "나다"), ("생기", VV, "생기다"), ("변하", VV, "변하다"),
    ("되", VV, "되다"), ("하", VV, "하다"), ("시키", VV, "시키다"),
    ("나타나", VV, "나타나다"), ("사라지", VV, "사라지다"),
    ("이기", VV, "이기다"), ("지", VV, "지다"),
    ("쓰", VV, "쓰다"), ("그리", VV, "그리다"), ("적", VV, "적다"),
    ("외우", VV, "외우다"), ("읊", VV, "읊다"),
    ("입", VV, "입다"), ("신", VV, "신다"), ("벗", VV, "벗다"),
    ("걸치", VV, "걸치다"),
    ("씻", VV, "씻다"), ("닦", VV, "닦다"), ("청소하", VV, "청소하다"),
    ("요리하", VV, "요리하다"), ("빨", VV, "빨다"), ("다리", VV, "다리다"),
    ("전화하", VV, "전화하다"), ("문자하", VV, "문자하다"),
    ("보내", VV, "보내다"), ("받", VV, "받다"),
    ("물어보", VV, "물어보다"), ("가르치", VV, "가르치다"),
    ("알려주", VV, "알려주다"), ("설명하", VV, "설명하다"),
    # 형용사 VA
    ("좋", VA, "좋다"), ("나쁘", VA, "나쁘다"),
    ("크", VA, "크다"), ("작", VA, "작다"), ("길", VA, "길다"),
    ("짧", VA, "짧다"), ("넓", VA, "넓다"), ("좁", VA, "좁다"),
    ("높", VA, "높다"), ("낮", VA, "낮다"), ("깊", VA, "깊다"),
    ("얕", VA, "얕다"), ("많", VA, "많다"), ("적", VA, "적다"),
    ("새롭", VA, "새롭다"), ("낡", VA, "낡다"),
    ("예쁘", VA, "예쁘다"), ("멋있", VA, "멋있다"),
    ("착하", VA, "착하다"), ("똑똑하", VA, "똑똑하다"),
    ("빠르", VA, "빠르다"), ("느리", VA, "느리다"),
    ("맛있", VA, "맛있다"), ("맛없", VA, "맛없다"),
    ("재미있", VA, "재미있다"), ("재미없", VA, "재미없다"),
    ("시끄럽", VA, "시끄럽다"), ("조용하", VA, "조용하다"),
    ("춥", VA, "춥다"), ("덥", VA, "덥다"), ("따뜻하", VA, "따뜻하다"),
    ("시원하", VA, "시원하다"), ("건조하", VA, "건조하다"),
    ("비싸", VA, "비싸다"), ("싸", VA, "싸다"),
    ("어렵", VA, "어렵다"), ("쉽", VA, "쉽다"), ("재미있", VA, "재미있다"),
    ("즐겁", VA, "즐겁다"), ("슬프", VA, "슬프다"),
    ("아프", VA, "아프다"), ("피곤하", VA, "피곤하다"),
    ("배고프", VA, "배고프다"), ("배부르", VA, "배부르다"),
    ("기쁘", VA, "기쁘다"), ("행복하", VA, "행복하다"),
    ("화나", VA, "화나다"), ("궁금하", VA, "궁금하다"),
    ("두렵", VA, "두렵다"), ("무섭", VA, "무섭다"),
    ("용감하", VA, "용감하다"), ("부럽", VA, "부럽다"),
    ("고맙", VA, "고맙다"), ("감사하", VA, "감사하다"),
    ("미안하", VA, "미안하다"), ("죄송하", VA, "죄송하다"),
    ("괜찮", VA, "괜찮다"), ("이상하", VA, "이상하다"),
    ("가깝", VA, "가깝다"), ("멀", VA, "멀다"),
    ("반갑", VA, "반갑다"), ("낫", VA, "낫다"),
    # ㅂ 불규칙 형용사 추가
    ("아름답", VA, "아름답다"), ("무겁", VA, "무겁다"),
    ("차갑", VA, "차갑다"), ("뜨겁", VA, "뜨겁다"),
    ("귀엽", VA, "귀엽다"), ("더럽", VA, "더럽다"),
    ("가볍", VA, "가볍다"), ("밝", VA, "밝다"),
    ("어둡", VA, "어둡다"), ("맵", VA, "맵다"),
    ("짜", VA, "짜다"), ("달", VA, "달다"), ("시", VA, "시다"),
    ("쓰", VA, "쓰다"), ("떫", VA, "떫다"),
    # 르/으 불규칙 추가
    ("바쁘", VA, "바쁘다"), ("예쁘", VA, "예쁘다"),
    ("크", VA, "크다"), ("다르", VA, "다르다"),
    ("고르", VV, "고르다"), ("모르", VV, "모르다"),
    # 있다/없다 계열
    ("있", VA, "있다"), ("없", VA, "없다"),
    ("멋있", VA, "멋있다"), ("재미있", VA, "재미있다"),
    ("맛있", VA, "맛있다"), ("재미없", VA, "재미없다"),
    ("맛없", VA, "맛없다"), ("싫", VA, "싫다"),
    ("좋", VA, "좋다"),
    # 의존 동사/보조 용언 VX
    ("않", VX, "않다"), ("않다", VX, "않다"),
    ("못하", VX, "못하다"), ("되", VX, "되다"),
    ("싶", VX, "싶다"), ("보", VX, "보다"),
    ("주", VX, "주다"), ("두", VX, "두다"),
    ("버리", VX, "버리다"), ("놓", VX, "놓다"),
    ("말", VX, "말다"), ("오", VX, "오다"),
    ("가지", VX, "가다"),
    ("내", VX, "내다"), ("대", VX, "대다"),
    ("나", VX, "나다"),
    ("하", VX, "하다"),
    ("있", VX, "있다"),
    # 형용사 '이다' 지정사
    ("이", VCP, "이다"), ("아니", VCN, "아니다"),
]

ENDINGS: List[Tuple[str, str, str]] = [
    # 종결 어말어미 EF
    ("다", EF, "다"),
    ("네요", EF, "네요"),
    ("습니다", EF, "습니다"),
    ("ㅂ니다", EF, "ㅂ니다"),
    ("어요", EF, "어요"),
    ("아요", EF, "아요"),
    ("요", EF, "요"),
    ("네", EF, "네"),
    ("구나", EF, "구나"),
    ("군요", EF, "군요"),
    ("아", EF, "아"),
    ("어", EF, "어"),
    ("지요", EF, "지요"),
    ("죠", EF, "죠"),
    ("나", EF, "나"),
    ("냐", EF, "냐"),
    ("니", EF, "니"),
    ("까", EF, "까"),
    ("ㅂ니까", EF, "ㅂ니까"),
    ("세요", EF, "세요"),
    ("으세요", EF, "으세요"),
    ("라", EF, "라"),
    ("자", EF, "자"),
    ("마", EF, "마"),
    ("렴", EF, "렴"),
    ("게", EF, "게"),
    ("오", EF, "오"),
    ("소", EF, "소"),
    ("ㅂ시오", EF, "ㅂ시오"),
    ("ㅂ시다", EF, "ㅂ시다"),
    ("는다", EF, "는다"),
    ("ㄴ다", EF, "ㄴ다"),
    ("다", EF, "다"),
    ("랍니다", EF, "랍니다"),
    # 선어말어미 EP
    ("았", EP, "았"),
    ("었", EP, "었"),
    ("였", EP, "였"),
    ("겠", EP, "겠"),
    ("시", EP, "시"),
    ("으시", EP, "으시"),
    ("옵", EP, "옵"),
    ("사옵", EP, "사옵"),
    # 연결어미 EC
    ("고", EC, "고"),
    ("며", EC, "며"),
    ("면서", EC, "면서"),
    ("지만", EC, "지만"),
    ("어서", EC, "어서"),
    ("아서", EC, "아서"),
    ("니까", EC, "니까"),
    ("으니까", EC, "으니까"),
    ("니", EC, "니"),
    ("면", EC, "면"),
    ("으면", EC, "으면"),
    ("게", EC, "게"),
    ("지", EC, "지"),
    ("도록", EC, "도록"),
    ("려고", EC, "려고"),
    ("으려고", EC, "으려고"),
    ("러", EC, "러"),
    ("으러", EC, "으러"),
    ("려", EC, "려"),
    ("자", EC, "자"),
    ("도", EC, "도"),
    ("는데", EC, "는데"),
    ("은데", EC, "은데"),
    ("ㄴ데", EC, "ㄴ데"),
    ("어도", EC, "어도"),
    ("아도", EC, "아도"),
    ("거든", EC, "거든"),
    ("건", EC, "건"),
    ("을수록", EC, "을수록"),
    ("ㄹ수록", EC, "ㄹ수록"),
    ("으나", EC, "으나"),
    ("든지", EC, "든지"),
    ("든가", EC, "든가"),
    # 관형형 전성어미 ETM
    ("는", ETM, "는"),
    ("은", ETM, "은"),
    ("ㄴ", ETM, "ㄴ"),
    ("을", ETM, "을"),
    ("ㄹ", ETM, "ㄹ"),
    ("던", ETM, "던"),
    ("았던", ETM, "았던"),
    ("었던", ETM, "었던"),
    ("는", ETM, "는"),
    # 명사형 전성어미 ETN
    ("기", ETN, "기"),
    ("ㅁ", ETN, "ㅁ"),
    ("음", ETN, "음"),
]

PARTICLES: List[Tuple[str, str, str]] = [
    # 주격조사 JKS
    ("이", JKS, "이"), ("가", JKS, "가"),
    ("께서", JKS, "께서"), ("에서", JKS, "에서"),
    # 목적격조사 JKO
    ("을", JKO, "을"), ("를", JKO, "를"),
    # 부사격조사 JKB
    ("에", JKB, "에"), ("에서", JKB, "에서"),
    ("에게", JKB, "에게"), ("한테", JKB, "한테"),
    ("께", JKB, "께"), ("로", JKB, "로"),
    ("으로", JKB, "으로"), ("부터", JKB, "부터"),
    ("까지", JKB, "까지"), ("보다", JKB, "보다"),
    ("처럼", JKB, "처럼"), ("같이", JKB, "같이"),
    ("마냥", JKB, "마냥"),
    # 관형격조사 JKG
    ("의", JKG, "의"),
    # 호격조사 JKV
    ("아", JKV, "아"), ("야", JKV, "야"),
    ("여", JKV, "여"), ("이여", JKV, "이여"),
    # 접속조사 JC
    ("와", JC, "와"), ("과", JC, "과"),
    ("하고", JC, "하고"), ("랑", JC, "랑"),
    ("이랑", JC, "이랑"), ("며", JC, "며"),
    # 보조사 JX
    ("은", JX, "은"), ("는", JX, "는"),
    ("도", JX, "도"), ("만", JX, "만"),
    ("까지", JX, "까지"), ("조차", JX, "조차"),
    ("마저", JX, "마저"), ("부터", JX, "부터"),
    ("야", JX, "야"), ("이야", JX, "이야"),
    ("나", JX, "나"), ("이나", JX, "이나"),
    ("라도", JX, "라도"), ("이라도", JX, "이라도"),
    ("든지", JX, "든지"), ("커녕", JX, "커녕"),
]

MODIFIERS: List[Tuple[str, str, str]] = [
    # 관형사 MM (한정/지시/수)
    ("이", MM, "이"), ("그", MM, "그"), ("저", MM, "저"),
    ("어느", MM, "어느"), ("무슨", MM, "무슨"), ("어떤", MM, "어떤"),
    ("모든", MM, "모든"), ("전", MM, "전"), ("새", MM, "새"),
    ("헌", MM, "헌"), ("다른", MM, "다른"), ("여러", MM, "여러"),
    ("한", MM, "한"), ("두", MM, "두"), ("세", MM, "세"),
    ("네", MM, "네"), ("몇", MM, "몇"), ("각", MM, "각"),
    ("이런", MM, "이런"), ("그런", MM, "그런"), ("저런", MM, "저런"),
    ("약간", MM, "약간"), ("많은", MM, "많은"),
    # 일반 부사 MAG
    ("정말", MAG, "정말"), ("매우", MAG, "매우"), ("아주", MAG, "아주"),
    ("너무", MAG, "너무"), ("무척", MAG, "무척"), ("엄청", MAG, "엄청"),
    ("되게", MAG, "되게"), ("완전", MAG, "완전"),
    ("잘", MAG, "잘"), ("못", MAG, "못"),
    ("빨리", MAG, "빨리"), ("천천히", MAG, "천천히"),
    ("일찍", MAG, "일찍"), ("자주", MAG, "자주"),
    ("가끔", MAG, "가끔"), ("항상", MAG, "항상"),
    ("늘", MAG, "늘"), ("언제나", MAG, "언제나"),
    ("이미", MAG, "이미"), ("벌써", MAG, "벌써"),
    ("아직", MAG, "아직"), ("곧", MAG, "곧"),
    ("먼저", MAG, "먼저"), ("함께", MAG, "함께"),
    ("같이", MAG, "같이"), ("다시", MAG, "다시"),
    ("또", MAG, "또"), ("더", MAG, "더"),
    ("가장", MAG, "가장"), ("제일", MAG, "제일"),
    ("대단히", MAG, "대단히"), ("별로", MAG, "별로"),
    ("전혀", MAG, "전혀"), ("결코", MAG, "결코"),
    ("아마", MAG, "아마"), ("아니", MAG, "아니"),
    ("예", MAG, "예"), ("네", MAG, "네"),
    ("그래", MAG, "그래"), ("아니", MAG, "아니"),
    ("응", MAG, "응"),
    ("오늘", MAG, "오늘"), ("어제", MAG, "어제"), ("내일", MAG, "내일"),
    ("그냥", MAG, "그냥"), ("바로", MAG, "바로"),
    ("어쩌면", MAG, "어쩌면"), ("하필", MAG, "하필"),
    ("과연", MAG, "과연"), ("설마", MAG, "설마"),
    ("제발", MAG, "제발"), ("부디", MAG, "부디"),
    ("만약", MAG, "만약"), ("만일", MAG, "만일"),
    ("비록", MAG, "비록"), ("하물며", MAG, "하물며"),
    # 접속 부사
    ("그리고", MAG, "그리고"), ("그러나", MAG, "그러나"),
    ("하지만", MAG, "하지만"), ("그런데", MAG, "그런데"),
    ("또한", MAG, "또한"), ("또는", MAG, "또는"),
    ("혹은", MAG, "혹은"), ("즉", MAG, "즉"),
    ("그래서", MAG, "그래서"), ("따라서", MAG, "따라서"),
    ("그러므로", MAG, "그러므로"), ("결국", MAG, "결국"),
    ("아울러", MAG, "아울러"),
]

INTERJECTIONS: List[Tuple[str, str, str]] = [
    ("네", IC, "네"),
    ("아니요", IC, "아니요"),
    ("예", IC, "예"),
    ("아", IC, "아"),
    ("어", IC, "어"),
    ("응", IC, "응"),
    ("그래", IC, "그래"),
    ("아이고", IC, "아이고"),
    ("어머", IC, "어머"),
    ("아차", IC, "아차"),
    ("아싸", IC, "아싸"),
    ("헐", IC, "헐"),
    ("와", IC, "와"),
    ("휴", IC, "휴"),
    ("아이고", IC, "아이고"),
    ("맙소사", IC, "맙소사"),
    ("세상에", IC, "세상에"),
]

AFFIXES: List[Tuple[str, str, str]] = [
    # 접미사 XSN (명사 파생)
    ("음", XSN, "음"),
    ("ㅁ", XSN, "ㅁ"),
    ("기", XSN, "기"),
    ("개", XSN, "개"),
    ("이", XSN, "이"),
    ("꾼", XSN, "꾼"),
    ("쟁이", XSN, "쟁이"),
    ("님", XSN, "님"),
    ("장이", XSN, "장이"),
    # 접미사 XSV (동사 파생)
    ("하", XSV, "하다"),
    ("되", XSV, "되다"),
    ("시키", XSV, "시키다"),
    ("내", XSV, "내다"),
    ("뜨리", XSV, "뜨리다"),
    ("치", XSV, "치다"),
    # 접미사 XSA (형용사 파생)
    ("답", XSA, "답다"),
    ("롭", XSA, "롭다"),
    ("스럽", XSA, "스럽다"),
    ("하", XSA, "하다"),
    ("없", XSA, "없다"),
    ("있", XSA, "있다"),
    ("같", XSA, "같다"),
    # 접두사
    ("맨", XPN, "맨"),
    ("늦", XPN, "늦"),
    ("짓", XPN, "짓"),
    ("시", XPN, "시"),
    ("새", XPN, "새"),
    ("군", XPN, "군"),
    ("애", XPN, "애"),
    ("초", XPN, "초"),
    ("고", XPN, "고"),
    ("맏", XPN, "맏"),
    ("강", XPN, "강"),
    # 의존명사 NNB
    ("것", NNB, "것"), ("거", NNB, "거"),
    ("수", NNB, "수"), ("줄", NNB, "줄"),
    ("리", NNB, "리"), ("법", NNB, "법"),
    ("때", NNB, "때"), ("데", NNB, "데"),
    ("분", NNB, "분"), ("이", NNB, "이"),
    ("지", NNB, "지"),
    # 의존명사(의미) NN
    ("따름", NNB, "따름"), ("뿐", NNB, "뿐"),
    ("대로", NNB, "대로"), ("만큼", NNB, "만큼"),
    ("양", NNB, "양"), ("척", NNB, "척"),
    ("체", NNB, "체"),
    # 보조사/조사 기능 일부
    ("ㄴ", NNB, "ㄴ"),
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

    # 7. 활용형 어간 자동 등록
    conj_count = 0
    if load_defaults:
        for lst in [PREDICATES]:
            for word, pos, lemma in lst:
                if pos in ("VV", "VA", "VX") and lemma.endswith("다"):
                    stem = lemma[:-1]
                    if stem != word:
                        try:
                            trie.insert(stem, pos, lemma)
                            conj_count += 1
                        except Exception:
                            pass
        print(f"[v] 어간 자동 등록: {conj_count}개")

    # 8. Trie 빌드
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
