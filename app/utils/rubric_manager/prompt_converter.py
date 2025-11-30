from typing import List
from app.utils.rubric_manager.models import Category

def convert_criteria_to_prompt_string(criteria_dict: dict) -> str:
    """
    루브릭의 Category 딕셔너리를 Markdown 문자열로 변환합니다.
    """
    markdown_string = ""
    for category_name, category_data in criteria_dict.items():
        # Pydantic 모델 객체일 경우를 대비하여 속성 접근
        if isinstance(category_data, Category):
            criteria_list = category_data.criteria
        # 딕셔너리일 경우
        else:
            criteria_list = category_data.get('criteria', [])

        markdown_string += f"### {category_name}\n"
        markdown_string += "| 항목 | 배점 | 설명 |\n"
        markdown_string += "|---|---|---|\n"
        for item in criteria_list:
            # Pydantic 모델 객체일 경우
            if hasattr(item, 'name'):
                name = item.name
                score = item.score
                description = item.description
            # 딕셔너리일 경우
            else:
                name = item.get('name', '')
                score = item.get('score', 0)
                description = item.get('description', '')
            markdown_string += f"| {name} | {score} | {description} |\n"
        markdown_string += "\n"
    return markdown_string
