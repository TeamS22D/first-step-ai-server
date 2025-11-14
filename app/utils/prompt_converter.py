from typing import List
from app.rubrics._models import BaseCriterion
from collections import defaultdict


def convert_criteria_to_prompt_string(criteria: List[BaseCriterion]) -> str:
    """
    Converts a list of BaseCriterion objects to a human-readable string for OpenAI prompts,
    grouping by major_item.
    """
    grouped_criteria = defaultdict(list)
    for c in criteria:
        grouped_criteria[c.major_item].append(c)

    prompt_lines = []
    for major_item, minor_items in grouped_criteria.items():
        if not minor_items:
            continue
        
        # Assuming score is the same for all minor_items under a major_item
        score = minor_items[0].score
        prompt_lines.append(f"- **대항목:** {major_item} ({score}점)")
        
        for c in minor_items:
            prompt_lines.append(f"  - **소항목:** {c.minor_item} ({c.minor_score}점)")
            prompt_lines.append(f"    - **평가 기준:** {c.evaluation_criteria}")
            prompt_lines.append(f"    - **측정 지표:** {c.measurement_point}")
            prompt_lines.append(f"    - **평가 방법:** {c.evaluation_method}")
            
    return "\n".join(prompt_lines)
