from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

# 1. 최하위 항목 (평가 기준)
@dataclass
class CriteriaItem:
    """단일 평가 기준 항목"""
    name: str
    score: int
    description: str

# 2. 카테고리 (기본 루브릭의 요소)
@dataclass
class Category:
    """기본 평가 루브릭의 카테고리"""
    category: str  # JSON 키와 일치하도록 'category'로 이름 변경
    total_score: int
    criteria: List[CriteriaItem] = field(default_factory=list)

# 3. 특수 문서 유형의 세부 내용
@dataclass
class SpecialTypeDetail:
    """weekly_report, release_note 등의 특수 문서 유형 세부 구조"""
    weights: Dict[str, int]
    special_rubric: List[CriteriaItem] = field(default_factory=list)

# 4. 루브릭 전체 구조
@dataclass
class Rubric:
    """전체 평가 루브릭을 담는 최상위 구조"""
    rubric_name: str  # JSON 키와 일치하도록 'rubric_name'으로 변경
    basic_rubric: List[Category] = field(default_factory=list)
    # special_types는 문서 유형(str)을 키로, 세부 구조(SpecialTypeDetail)를 값으로 가집니다.
    special_types: Dict[str, SpecialTypeDetail] = field(default_factory=dict)