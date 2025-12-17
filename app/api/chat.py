import json
from dotenv import load_dotenv
from fastapi import APIRouter, WebSocket, HTTPException
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
from typing import List, Dict, Any, Optional
from datetime import datetime

load_dotenv()

router = APIRouter()

class Feedback(BaseModel):
    good_points: str
    improvement_points: str
    suggested_fix: str


class EvaluationItem(BaseModel):
    item: str
    score: int
    feedback: Feedback


class FinalEvaluation(BaseModel):
    evaluations: List[EvaluationItem]
    total_score: int
    grade: str
    general_feedback: str


class AIPersona(BaseModel):
    name: str
    role: str
    character: str


class ChatMissionTemplate(BaseModel):
    id: int
    title: str
    description: str
    ai_persona: AIPersona
    hint: str
    ai_persona_prompt: str
    evaluation_guideline: str
    example_conversations_file: str


class ChatMissionTemplatePublic(BaseModel):
    id: int
    title: str
    description: str
    ai_persona: AIPersona
    hint: str


class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: datetime


class ChatMissionInstance(BaseModel):
    chatMissionId: int
    templateId: int
    userId: int
    chatHistory: List[Dict[str, Any]]
    status: str
    evaluation: Optional[FinalEvaluation] = None
    createdAt: datetime
    completedAt: Optional[datetime] = None


class StartChatMissionRequest(BaseModel):
    templateId: int
    userId: int


class SaveChatRequest(BaseModel):
    chatHistory: List[Dict[str, Any]]


class CompleteChatRequest(BaseModel):
    chatHistory: List[Dict[str, Any]]

def load_missions_from_json(file_path: str = "app/missions.json") -> Dict[int, ChatMissionTemplate]:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            missions = {}
            for mission_data in data.get("chat_missions", []):
                mission = ChatMissionTemplate(**mission_data)
                missions[mission.id] = mission
            return missions
    except FileNotFoundError:
        print(f"Warning: {file_path} not found. Using empty missions.")
        return {}
    except Exception as e:
        print(f"Error loading missions: {e}")
        return {}

MISSION_TEMPLATES = load_missions_from_json()

CHAT_MISSION_INSTANCES: Dict[int, ChatMissionInstance] = {}
NEXT_CHAT_MISSION_ID = 1

@router.get("/chat-mission/templates")
async def get_all_templates():
    public_templates = [
        ChatMissionTemplatePublic(
            id=t.id,
            title=t.title,
            description=t.description,
            ai_persona=t.ai_persona,
            hint=t.hint
        )
        for t in MISSION_TEMPLATES.values()
    ]
    return {"templates": public_templates}

@router.get("/chat-mission/template/{template_id}")
async def get_template(template_id: int):
    template = MISSION_TEMPLATES.get(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    return ChatMissionTemplatePublic(
        id=template.id,
        title=template.title,
        description=template.description,
        ai_persona=template.ai_persona,
        hint=template.hint
    )

@router.post("/chat-mission/start")
async def start_chat_mission(request: StartChatMissionRequest):
    # 새로운 채팅 미션 인스턴스 시작
    global NEXT_CHAT_MISSION_ID

    template = MISSION_TEMPLATES.get(request.templateId)
    if not template:
        raise HTTPException(status_code=404, detail="Mission template not found")

    chat_mission = ChatMissionInstance(
        chatMissionId=NEXT_CHAT_MISSION_ID,
        templateId=request.templateId,
        userId=request.userId,
        chatHistory=[],
        status="in_progress",
        createdAt=datetime.now()
    )

    CHAT_MISSION_INSTANCES[NEXT_CHAT_MISSION_ID] = chat_mission
    NEXT_CHAT_MISSION_ID += 1

    return {
        "chatMissionId": chat_mission.chatMissionId,
        "templateId": chat_mission.templateId,
        "userId": chat_mission.userId,
        "chatHistory": chat_mission.chatHistory,
        "status": chat_mission.status,
        "createdAt": chat_mission.createdAt
    }


@router.get("/chat-mission/{chat_mission_id}")
async def get_chat_mission(chat_mission_id: int):
    # 특정 채팅 미션 인스턴스만 조회
    mission = CHAT_MISSION_INSTANCES.get(chat_mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Chat mission not found")
    return mission


@router.patch("/chat-mission/save/{chat_mission_id}")
async def save_chat_mission(chat_mission_id: int, request: SaveChatRequest):
    # 채팅 중간 저장
    mission = CHAT_MISSION_INSTANCES.get(chat_mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Chat mission not found")

    mission.chatHistory = request.chatHistory
    save_time = datetime.now()

    return {
        "message": "채팅이 저장되었습니다.",
        "save": {
            "chatHistory": mission.chatHistory,
            "saveAt": save_time
        }
    }


@router.delete("/chat-mission/delete/{chat_mission_id}")
async def delete_chat_mission(chat_mission_id: int):
    # 채팅 미션 삭제
    if chat_mission_id not in CHAT_MISSION_INSTANCES:
        raise HTTPException(status_code=404, detail="Chat mission not found")

    del CHAT_MISSION_INSTANCES[chat_mission_id]

    return {
        "message": "채팅 미션 삭제",
        "delete": chat_mission_id
    }

@router.post("/chat-mission/send/{chat_mission_id}")
async def complete_chat_mission(chat_mission_id: int, request: CompleteChatRequest):
    # 채팅 미션 완료 및 평가 실행
    mission = CHAT_MISSION_INSTANCES.get(chat_mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Chat mission not found")

    template = MISSION_TEMPLATES.get(mission.templateId)
    if not template:
        raise HTTPException(status_code=404, detail="Mission template not found")

    # 평가 실행
    try:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
        parser = JsonOutputParser(pydantic_object=FinalEvaluation)

        eval_prompt = ChatPromptTemplate.from_template(
            template=EVALUATION_PROMPT_TEMPLATE,
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )

        eval_chain = eval_prompt | llm | parser
        history_str = "\n".join([
            f"{msg['role']}: {msg['content']}"
            for msg in request.chatHistory
        ])

        evaluation_result = await eval_chain.ainvoke({
            "mission_title": template.title,
            "mission_description": template.description,
            "evaluation_guideline": template.evaluation_guideline,
            "chat_history": history_str,
        })

        # 미션 상태 업데이트
        mission.status = "completed"
        mission.completedAt = datetime.now()
        mission.evaluation = FinalEvaluation(**evaluation_result)
        mission.chatHistory = request.chatHistory

        return {
            "evaluations": evaluation_result["evaluations"],
            "total_score": evaluation_result["total_score"],
            "grade": evaluation_result["grade"],
            "general_feedback": evaluation_result["general_feedback"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"평가 중 오류가 발생했습니다: {str(e)}")

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
                                
                                ## 항목별 피드백 작성 규칙:
                                각 항목에 대해 반드시 아래 3가지를 모두 포함하세요.
                                
                                1. `good_points`: 해당 항목에서 잘한 점 1~2가지
                                2. `improvement_points`: 아쉬운 점을 **채팅 내용에서 직접 인용**하여 설명
                                3. `suggested_fix`: 인용한 문장을 더 나은 표현으로 수정 제안
                                
                                ## 등급 산정 기준:
                                | 등급 | 점수 범위 |
                                |---|---|
                                | A | 90~100 |
                                | B  | 80~89  |
                                | C | 70~79  |
                                | D  | 60~69  |
                                | E  | 50~59  |
                                | F  | 0~49  |
                                
                                ## 출력 형식 지침:
                                {format_instructions}
                                
                                ## 채팅 내역:
                                {chat_history}
                                """

async def run_chat_session(websocket: WebSocket, template_id: int):
    await websocket.accept()

    template = MISSION_TEMPLATES.get(template_id)
    if not template:
        await websocket.send_text(json.dumps({"error": "Mission template not found"}))
        await websocket.close()
        return

    try:
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
        loader = TextLoader(template.example_conversations_file, encoding="utf-8")
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
        qa_system_prompt = template.ai_persona_prompt + "\n\nContext:\n{context}"
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

                    history_str = "\n".join([
                        f"{('사용자' if msg.type == 'human' else 'AI')}: {msg.content}"
                        for msg in chat_history
                    ])

                    evaluation_result = await eval_chain.ainvoke({
                        "mission_title": template.title,
                        "mission_description": template.description,
                        "evaluation_guideline": template.evaluation_guideline,
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
        print(f"WebSocket Error: {e}")
    finally:
        print(f"Client disconnected")
        if websocket.client_state.name != 'DISCONNECTED':
            await websocket.close()

@router.websocket("/chat/mission/{template_id}")
async def chat_mission_websocket(websocket: WebSocket, template_id: int):
    await run_chat_session(websocket, template_id)