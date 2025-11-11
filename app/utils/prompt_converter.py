from typing import List
from app.rubrics.models import BaseCriterion


def convert_criteria_to_prompt_string(criteria: List[BaseCriterion]) -> str:
    """
    Converts a list of BaseCriterion objects to a human-readable string for OpenAI prompts.
    """
    prompt_lines = []
    for c in criteria:
        prompt_lines.append(f"- **대항목:** {c.major_item} ({c.score}점)")
        prompt_lines.append(f"  - **소항목:** {c.minor_item} ({c.minor_score}점)")
        prompt_lines.append(f"    - **평가 기준:** {c.evaluation_criteria}")
        prompt_lines.append(f"    - **측정 지표:** {c.measurement_point}")
        prompt_lines.append(f"    - **평가 방법:** {c.evaluation_method}")
    return "\n".join(prompt_lines)
