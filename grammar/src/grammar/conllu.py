from typing import List, Tuple, Dict, Optional


class ConlluParser:
    """CoNLL-U 포맷 파서 (Custom support for user format)"""

    def parse(self, file_path: str) -> List[Dict]:
        """
        CoNLL-U 파일을 파싱하여 문장 정보를 반환

        Returns:
            List of sentences, where each sentence is:
            {
                "text": "Full sentence text",
                "tokens": [
                    {
                        "id": 1,
                        "form": "워드",
                        "lemma": "기본형",
                        "upos": "POS",
                        "head": 0,
                        "deprel": "root",
                        "morphs": [("word", "tag"), ...]
                    },
                    ...
                ]
            }
        """
        sentences = []
        current_tokens = []

        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()

                # Comment line
                if line.startswith("#"):
                    continue

                # Empty line = End of sentence
                if not line:
                    if current_tokens:
                        sentences.append(self._build_sentence(current_tokens))
                        current_tokens = []
                    continue

                parts = line.split("\t")
                if len(parts) < 8:
                    # Tabs might be spaces?
                    parts = line.split()

                if len(parts) < 8:
                    continue

                # Heuristic for column detection
                # Standard: ID(0) FORM(1) LEMMA(2) UPOS(3) XPOS(4) FEATS(5) HEAD(6) DEPREL(7) ...
                # User (Predicted): ID(0) FORM(1) LEMMA(2) UPOS(3) XPOS(4) HEAD(5) DEPREL(6) ...

                token = {
                    "id": int(parts[0]),
                    "form": parts[1],
                    "lemma": parts[2],
                    "upos": parts[3],
                    # ...
                }

                # Detect HEAD column
                # Standard HEAD is at index 6. User example seems to have it at index 5.
                head_idx = 6
                if parts[5].isdigit() and not parts[6].isdigit():
                    # If col 5 is digit (HEAD) and col 6 is string (DEPREL) -> Shifted format (Missing FEAT)
                    head_idx = 5

                # HEAD & DEPREL
                try:
                    token["head"] = (
                        int(parts[head_idx]) if parts[head_idx] != "_" else 0
                    )
                    token["deprel"] = parts[head_idx + 1]
                except (ValueError, IndexError):
                    token["head"] = 0
                    token["deprel"] = "root"

                # Extract Morphs
                # 1. Try parsing from LEMMA/XPOS (KAIST Style: Lemma="A+B", XPOS="t1+t2")
                token["morphs"] = []
                lemma_parts = parts[2].split("+")
                xpos_parts = parts[4].split("+")

                if len(lemma_parts) == len(xpos_parts):
                    for l, p in zip(lemma_parts, xpos_parts):
                        norm_p = self._normalize_tag(p)
                        # Clean lemma (remove noise if any?)
                        token["morphs"].append((l, norm_p))

                # 2. If empty, try MISC (Old logic)
                if not token["morphs"]:
                    morph_str = parts[-1]
                    token["morphs"] = self._parse_morphs(morph_str)

                current_tokens.append(token)

            if current_tokens:
                sentences.append(self._build_sentence(current_tokens))

        return sentences

    def _build_sentence(self, tokens: List[Dict]) -> Dict:
        # Reconstruct full text from tokens
        # Assuming space separation for now
        text = " ".join([t["form"] for t in tokens])
        return {"text": text, "tokens": tokens}

    def _parse_morphs(self, morph_str: str) -> List[Tuple[str, str]]:
        if "_" == morph_str:
            return []

        morphs = []
        # Support "word/tag + word/tag"
        for chunk in morph_str.split("+"):
            chunk = chunk.strip()
            if "/" in chunk:
                word, pos = chunk.rsplit("/", 1)
                pos = self._normalize_tag(pos.strip())
                morphs.append((word.strip(), pos))
            else:
                # Fallback?
                morphs.append((chunk, "UNK"))
        return morphs

    def _normalize_tag(self, tag: str) -> str:
        """KAIST 등 비표준 태그를 세종 표준(TTAK.KO-11.0010/R1)으로 변환"""
        tag_lower = tag.lower()

        # KAIST -> Sejong Mapping
        mapping = {
            # 체언
            "ncn": "NNG",
            "ncpa": "NNG",
            "ncps": "NNG",
            "nq": "NNP",
            "nqq": "NNP",
            "nbu": "NNB",
            "nbn": "NNB",
            "pp": "NP",
            "np": "NP",
            "nnc": "NR",
            "nno": "NR",
            # 용언
            "pvg": "VV",
            "pvd": "VV",
            "paa": "VA",
            "pad": "VA",
            "px": "VX",
            "jp": "VCP",  # 이다
            # 수식언
            "mm": "MM",
            "mag": "MAG",
            "maj": "MAJ",
            # 관계언
            "jcs": "JKS",
            "jcc": "JKC",
            "jco": "JKO",
            "jcm": "JKB",
            "jca": "JKB",
            "jcr": "JKB",  # 부사격
            "jcv": "JKV",
            "jxc": "JX",
            "jxt": "JX",
            "jxf": "JX",
            "jcj": "JC",
            "jct": "JC",
            # 어미
            "ep": "EP",
            "ef": "EF",
            "ecx": "EC",
            "ecs": "EC",
            "ecc": "EC",
            "etn": "ETN",
            "etm": "ETM",
            # 접사
            "xsn": "XSN",
            "xsv": "XSV",
            "xsa": "XSA",
            # 기호
            "sf": "SF",
            "sp": "SP",
            "ss": "SS",
            "se": "SE",
            "so": "SO",
            "sw": "SW",
            # 기타
            "sl": "SL",
            "sh": "SH",
            "sn": "SN",
        }

        # 1. 매핑 테이블 확인
        if tag_lower in mapping:
            return mapping[tag_lower]

        # 2. 이미 표준 태그인 경우 (대문자 변환)
        # TTA 표준 태그 목록 (약식 확인)
        standard_tags = {
            "NNG",
            "NNP",
            "NNB",
            "NR",
            "NP",
            "VV",
            "VA",
            "VX",
            "VCP",
            "VCN",
            "MM",
            "MAG",
            "MAJ",
            "IC",
            "JKS",
            "JKC",
            "JKG",
            "JKO",
            "JKB",
            "JKV",
            "JKQ",
            "JX",
            "JC",
            "EP",
            "EF",
            "EC",
            "ETN",
            "ETM",
            "XPN",
            "XSN",
            "XSV",
            "XSA",
            "XR",
            "SF",
            "SP",
            "SS",
            "SE",
            "SO",
            "SW",
            "SL",
            "SH",
            "SN",
            "NA",
        }

        tag_upper = tag.upper()
        if tag_upper in standard_tags:
            return tag_upper

        # 변환 실패 시 원본 반환 (또는 UNK 처리)
        return tag
