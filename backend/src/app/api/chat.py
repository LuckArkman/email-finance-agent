from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel
from typing import List, Optional
from app.extraction.llm_client import LLMExtractorClient
from app.extraction.prompts import PromptManager
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

router = APIRouter(prefix="/api/v1/chat", tags=["Agent Chat"])

class ChatMessage(BaseModel):
    role: str # 'user' or 'assistant'
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]

class ChatResponse(BaseModel):
    response: str

@router.post("/converse", response_model=ChatResponse)
async def chat_with_agent_brain(request: ChatRequest = Body(...)):
    """
    Direct conversation with the Sustentacódigo Agent Brain (Llama 3).
    Allows users to ask about invoices, status, or general financial advice.
    """
    llm = LLMExtractorClient()
    
    # 1. Prepare messages for Langchain
    # We inject the Brain Persona as the System Message
    system_prompt = PromptManager.build_agent_brain_prompt().messages[0].prompt.template
    
    langchain_messages = [SystemMessage(content=system_prompt)]
    
    for msg in request.messages:
        if msg.role == "user":
            langchain_messages.append(HumanMessage(content=msg.content))
        else:
            langchain_messages.append(AIMessage(content=msg.content))
            
    try:
        # We call the underlying LLM directly for conversation
        # (avoiding the Pydantic parser used for extraction)
        response = await llm.llm.ainvoke(langchain_messages)
        return ChatResponse(response=response.content)
    except Exception as e:
        print(f"Error in Chat Brain: {e}")
        raise HTTPException(status_code=500, detail="O Agente Brain está temporariamente indisponível.")
