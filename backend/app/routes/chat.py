from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.utils.database import get_db
from app.models.conversation import Conversation
from app.schemas.chat import ChatRequest, ChatResponse

from app.services.nlu.intent_classifier import nlu_classifier
from app.services.search.semantic_search import search_engine
from app.services.llm.generator import llm_engine

router = APIRouter(prefix="/api/chat", tags=["Chat & Conversations"])

@router.post("/ask", response_model=ChatResponse)
def ask_assistant(request: ChatRequest, db: Session = Depends(get_db)):
    try:
        # 1. NEW MEMORY FEATURE: Fetch the last 3 messages from this session
        past_chats = db.query(Conversation).filter(
            Conversation.session_id == request.session_id
        ).order_by(Conversation.created_at.desc()).limit(3).all()
        
        # Reverse them so they are in chronological order (oldest to newest)
        past_chats.reverse()

        # Format history for the AI
        chat_history = []
        for chat in past_chats:
            chat_history.append({"user": chat.query_text, "assistant": chat.response_text})

        # 2. NLU: Classify Intent
        intent, confidence = nlu_classifier.classify(request.query_text)

        # 3. RETRIEVAL: Search Vector DB
        search_results = search_engine.search(request.query_text, top_k=5)

        # 4. GENERATION: Pass Query + Facts + HISTORY to the AI!
        ai_response = llm_engine.generate_response(
            query=request.query_text, 
            context_list=search_results,
            history=chat_history  # <--- WE ADDED MEMORY HERE!
        )

        # 5. DATABASE: Save the new interaction
        new_conversation = Conversation(
            user_id=request.user_id,
            session_id=request.session_id,
            query_text=request.query_text,
            response_text=ai_response,
            context_vector={"detected_intent": intent, "confidence": confidence} 
        )
        
        db.add(new_conversation)
        db.commit()
        db.refresh(new_conversation)
        
        return new_conversation

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))