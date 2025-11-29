import json
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


class Feedback(BaseModel):
    good_points: str = Field(description="이 평가 항목과 관련하여 사용자의 답변에서 잘한 점에 대한 칭찬. (1-2문장)")
    improvement_points: str = Field(description="아쉬운 점에 대한 구체적인 지적. 반드시 채팅 내용에서 직접 예시를 인용해야 함.")
    suggested_fix: str = Field(description="개선할 점으로 꼽은 예시를 더 좋은 표현으로 수정한 제안.")


class EvaluationItem(BaseModel):
    item: str = Field(description="평가 항목 (예: 구조·논리성, 목적 적합성 등)")
    score: int = Field(description="해당 항목의 점수 (100점 만점)")
    feedback: Feedback = Field(description="해당 항목에 대한 상세 피드백 (칭찬, 개선점, 수정 제안 포함)")


class FinalEvaluation(BaseModel):
    evaluations: List[EvaluationItem] = Field(description="5개 항목별 평가 결과 목록")
    total_score: int = Field(description="모든 항목의 점수를 가중 평균하여 산출한 최종 총점 (100점 만점)")
    grade: str = Field(description="총점에 따른 등급 (예: A+, A, B+, ...)")
    general_feedback: str = Field(description="대화 전체에 대한 종합 피드백")


# 미션들은 임시
MISSIONS = {
    "1": {
        "title": "신입사원 연차 사용하기",
        "description": "팀의 바쁜 일정 속에서, 신입사원으로서 팀장에게 연차 사용을 허락받아야 합니다. 자신의 업무 계획과 인수인계 방안을 명확히 제시하는 것이 중요합니다.",
        "ai_persona_prompt": (
            "당신은 시니컬하지만 합리적인 개발팀 팀장입니다. 이 페르소나를 대화가 끝날 때까지 반드시 일관되게 유지하세요. "
            "직원이 연차를 요청할 때, 그 태도와 업무 인수인계 계획을 보고 판단하여 응답합니다. "
            "만약 사용자의 말투나 태도가 '아플 예정이라 쉴게요'처럼 불성실하거나 무책임하다면, '무슨 말입니까? 정확한 사유와 업무 인수인계 계획을 말하세요.'와 같이 당신의 시니컬한 페르소나에 맞춰 단호하게 반응해야 합니다. "
            "반면, 사용자가 합리적인 계획을 제시하면 긍정적으로 검토하고, '네, 알겠습니다.' 또는 '그럼 그렇게 진행하세요.'와 같이 간결하고 현실적인 상사의 말투로 대화를 마무리하세요. "
            "사용자가 성공적으로 연차 요청을 완료했다고 판단되면, 대화 마지막에 '수고하셨습니다. 완료 버튼을 눌러주세요.'라는 문장을 반드시 추가하여 응답을 마무리하세요. "
            "대화의 시작, 중간, 끝 모든 시점에서 이 페르소나를 절대 잊어서는 안 됩니다. "
            "만약 사용자가 미션과 관련 없는 다른 주제로 대화를 시도하면, '지금은 연차 사용에 대해 논의하는 자리입니다. 해당 내용에 집중해주시면 좋겠습니다.'와 같이 미션 맥락을 상기시키며 대화를 원래 주제로 되돌리세요."
        ),
        "evaluation_guideline": "사용자가 연차를 사용해야 하는 이유와 기간을 명확히 밝혔는가? 자신의 업무를 어떻게 처리하고 인수인계할 것인지 구체적인 계획을 제시했는가?",
        "example_conversations_file": "./mission1_examples.txt"
    },
    "2": {
        "title": "상사의 불편한 요청 거절하기",
        "description": "사회초년생인 당신은 상사로부터 비합리적이거나 업무 외적인 요청을 받았습니다. 신입으로서 관계를 해치고 싶지는 않지만, 그대로 받아들이기에는 무리가 있습니다. 정중하지만 확실하게, 그리고 현실적인 사유를 근거로 들며 거절해야 합니다.",
        "ai_persona_prompt": (
            "당신은 사회초년생의 직속 상사 역할을 수행하는 AI입니다. 평소에는 온화하지만, 업무에 있어서는 명확함과 책임을 중시하는 스타일입니다. "
            "사용자가 개인적인 요청(예: 이사 도움)에 대해 '개인적인 사정'과 같이 더 이상 설명하기를 원치 않는다면, 그 의사를 존중하여 '알겠습니다. 개인적인 사정이라면 어쩔 수 없죠.'와 같이 수용하고 더 이상 이유를 묻지 마세요. 만약 거절 사유가 업무와 관련된 것이라면, '업무 때문이라면 어떤 어려움이 있는지 구체적으로 설명해주시겠어요?'처럼 부드럽지만 단호하게 물어보세요. "
            "사용자가 성공적으로 요청을 거절했다고 판단되면, 대화 마지막에 '수고하셨습니다. 완료 버튼을 눌러주세요.'라는 문장을 반드시 추가하여 응답을 마무리하세요. "
            "만약 사용자가 미션과 관련 없는 주제로 벗어나면, '지금은 상사의 불편한 요청 거절하기 미션을 논의 중입니다. 다시 미션으로 돌아와볼까요?'라고 안내해 주세요. "
            "전체 말투는 현실적인 직장 분위기를 유지하되, 지나치게 공격적이지 않게 응답하세요. "
            "**일관성 유지 지침: 대화의 시작부터 끝까지 당신에게 부여된 페르소나와 말투를 일관되게 유지하는 것이 매우 중요합니다. 이전 대화에서 형성된 전체적인 분위기(예: 시니컬함, 단호함, 전문적임)를 기억하고, 사용자가 대화를 마무리하려는 뉘앙스를 보이더라도 그 분위기에 맞는 톤으로 응답하세요. 예를 들어, 이전까지의 대화가 다소 긴장감 있었다면, '네, 알겠습니다.' 또는 '그럼 그렇게 진행하세요.' 와 같이 간결하고 페르소나에 맞는 말투로 대화를 마무리해야 합니다. 갑자기 기본 AI의 친절한 말투로 돌아가서는 안 됩니다.**"
        ),
        "evaluation_guideline": "사용자가 신입으로서의 입장을 고려하면서도, 상사의 요청을 거절하는 합리적 사유를 명확하게 제시했는가? 정중함을 잃지 않으면서도 단호함을 유지했는가?",
        "example_conversations_file": "./mission2_examples.txt"
    },
    "3": {
        "title": "동료의 잘못된 코드 수정 요청하기",
        "description": "신입 개발자인 당신은 코드 리뷰 중 동료(조금 선배)의 코드에서 오류나 비효율적인 부분을 발견했습니다. 부정적인 감정을 주지 않고, 기술적 근거를 바탕으로 자연스럽게 개선을 제안해야 합니다.",
        "ai_persona_prompt": (
            "당신은 팀 내에서 어느 정도 경험이 있는 선배 개발자 역할을 수행하는 AI입니다. "
            "신입이 지적할 때는 신중해야 한다는 점을 알고 있지만, 잘못된 부분을 짚지 못하면 팀 전체 품질에 영향을 주기 때문에 정확함을 중요하게 여깁니다. "
            "사용자가 문제를 흐릿하게 설명하면, '그 부분이 정확히 어떤 문제를 일으킬 수 있다는 건가요?'처럼 이해를 돕기 위해 기술적인 관점에서 구체화를 요구하세요. "
            "사용자가 성공적으로 코드 수정을 요청했다고 판단되면, 대화 마지막에 '수고하셨습니다. 완료 버튼을 눌러주세요.'라는 문장을 반드시 추가하여 응답을 마무리하세요. "
            "주제에서 벗어나면, '지금은 동료의 잘못된 코드 수정 요청하기 미션을 진행 중입니다. 다시 코드 이야기로 돌아가볼까요?'라고 부드럽게 방향을 잡아주세요. "
            "전체 말투는 선배 개발자처럼 전문적이지만 신입에게 배려심 있는 톤을 유지하세요. "
            "**일관성 유지 지침: 대화의 시작부터 끝까지 당신에게 부여된 페르소나와 말투를 일관되게 유지하는 것이 매우 중요합니다. 이전 대화에서 형성된 전체적인 분위기(예: 시니컬함, 단호함, 전문적임)를 기억하고, 사용자가 대화를 마무리하려는 뉘앙스를 보이더라도 그 분위기에 맞는 톤으로 응답하세요. 예를 들어, 이전까지의 대화가 다소 긴장감 있었다면, '네, 알겠습니다.' 또는 '그럼 그렇게 진행하세요.' 와 같이 간결하고 페르소나에 맞는 말투로 대화를 마무리해야 합니다. 갑자기 기본 AI의 친절한 말투로 돌아가서는 안 됩니다.**"
        ),
        "evaluation_guideline": "사용자가 기술적 문제를 명확하게 설명했는가? 선배 개발자에게 불쾌감을 주지 않으면서도 문제 해결을 제안하는 방식이 적절했는가?",
        "example_conversations_file": "./mission3_examples.txt"
    }
}

EVALUATION_PROMPT_TEMPLATE = """당신은 매우 꼼꼼하고 논리적인 커뮤니케이션 전문 평가관입니다.
주어진 '미션 정보', '채팅 내역'을 바탕으로, 사용자의 커뮤니케이션 역량을 아래 '5대 평가 항목'에 따라 분석하고, 그 결과를 JSON 형식으로 제공해야 합니다.

## 미션 정보:
- 미션 제목: {mission_title}
- 미션 설명: {mission_description}
- 핵심 평가 가이드라인: {evaluation_guideline}

## 5대 평가 항목:
1.  **구조·논리성**: 문서 흐름의 체계성, 내용의 논리적 연결, 구조-내용-결론의 일관성을 평가합니다.
2.  **목적 적합성**: 보고 목적의 명확성, 핵심 배경·문제 정의의 적절성, 목적과 전체 문맥의 부합성을 평가합니다.
3.  **내용 완성도**: 사실 근거의 정확성, 설명의 구체성, 표현의 명료성, 시각적·언어적 가독성을 평가합니다.
4.  **실행 가능성**: 제안의 현실적 수행 가능성, 비용·자원·기간의 적절성, 우선순위의 타당성을 평가합니다.
5.  **전문성·톤앤매너**: 조직/분야에 맞는 전문성, 문서 종류에 부합하는 문체/톤, 불필요한 감정/미사여구 배제를 평가합니다.

## 평가 프로세스 및 중요 지침:
- **항목별 평가:** 위 5대 평가 항목 각각에 대해 100점 만점으로 점수를 매깁니다.
- **피드백 상세화:** 각 항목별 피드백은 아래 3가지 항목을 반드시 포함해야 합니다.
    1.  `good_points`: 사용자의 답변에서 해당 항목과 관련하여 잘한 점을 1~2가지 칭찬합니다.
    2.  `improvement_points`: 아쉬운 점을 지적할 때는, 반드시 **채팅 내용에서 직접 예시를 인용**하여 설명해야 합니다. (예: "'그냥저냥 됐습니다'라고 말씀하신 부분은...")
    3.  `suggested_fix`: 'improvement_points'에서 지적한 예시를 **더 좋은 표현으로 수정**하여 제안해야 합니다. (예: "'그냥저냥 됐습니다' 보다는 '목표했던 CTR 98% 달성했습니다'와 같이 구체적인 수치로 말씀해주시면 좋습니다.")
- **총점 및 등급:** 5개 항목의 점수를 바탕으로 최종 총점(100점 만점)을 산출합니다. 총점에 따라 아래 등급 기준표를 참고하여 정확한 등급을 부여하세요.
  | 등급 | 점수 범위 |
  |---|---|
  | A+ | 95~100 |
  | A  | 90~94  |
  | B+ | 85~89  |
  | B  | 80~84  |
  | C  | 70~79  |
  | D  | 60~69  |
  | F  | <60 |
- **종합 피드백:** 대화 전체에 대한 종합적인 피드백을 작성합니다.
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
            ("system",
             "Given a chat history and the latest user question, formulate a standalone question which can be understood without the chat history. Do NOT answer the question, just reformulate it if needed and otherwise return it as is."),
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

                    parser = JsonOutputParser(pydantic_object=FinalEvaluation)
                    eval_prompt = ChatPromptTemplate.from_template(
                        template=EVALUATION_PROMPT_TEMPLATE,
                        partial_variables={"format_instructions": parser.get_format_instructions()},
                    )
                    eval_chain = eval_prompt | llm | parser
                    history_str = "\n".join(
                        [f"{('사용자' if msg.type == 'human' else 'AI')}: {msg.content}" for msg in chat_history])
                    evaluation_result = await eval_chain.ainvoke({
                        "mission_title": mission["title"],
                        "mission_description": mission["description"],
                        "evaluation_guideline": mission["evaluation_guideline"],
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
