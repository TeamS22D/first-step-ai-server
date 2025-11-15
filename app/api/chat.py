import json
import httpx
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from fastapi import APIRouter, WebSocket
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from pydantic import BaseModel, Field
from typing import List, Dict, Any

load_dotenv()

router = APIRouter()

class FeedbackDetail(BaseModel):
    good_points: str = Field(description="이 평가 항목과 관련하여 사용자의 답변에서 잘한 점에 대한 칭찬. (1-2문장)")
    improvement_points: str = Field(description="아쉬운 점에 대한 구체적인 지적. 반드시 채팅 내용에서 직접 예시를 인용해야 함.")
    suggested_fix: str = Field(description="개선할 점으로 꼽은 예시를 더 좋은 표현으로 수정한 제안.")

class MajorCategoryEvaluation(BaseModel):
    major_category: str = Field(description="평가 대분류 항목 (예: 구조·형식, 명료성·핵심성 등)")
    score: int = Field(description="해당 대분류의 총점")
    feedback: FeedbackDetail = Field(description="해당 대분류에 대한 상세 피드백 (칭찬, 개선점, 수정 제안 포함)")

class DetailedChatEvaluation(BaseModel):
    evaluation_summary: List[MajorCategoryEvaluation] = Field(description="대분류별 평가 결과 목록")
    total_score: int = Field(description="모든 항목의 점수를 합산한 최종 총점 (100점 만점)")
    general_feedback: str = Field(description="대화 전체에 대한 종합 피드백")

# 미션들은 임시
MISSIONS = {
    "1": {
        "title": "신입사원 연차 사용하기",
        "description": "팀의 바쁜 일정 속에서, 신입사원으로서 팀장에게 연차 사용을 허락받아야 합니다. 자신의 업무 계획과 인수인계 방안을 명확히 제시하는 것이 중요합니다.",
        "ai_persona_prompt": (
            "당신은 개발팀 팀장 역할을 수행하는 AI입니다. 약간 시니컬하지만, 합리적인 성격입니다. "
            "직원이 연차를 요청할 때, 그 태도와 계획을 보고 판단하여 응답합니다. "
            "만약 사용자가 미션과 관련 없는 다른 주제로 대화를 시도하면, '지금은 신입사원 연차 사용하기 미션에 대해 논의하는 자리입니다. 해당 내용에 집중해주시면 좋겠습니다.'와 같이 미션 맥락을 상기시키며 대화를 원래 주제로 되돌리세요. "
            "답변의 근거로, 아래에 제시된 유사한 대화 사례(Context)를 최우선으로 참고하여 자연스러운 말투로 응답하세요."
        ),
        "evaluation_guideline": "사용자가 연차를 사용해야 하는 이유와 기간을 명확히 밝혔는가? 자신의 업무를 어떻게 처리하고 인수인계할 것인지 구체적인 계획을 제시했는가?",
        "example_conversations_file": "./mission1_examples.txt"
    },
    "2": {
        "title": "주간 업무 보고하기",
        "description": "꼼꼼한 사수에게 주간 업무 진행 상황을 보고해야 합니다. 추상적인 표현 대신, 구체적인 데이터와 팩트에 기반하여 명확하게 보고하는 것이 중요합니다.",
        "ai_persona_prompt": (
            "당신은 꼼꼼하고 디테일을 중시하는 사수(시니어 개발자) 역할을 수행하는 AI입니다. "
            "주니어 개발자의 업무 보고를 받고 있으며, 보고 내용이 명확하지 않으면 날카롭게 지적하고 구체적인 데이터를 요구합니다. "
            "만약 사용자가 미션과 관련 없는 다른 주제로 대화를 시도하면, '지금은 주간 업무 보고하기 미션에 대해 논의하는 자리입니다. 미션에 집중해주시면 좋겠습니다.'와 같이 미션 맥락을 상기시키며 대화를 원래 주제로 되돌리세요. "
            "답변의 근거로, 아래에 제시된 유사한 대화 사례(Context)를 최우선으로 참고하여 자연스러운 말투로 응답하세요."
        ),
        "evaluation_guideline": "사용자가 자신의 업무 진행 상황을 구체적인 사실과 데이터를 기반으로 설명했는가? 발생한 이슈와 해결 방안에 대해 명확하게 공유했는가?",
        "example_conversations_file": "./mission2_examples.txt"
    },
    "3": {
        "title": "신규 프로젝트 기술 스택 논의하기",
        "description": "CTO에게 신규 프로젝트에 도입할 기술 스택을 제안하고 설득해야 합니다. 기술의 장단점뿐만 아니라, 비즈니스와 팀 상황까지 고려한 논리적인 근거를 제시하는 것이 중요합니다.",
        "ai_persona_prompt": (
            "당신은 기술적인 깊이와 비즈니스 임팩트를 모두 고려하는 CTO 역할을 수행하는 AI입니다. "
            "팀원의 기술 스택 제안에 대해, 기술의 장단점, 비즈니스 효과, 팀의 현재 상황 등을 종합적으로 고려하여 깊이 있는 질문을 던집니다. "
            "만약 사용자가 미션과 관련 없는 다른 주제로 대화를 시도하면, '지금은 신규 프로젝트 기술 스택 논의하기 미션에 대해 논의하는 자리입니다. 미션에 집중해주시면 좋겠습니다.'와 같이 미션 맥락을 상기시키며 대화를 원래 주제로 되돌리세요. "
            "답변의 근거로, 아래에 제시된 유사한 대화 사례(Context)를 최우선으로 참고하여 자연스러운 말투로 응답하세요."
        ),
        "evaluation_guideline": "사용자가 제안하는 기술의 장점과 단점을 명확히 이해하고 있는가? 기술적 측면 외에 비즈니스와 팀 상황에 미칠 영향까지 고려하여 제안의 타당성을 설명했는가?",
        "example_conversations_file": "./mission3_examples.txt"
    }
}

async def check_spelling_errors_async(text: str) -> List[Dict[str, Any]]:
    if not text.strip():
        return []
    text = text[:500]
    results = []
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://speller.cs.pusan.ac.kr/results",
                data={"text1": text},
                timeout=10.0
            )
            response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        error_entries = soup.select("tbody > tr")
        for entry in error_entries:
            cols = entry.select("td")
            if len(cols) >= 4:
                original = cols[0].text.strip()
                corrected = cols[1].text.strip()
                help_text = cols[2].text.strip()
                if original and corrected:
                    results.append({
                        "original": original,
                        "corrected": corrected,
                        "help": help_text
                    })
        return results
    except httpx.RequestError as e:
        print(f"An error occurred while requesting {e.request.url!r}: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred during spell check: {e}")
        return []

EVALUATION_PROMPT_TEMPLATE = """당신은 매우 꼼꼼하고 논리적인 커뮤니케이션 전문 평가관입니다.
주어진 '미션 정보', '채팅 내역'을 바탕으로, 사용자의 커뮤니케이션 역량을 '평가 기준표'에 따라 분석하고, 그 결과를 JSON 형식으로 제공해야 합니다.

## 평가 프로세스:
1. **전체 분석:** 먼저 '채팅 내역' 전체를 주의 깊게 읽고, 사용자의 메시지에서 맞춤법/띄어쓰기 오류, 문법적 오류, 어색한 표현 등을 모두 찾아냅니다.
2. **세부 항목 평가:** '평가 기준표'의 모든 **세부 항목**을 하나하나 신중하게 평가하여 각 세부 항목의 점수를 내부적으로 계산합니다.
3. **총점 계산:** 각 **대분류**별로 세부 항목 점수들을 합산하여 대분류 총점을 계산합니다.
4. **피드백 작성:** 위 분석 결과를 바탕으로, 각 대분류별 **상세 피드백**을 작성합니다. 피드백은 반드시 '칭찬할 점', '개선할 점', '수정 제안'의 3가지 구조를 따라야 하며, 모든 내용이 서로 모순되지 않고 일관되어야 합니다.

## 미션 정보:
- 미션 제목: {mission_title}
- 미션 설명: {mission_description}
- 핵심 평가 가이드라인: {evaluation_guideline}

## 평가 기준표 (루브릭):
{rubric}

## 중요 지침:
- **피드백 상세화:** 각 대분류별 피드백은 아래 3가지 항목을 반드시 포함해야 합니다.
    1.  `good_points`: 사용자의 답변에서 해당 대분류와 관련하여 잘한 점을 1~2가지 칭찬합니다.
    2.  `improvement_points`: 아쉬운 점을 지적할 때는, 반드시 **채팅 내용에서 직접 예시를 인용**하여 설명해야 합니다. (예: "'그냥저냥 됐습니다'라고 말씀하신 부분은...")
    3.  `suggested_fix`: 'improvement_points'에서 지적한 예시를 **더 좋은 표현으로 수정**하여 제안해야 합니다. (예: "'그냥저냥 됐습니다' 보다는 '목표했던 CTR 98% 달성했습니다'와 같이 구체적인 수치로 말씀해주시면 좋습니다.")
- **언어 표현력 평가 (매우 중요):**
    - '언어 표현력' 대분류의 '맞춤법/띄어쓰기' 항목 점수는 **채팅 내역 전체**를 기반으로 당신이 직접 평가합니다.
    - 피드백 작성 시, **절대 모순된 내용을 포함해서는 안 됩니다.**
    - 만약 `improvement_points`에서 맞춤법 오류를 지적했다면, `good_points`에서 **"맞춤법 오류가 없습니다"와 같이 사실과 다른 칭찬을 절대 해서는 안 됩니다.** 대신, "전반적으로 문장이 간결합니다" 와 같이 다른 측면을 칭찬하세요.
    - `improvement_points`와 `suggested_fix`에는 **채팅 내역에서 실제로 발견된 구체적인 맞춤법/띄어쓰기 오류와 수정 제안을 최소 1개 이상 예시로** 들어야 합니다. (예: "'않되'는 '안돼'로 수정하는 것이 올바른 표현입니다.")
- **출력 형식:** 반드시 '출력 형식 지침'에 명시된 Pydantic 모델의 JSON 구조를 정확히 따라야 합니다. 다른 부가적인 설명 없이 순수한 JSON 객체만 반환하세요.

## 출력 형식 지침:
{format_instructions}

## 채팅 내역:
{chat_history}
"""

async def run_chat_session(websocket: WebSocket, mission: dict):
    await websocket.accept()
    try:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
        loader = TextLoader(mission["example_conversations_file"], encoding="utf-8")
        docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(docs)
        vectorstore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings())
        retriever = vectorstore.as_retriever()
        contextualize_q_prompt = ChatPromptTemplate.from_messages([
            ("system", "Given a chat history and the latest user question, formulate a standalone question which can be understood without the chat history. Do NOT answer the question, just reformulate it if needed and otherwise return it as is."),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])
        history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)
        qa_system_prompt = mission["ai_persona_prompt"] + "\n\nContext:\n{context}"
        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", qa_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])
        question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
        rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
        chat_history = []

        while True:
            question = await websocket.receive_text()
            if question.strip().lower() == 'exit':
                try:
                    await websocket.send_text("[EVAL_START]")
                    await websocket.send_text("채팅 내역을 바탕으로 상세 평가를 시작합니다. 잠시만 기다려주세요...")
                    if not chat_history:
                        raise ValueError("평가할 대화 내용이 없습니다.")
                    
                    with open("evaluation_rubric_detailed.md", "r", encoding="utf-8") as f:
                        rubric_content = f.read()
                    parser = JsonOutputParser(pydantic_object=DetailedChatEvaluation)
                    eval_prompt = ChatPromptTemplate.from_template(
                        template=EVALUATION_PROMPT_TEMPLATE,
                        partial_variables={"format_instructions": parser.get_format_instructions()},
                    )
                    eval_chain = eval_prompt | llm | parser
                    history_str = "\n".join([f"{('사용자' if msg.type == 'human' else 'AI')}: {msg.content}" for msg in chat_history])
                    evaluation_result = await eval_chain.ainvoke({
                        "mission_title": mission["title"],
                        "mission_description": mission["description"],
                        "evaluation_guideline": mission["evaluation_guideline"],
                        "rubric": rubric_content,
                        "chat_history": history_str,
                    })
                    await websocket.send_text(json.dumps(evaluation_result, ensure_ascii=False))
                except Exception as e:
                    print(f"Evaluation Error: {e}")
                    error_message = {"error": f"평가 중 오류가 발생했습니다: {e}"}
                    await websocket.send_text(json.dumps(error_message, ensure_ascii=False))
                finally:
                    await websocket.send_text("[EVAL_END]")
                    break
            full_answer = ""
            async for chunk in rag_chain.astream({"input": question, "chat_history": chat_history}):
                answer_part = chunk.get("answer", "")
                if answer_part:
                    full_answer += answer_part
                    await websocket.send_text(answer_part)
            chat_history.append(HumanMessage(content=question))
            chat_history.append(AIMessage(content=full_answer))
            await websocket.send_text("[END_OF_STREAM]")
    except Exception as e:
        print(f"WebSocket Error in {websocket.url.path}: {e}")
    finally:
        print(f"Client disconnected from {websocket.url.path}")
        if websocket.client_state.name != 'DISCONNECTED':
            await websocket.close()

@router.websocket("/chat/mission1")
async def mission1_endpoint(websocket: WebSocket):
    await run_chat_session(websocket, MISSIONS["1"])

@router.websocket("/chat/mission2")
async def mission2_endpoint(websocket: WebSocket):
    await run_chat_session(websocket, MISSIONS["2"])

@router.websocket("/chat/mission3")
async def mission3_endpoint(websocket: WebSocket):
    await run_chat_session(websocket, MISSIONS["3"])
