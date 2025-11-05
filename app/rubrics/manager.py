import os
from pathlib import Path
import openpyxl
from .models import Rubric, BaseCriterion, WeightedCriterion, SpecializedCriterion
from typing import Optional, Any, List, Dict


class RubricManager:
    def __init__(self, rubrics_dir: str = "app/rubrics"):
        self.rubrics_dir = Path(rubrics_dir)
        self.rubrics: Dict[str, Rubric] = {}
        self._load_all_rubrics()

    def _load_all_rubrics(self):
        """rubrics_dir에서 모든 루브릭을 불러옵니다."""
        if not self.rubrics_dir.is_dir():
            return
        for file_path in self.rubrics_dir.glob("*.xlsx"):
            rubric_name = file_path.stem
            self.rubrics[rubric_name] = self._parse_rubric_file(file_path)

    def _parse_rubric_file(self, file_path: Path) -> Rubric:
        """Parses a single .xlsx rubric file based on the new structure."""

        workbook = openpyxl.load_workbook(file_path)
        rubric = Rubric(name=file_path.stem)

        # Parse '기본 평가표'
        if '기본 평가표' in workbook.sheetnames:
            sheet = workbook['기본 평가표']
            current_major_item = ""
            current_score = 0
            # Headers are in the 3rd row, data starts from 4th
            for row in sheet.iter_rows(min_row=4, values_only=True):
                if row[0] is not None and row[0] != "":
                    current_major_item = row[0]
                    current_score = row[1]
                if row[2] is not None:  # 세부 항목이 있는 경우
                    rubric.base_criteria.append(BaseCriterion(
                        major_item=current_major_item,
                        score=current_score,
                        minor_item=row[2],
                        minor_score=row[3],
                        evaluation_criteria=row[4],
                        measurement_point=row[5],
                        evaluation_method=row[6]
                    ))

        # Parse '유형별 가중치'
        if '유형별 가중치' in workbook.sheetnames:
            sheet = workbook['유형별 가중치']
            headers = [cell.value for cell in sheet[3]]  # Headers in 3rd row
            # Data starts from 4th row
            for row in sheet.iter_rows(min_row=4, max_row=sheet.max_row, values_only=True):
                if row[0] is not None:
                    weights = {header: weight for header, weight in zip(headers[1:], row[1:]) if
                               header is not None and weight is not None}
                    rubric.weighted_criteria.append(WeightedCriterion(
                        item=row[0],
                        weights=weights
                    ))

        # Parse '특화 평가항목'
        if '특화 평가항목' in workbook.sheetnames:
            sheet = workbook['특화 평가항목']
            current_doc_type = ""
            # Data starts from 4th row
            for row in sheet.iter_rows(min_row=4, values_only=True):
                if row[0] is not None and row[0] != "":
                    current_doc_type = row[0]
                if row[1] is not None:
                    rubric.specialized_criteria.append(SpecializedCriterion(
                        doc_type=current_doc_type,
                        item=row[1],
                        criteria=row[2],
                        score=row[3],
                        measurement_method=row[4]
                    ))

        return rubric

    def get_rubric(self, name: str) -> Optional[Rubric]:
        """
        이름을 통해 루브릭을 찾음
        <name>형식 이거나 <name.rubric>의 형태를 갖춤
        """
        if name.startswith("rubric."):
            name = name.split(".", 1)[1]

        if name not in self.rubrics:
            self._load_all_rubrics()  # Refresh if not found

        return self.rubrics.get(name)
