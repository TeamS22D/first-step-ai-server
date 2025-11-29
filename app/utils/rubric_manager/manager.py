import logging
from pathlib import Path
import json
from .models import *
from typing import Optional, Any, List, Dict

def _parse_rubric_file(file_path: Path) -> Rubric:
    """.json 파일을 불러옵니다."""
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

        # 1. basic_rubric 파싱
        parsed_basic_rubric = {}
        for category_data in data.get("basic_rubric", []):
            # CriteriaItem 리스트 파싱
            criteria_items = [
                CriteriaItem(**item_data)
                for item_data in category_data.get("criteria", [])
            ]
            # Category 객체 생성
            parsed_basic_rubric[category_data.get("category")] = Category(
                criteria=criteria_items
            )


        # 2. special_types 파싱
        parsed_special_types = {}
        for type_name, type_data in data.get("special_types", {}).items():
            # SpecialTypeDetail 내부의 special_rubric (CriteriaItem 리스트) 파싱
            special_criteria_items = [
                CriteriaItem(**item_data)
                for item_data in type_data.get("special_rubric", [])
            ]

            # SpecialTypeDetail 객체 생성
            parsed_special_types[type_name] = SpecialTypeDetail(
                weights=type_data.get("weights", {}),
                special_rubric=special_criteria_items
            )

        # 3. Rubric 객체 생성 및 반환
        return Rubric(
            rubric_name=data.get("rubric_name"),
            basic_rubric=parsed_basic_rubric,
            special_types=parsed_special_types
        )

class RubricManager:
    def __init__(self, rubrics_dir: str = "app/rubrics"):
        self.rubrics_dir = Path(rubrics_dir)
        self.rubrics: Dict[str, Rubric] = {}
        self._load_all_rubrics()

    def _load_all_rubrics(self):
        """rubrics_dir에서 모든 루브릭을 불러옵니다."""
        if not self.rubrics_dir.is_dir():
            return
        for file_path in self.rubrics_dir.glob("*.json"):
            logging.debug(f"loading {file_path}")
            parsed_rubric = _parse_rubric_file(file_path)
            self.rubrics[parsed_rubric.rubric_name] = parsed_rubric

    def get_rubric(self, rubric_name: str) -> Optional[Rubric]:
        return self.rubrics.get(rubric_name)



    def get_basic_rubric(self, name: str) -> Optional[Dict[str, Category]]:
        """
        basic_rubric을 불러옵니다.
        <name> -> Basic Rubric
        """
        if name in self.rubrics:
            return self.rubrics.get(name).basic_rubric
        return None

    def get_special_weights(self, name: str, special_type :str) -> Optional[Dict[str, int]]:
        if name in self.rubrics:
            rubric = self.rubrics.get(name)
            if special_type in rubric.special_types:
                return rubric.special_types.get(special_type).weights

        return None

    def get_special_rubric(self, name: str, special_type: str) -> Optional[List[CriteriaItem]]:
        if name in self.rubrics:
            rubric = self.rubrics.get(name)
            if special_type in rubric.special_types:
                return rubric.special_types.get(special_type).special_rubric
        return None
