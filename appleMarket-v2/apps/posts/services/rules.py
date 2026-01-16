import re
from typing import Dict, Optional, Tuple

SEP = r"(?:\s*[:：]?\s*)"
NUM = r"(\d+(?:[.,]\d+)?)"
UNIT = r"(?:\s*(mg|g|9|q))?"
PERCENT = r"(?:\s*(\d+)\s*%)"


def _base_result(error: Optional[str] = None) -> Dict[str, Optional[float]]:
    return {
        "calories": None,
        "carbs": None,
        "protein": None,
        "fat": None,
        "error": error,
    }


def _to_float(s: str) -> float:
    return float(s.replace(",", "."))


def _normalize_text(text: str) -> str:
    if not text:
        return ""

    t = text
    t = re.sub(r"\b理\b", "단백질", t)

    for kw in ("단백질", "지방", "탄수화물"):
        t = re.sub(rf"({kw}{SEP})(\d+)\s*(9|q)\b", r"\1\2 g", t, flags=re.IGNORECASE)

    t = re.sub(r"단백\s*질", "단백질", t)
    t = re.sub(r"지\s*방", "지방", t)
    t = re.sub(r"탄수\s*화물", "탄수화물", t)

    return t


def _extract_calories(text: str) -> Optional[float]:
    pats = [
        re.compile(rf"{NUM}\s*kca[l1i]", re.IGNORECASE),
        re.compile(rf"열량{SEP}{NUM}\s*(?:kca[l1i])?", re.IGNORECASE),
        re.compile(rf"칼로리{SEP}{NUM}\s*(?:kca[l1i])?", re.IGNORECASE),
        re.compile(rf"에너지{SEP}{NUM}\s*(?:kca[l1i])?", re.IGNORECASE),
    ]
    for p in pats:
        m = p.search(text)
        if m:
            try:
                return _to_float(m.group(1))
            except:
                pass
    return None


def _extract_percent(text: str, keyword: str) -> Optional[int]:
    """키워드 근처 퍼센트 추출"""
    pat = re.compile(rf"{keyword}[^%]*?(\d+)\s*%", re.IGNORECASE)
    m = pat.search(text)
    if m:
        try:
            return int(m.group(1))
        except:
            pass
    return None


def _fix_decimal_for_small_nutrients(value: float, nutrient: str, raw: str, text: str, keyword: str) -> float:
    if nutrient not in ("fat", "protein"):
        return value

    # 패턴 기반 판단
    suspicious = bool(re.search(r"\d\s+\d", raw)) or ("9" in raw.lower()) or ("q" in raw.lower())
    
    # 퍼센트 기반 판단
    percent = _extract_percent(text, keyword)
    if percent is not None:
        if nutrient == "protein" and value >= 10 and percent < 20:
            suspicious = True
        elif nutrient == "fat" and value >= 10 and percent < 15:
            suspicious = True
    
    if suspicious and 10 <= value < 100:
        return round(value / 10, 1)
    
    return value


def _extract_nutrient(text: str, keyword: str, nutrient_key: str) -> Optional[float]:
    pat = re.compile(rf"{keyword}\s*(?:\([^)]*\))?{SEP}{NUM}{UNIT}", re.IGNORECASE)
    m = pat.search(text)
    if not m:
        return None

    raw = m.group(0)
    try:
        value = _to_float(m.group(1))
    except:
        return None

    unit = (m.group(2) or "").lower()
    if unit in ("9", "q"):
        unit = "g"
    if unit == "mg":
        value /= 1000

    value = round(value, 1)
    return _fix_decimal_for_small_nutrients(value, nutrient_key, raw, text, keyword)


def parse_nutrition(raw_text: str) -> Dict[str, Optional[float]]:
    text = _normalize_text(raw_text)

    calories = _extract_calories(text)
    carbs = _extract_nutrient(text, "탄수화물", "carbs")
    protein = _extract_nutrient(text, "단백질", "protein")
    fat = _extract_nutrient(text, "지방", "fat")

    result = _base_result()
    result.update({
        "calories": calories,
        "carbs": carbs,
        "protein": protein,
        "fat": fat,
    })

    if calories is None and carbs is None and protein is None and fat is None:
        result["error"] = "영양성분을 인식하지 못했습니다."

    return result


class NutritionExtractor:
    @classmethod
    def extract_all(cls, text: str) -> Dict[str, Optional[float]]:
        return parse_nutrition(text)