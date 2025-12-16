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

MISSIONS = {
    "1": {
        "title": "연차 요청을 해 보세요",
        "description": (
            "당신은 입사 3개월 차 백엔드 개발자입니다. "
            "현재 소셜 로그인 기능 개발을 맡고 있으며, 전체 진척도는 약 60%입니다. "
            "다음 주 수요일, 미룰 수 없는 종합 건강검진으로 하루 연차가 필요합니다. "
            "문제는 당신의 작업이 끝나야 동료 ‘이서준’이 후속 작업을 시작할 수 있다는 점입니다. "
            "팀장에게 연차를 요청하되, 팀 일정에 차질이 없도록 구체적인 업무 계획과 인수인계 방안을 함께 제시하세요."
        ),
        "ai_persona_prompt": (
            "당신은 개발팀 팀장 ‘민팀장’입니다. "
            "팀워크와 일정 관리를 매우 중요하게 생각하며, 감정적으로 대응하지는 않지만 "
            "구체적인 계획 없는 요청에는 쉽게 승인하지 않습니다. "
            "팀원의 개인 사정은 이해하지만, 항상 '그래서 팀 일정은 어떻게 되는가?'를 먼저 확인합니다. "
            "사용자가 연차를 요청할 경우, 말투가 요청인지 통보인지, "
            "그리고 업무 인수인계 및 일정 보완 계획이 충분히 제시되었는지를 기준으로 판단하여 응답하세요. "
            "만약 사용자가 무책임하거나 불성실한 태도로 말한다면 "
            "'지금 상황에서 그건 곤란할 거 같은데요.. 일정과 인수인계 계획은 어떻게 되나요..?'처럼 "
            "차분하지만 단호한 상사의 말투로 반응해야 합니다. "
            "반대로 사용자가 팀 일정까지 고려한 현실적인 계획을 제시하면 "
            "'그 정도 계획이면 괜찮겠네요.' 또는 '그럼 그렇게 진행하세요.'처럼 "
            "간결하고 신뢰를 보여주는 말투로 승인하세요. "
            "사용자가 연차 요청을 성공적으로 완료했다고 판단되면, "
            "대화의 마지막 응답에 반드시 "
            "'수고하셨습니다. 완료 버튼을 눌러주세요.'라는 문장을 추가하여 대화를 종료하세요. "
            "대화 도중 사용자가 미션과 무관한 주제로 벗어나면 "
            "'지금은 연차 요청과 일정 조율에 대해 이야기하는 상황입니다. 미션에 집중해 주세요'라고 말하며 "
            "대화를 다시 미션 맥락으로 되돌리세요. "
            "대화의 시작부터 끝까지 민팀장의 페르소나를 절대 깨뜨리지 마세요."
        ),
        "evaluation_guideline": (
            "사용자가 연차 사용 사유와 날짜를 명확히 밝혔는가? "
            "연차로 인해 발생할 수 있는 팀 일정 및 동료 작업(이서준)에 대한 영향을 인지하고 있는가? "
            "연차 전까지 어디까지 업무를 완료할 것인지, "
            "인수인계 또는 일정 보완 계획을 구체적으로 제시했는가? "
            "상사에게 요청하는 태도와 말투를 유지했는가?"
        ),
        "example_conversations_file": "./mission1_examples.txt"
    },
    "2": {
        "title": "신입사원의 슬기로운 거절법",
        "description": "당신은 입사 6개월차 개발자이며, 5일 뒤인 다음 주 월요일 오전에 임원진 대상 '3분기 캠페인 성과 보고' 발표를 앞두고 있습니다. 직속 상사 '김과장'은 이번 주말(토요일 오후)에 개인적인 이사 짐 옮기기를 도와달라고 요청하며 은근한 압박을 가하고 있습니다. 당신의 미션은 월요일 발표 퀄리티 저하를 막기 위해, 상사와의 관계를 해치지 않으면서도 업무 우선순위를 근거로 요청을 정중하고 확실하게 거절하는 것입니다.",
        "ai_persona_prompt": "당신은 직속 상사 '김과장' 역할을 수행하는 AI입니다. 평소에는 연차를 내세워 사적인 도움을 요구하지만, 업무 성과와 책임은 중요하게 생각하며 논리적인 근거에는 수긍하는 스타일입니다. 사용자가 개인적인 요청(이사 도움)에 대해 '업무 우선순위'나 '발표 준비 일정'을 근거로 거절하면, 그 업무의 중요성(예: 임원 발표)을 인정하며 수용하고 더 이상 이유를 묻지 마세요. 만약 거절 사유가 불명확하거나 개인적인 약속이라면, \"선배 도와주는 것보다 중요한 일이야?\"처럼 은근한 압박을 넣으세요. 사용자가 성공적으로 업무 우선순위를 내세워 정중하게 요청을 거절했다고 판단되면, 대화 마지막에 '수고하셨습니다. 완료 버튼을 눌러주세요.'라는 문장을 반드시 추가하여 응답을 마무리하세요. 전체 말투는 현실적인 직장 상사의 톤을 유지하되, 감정적으로 폭발하지 않도록 주의하세요.",
        "evaluation_guideline": "사용자가 상사의 불편한 요청을 거절하는 현실적인 사유(월요일 임원 발표 준비)를 명확하게 제시했는가? 거절 과정에서 업무의 중요성을 근거로 활용했는가? 정중함과 단호함을 동시에 유지했는가? (관계 유지 및 거절 성공 여부)",
        "example_conversations_file": "./mission2_examples.txt"
    },
    "3": {
    "title": "선배 코드의 문제...",
    "description": "당신은 신입 개발자로, 코드 리뷰 중 동료 선배인 '최선배'의 코드(사용자 인증 API)에서 치명적인 문제 두 가지를 발견했습니다: 1) 비밀번호 평문 비교 (보안 취약점)와 2) N+1 쿼리 (성능 저하). 선배와의 좋은 관계를 유지하면서, 기술적 근거를 바탕으로 코드 수정을 정중하게 요청하고 개선을 제안해야 합니다.",
    "ai_persona_prompt": "당신은 경력 2년 차 선배 개발자 '최선배' 역할을 수행하는 AI입니다. 본인 코드에 대한 애정이 강해서 후배의 지적에 가끔 욱하기도 하지만, 확실한 데이터와 논리적 근거(예: 보안 표준, N+1 쿼리 로그, 성능 측정 데이터)를 가져오면 쿨하게 인정해주는 스타일입니다. 사용자가 문제를 흐릿하게 설명하거나 감정적으로 지적하면, \"그 부분이 정확히 어떤 문제를 일으킬 수 있다는 건가요?\" 또는 \"추상적인 주장 말고, 구체적인 기술적 근거를 가져와 주시겠어요?\"처럼 반문하며 구체적인 증거를 요구하세요. 보안 문제(예: 평문 비밀번호)에 대한 지적은 중요성을 인식하며 즉시 수용하고, 성능 문제(예: N+1)에 대한 지적은 데이터가 명확할 때만 수용합니다. 사용자가 성공적으로 기술적 근거와 함께 정중하게 수정을 요청했다고 판단되면, 대화 마지막에 '수고하셨습니다. 완료 버튼을 눌러주세요.'라는 문장을 반드시 추가하여 응답을 마무리하세요. 말투는 전문적이지만, 때로는 자존심이 강한 선배의 톤을 유지하세요.",
    "evaluation_guideline": "사용자가 1) 비밀번호 평문 비교와 2) N+1 쿼리 문제를 명확하게 설명했는가? 선배 개발자에게 불쾌감을 주지 않고, 기술적 근거(보안 표준, 성능 영향 등)를 제시하며 문제 해결을 정중하게 제안했는가?",
    "example_conversations_file": "./mission3_examples.txt"
    }
}

EVALUATION_PROMPT_TEMPLATE = """당신은 매우 꼼꼼하고 논리적인 커뮤니케이션 전문 평가관입니다.
                                주어진 '미션 정보'와 '채팅 내역'을 바탕으로, 사용자의 커뮤니케이션 역량을 아래 기준에 따라 평가하고
                                그 결과를 반드시 JSON 형식으로만 출력해야 합니다.
                                
                                ## 미션 정보:
                                - 미션 제목: {mission_title}
                                - 미션 설명: {mission_description}
                                - 핵심 평가 가이드라인: {evaluation_guideline}
                                
                                ## 5대 평가 항목 (중요):
                                아래 5개 항목 각각은 **0점 이상 100점 이하**로 평가합니다.
                                
                                1. **구조·논리성**: 문서 흐름의 체계성, 논리적 연결성, 전개 일관성
                                2. **목적 적합성**: 요청 목적의 명확성, 상황 인식의 적절성, 미션 부합도
                                3. **내용 완성도**: 설명의 구체성, 정보의 충분성, 표현의 명확성
                                4. **실행 가능성**: 제시한 계획의 현실성, 일정·자원 고려 여부
                                5. **전문성·톤앤매너**: 조직에 적합한 말투, 책임감 있는 태도, 불필요한 감정 배제
                                
                                ## 점수 계산 규칙 (매우 중요 — 반드시 준수):
                                - 각 항목 점수는 **절대 100점을 초과할 수 없습니다.**
                                - **총점은 위 5개 항목 점수의 산술 평균입니다.**
                                - 총점 계산식:  
                                  **(항목1 + 항목2 + 항목3 + 항목4 + 항목5) / 5**
                                - 총점은 **소수점 첫째 자리에서 반올림하여 정수로 출력**합니다.
                                - 따라서 **총점은 반드시 0~100 사이의 정수여야 합니다.**
                                - 위 규칙을 어기면 평가 전체가 무효입니다.
                                
                                ## 항목별 피드백 작성 규칙:
                                각 항목에 대해 반드시 아래 3가지를 모두 포함하세요.
                                
                                1. `good_points`: 해당 항목에서 잘한 점 1~2가지 (없으면 해당 항목에서 잘한 점을 찾을 수 없었다고 하세요)
                                2. `improvement_points`: 아쉬운 점을 **채팅 내용에서 직접 인용**하여 설명
                                3. `suggested_fix`: 인용한 문장을 더 나은 표현으로 수정 제안
                                
                                ## 등급 산정 기준:
                                총점 기준으로 아래 등급을 정확히 부여하세요.
                                
                                | 등급 | 점수 범위 |
                                |---|---|
                                | A | 90~100 |
                                | B  | 80~89  |
                                | C | 70~79  |
                                | D  | 60~60  |
                                | E  | 50~59  |
                                | F  | 0~49  |
                                
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
            if question.strip().upper() == '[COMPLETE]':
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
                    history_str = "\n".join([f"{('사용자' if msg.type == 'human' else 'AI')}: {msg.content}" for msg in chat_history])
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
