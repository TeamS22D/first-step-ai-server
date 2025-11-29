# 채팅 평가 루브릭

## 평가 방식
- 아래 평가 기준표의 **모든 세부 항목**을 참고하여 점수를 계산합니다.
- 최종 피드백은 **대분류** 기준으로 요약하여 제공합니다.ㅊ

| 평가 항목 | 배점 | 세부 항목 | 세부 배점 | 측정 기준 | 평가 방식 |
|-----------|------|------------|------------|------------|------------|
| 구조·형식 | 20 | 제목 구조 적절성 | 5 | [말머리][핵심 주제] 형태, 10-25자 | regex·패턴 |
|           |    | 수신/참조 구분 | 4 | TO/CC 목적에 맞게 구분 | presence |
|           |    | 단락 구분 및 순서 | 4 | 인사→목적→본문→마무리 | keyword order |
|           |    | 서식 일관성 | 4 | 불릿, 줄바꿈, 강조 통일 | style check |
|           |    | 첨부파일 언급 | 3 | 첨부 시 본문 언급 | attachment match |
| 목적·핵심성 | 20 | 첫 문단 목적 명시 | 6 | 첫 2문장 내 요청/보고 명시 | position |
|           |    | 주요 키워드 포함 | 5 | 핵심 용어 포함 | keyword presence |
|           |    | 배경 맥락 제시 | 5 | 발송 이유 설명 | contextual sentence |
|           |    | 응답 요구사항 명확성 | 4 | 구체적 액션 요청 | specificity check |
| 완결성 | 20 | 필수 정보 완비 | 6 | 5W1H 요소 포함 | field coverage |
|         |    | 구체성·정량화 | 5 | 70% 완료 vs 진행 중 | specificity ratio |
|         |    | 후속 단계 제시 | 5 | 다음 단계 명시 | presence |
|         |    | 기한 명시 | 4 | YYYY-MM-DD 형식 | date pattern |
| 명료성·가독성 | 15 | 문장 길이 적정성 | 5 | 평균 25어절 이하 | tokenizer |
|             |    | 간결한 표현 | 4 | 군더더기 10% 이하 | stopword/frequency |
|             |    | 능동형 문장 사용 | 3 | 능동형 70% 이상 | morphological pattern |
|             |    | 전문용어 설명 | 3 | 약어 풀네임 병기 | acronym check |
| 근거·신뢰성 | 10 | 수치·데이터 근거 | 4 | 정확한 수치 제시 | number/date |
|             |    | 출처·참조 명시 | 3 | 관련 문서/링크 | hyperlink/citation |
|             |    | 확정적 표현 | 3 | ~입니다 vs ~같습니다 | modal pattern |
| 실행가능성 | 10 | 액션아이템 명시 | 3 | To-do 리스트 형태 | intent detection |
|             |    | 책임 주체 명시 | 3 | 담당자/부서 지정 | named entity |
|             |    | 구체적 일정 | 2 | 모호한 표현 지양 | date/time pattern |
|             |    | 리스크 대응 | 2 | Plan B 제시 | keyword match |
| 어조·매너 | 5 | 인사말 | 1 | 시작/종료 인사 | greeting/closing |
|            |   | 존칭 사용 | 2 | 존칭 90% 이상 | polite form ratio |
|            |   | 긍정적 어조 | 1 | 부정 표현 최소화 | sentiment analysis |
|            |   | 적절한 톤 | 1 | 비즈니스 중립 톤 | sentiment window |
| 보안·기밀성 | 5 | 민감정보 보호 | 2 | 개인정보 마스킹 | regex pattern |
|             |   | 기밀 표시 | 2 | 대외비/기밀 표시 | keyword check |
|             |   | 수신자 확인 | 1 | 외부 도메인 주의 | domain check |
| 합계 | 100 |  |  |  |  |
