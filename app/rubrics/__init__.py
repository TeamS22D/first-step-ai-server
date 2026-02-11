import json
import os
from typing import Dict, Any

# rubrics 디렉토리의 절대 경로를 가져옵니다.
rubrics_dir = os.path.dirname(__file__)

def get_rubric(document_type: str) -> Dict[str, Any]:
    """
    document_type에 해당하는 루브릭 JSON 파일을 읽어와 딕셔너리로 반환합니다.
    파일 이름은 'document_rubric.json', 'document_rubric_v2.json' 등과 같을 것으로 예상합니다.
    """
    # document_type으로부터 파일 이름을 유추합니다. 예: "document_v1" -> "document_rubric.json"
    # 간단한 예시로, document_type을 파일 이름의 일부로 가정합니다.
    # 실제로는 더 복잡한 매핑이 필요할 수 있습니다.
    if document_type == "document_v1":
        file_name = "document_rubric.json"
    elif document_type == "document_v2":
        file_name = "document_rubric_v2.json"
    elif document_type == "email":
        file_name = "email_rubric.json"
    else:
        # 기본 루브릭 또는 에러 처리
        # 여기서는 document_rubric.json을 기본으로 사용하겠습니다.
        file_name = "document_rubric.json"

    file_path = os.path.join(rubrics_dir, file_name)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            # Pydantic 모델 등으로 파싱이 필요하다면 여기서 처리할 수 있습니다.
            # 우선은 JSON 객체를 그대로 반환합니다.
            # 하지만 eval_document_v1.py에서는 .base_criteria를 사용하므로,
            # 실제로는 Pydantic 모델 객체를 반환해야 할 수 있습니다.
            # 지금은 해당 파일이 없으므로 일단 Dict를 반환합니다.
            # rubric_manager.models.Rubric 가 필요해 보입니다.
            from app.utils.rubric_manager.models import Rubric
            rubric_data = json.load(f)
            return Rubric(**rubric_data)

    except FileNotFoundError:
        raise FileNotFoundError(f"Rubric file not found for document type: {document_type} at path {file_path}")
    except json.JSONDecodeError:
        raise ValueError(f"Error decoding JSON from rubric file: {file_path}")

