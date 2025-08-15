from fastapi import APIRouter
from models import QueryModel
from memory import load_memory, history_to_db
from agent import create_agent, format_memory_to_string
from utils import save_to_txt, save_to_cache
from datetime import datetime

router = APIRouter()


@router.post("/ask")
async def ask_question(body: QueryModel):
    memory = load_memory(body.user_id)
    agent_executor, parser = create_agent(memory)

    # Format chat history string from memory for prompt input
    chat_history_str = format_memory_to_string(memory)

    raw_response = await agent_executor.ainvoke(
        {"query": body.query, "chat_history": chat_history_str}
    )

    # Default output in case parsing fails
    formatted_output = ""
    try:
        output_text = raw_response.get("output") or raw_response.get("output_text", "")
        try:
            structured_response = parser.parse(output_text)

            formatted_output = structured_response.summary
            if structured_response.symptoms:
                formatted_output += "\n\nCommon symptoms:\n- " + "\n- ".join(
                    structured_response.symptoms
                )
            if structured_response.do:
                formatted_output += "\n\nDo's:\n- " + "\n- ".join(
                    structured_response.do
                )
            if structured_response.dont:
                formatted_output += "\n\nDon'ts:\n- " + "\n- ".join(
                    structured_response.dont
                )
            if structured_response.gp:
                formatted_output += "\n\nWhen to see a GP:\n- " + "\n- ".join(
                    structured_response.gp
                )
            if structured_response.sources:
                formatted_output += "\n\nSources:\n- " + "\n- ".join(
                    structured_response.sources
                )
            if structured_response.assistance:
                formatted_output += (
                    f"\n\n--------------------\n\n{structured_response.assistance}"
                )
        except Exception:
            # fallback if parsing fails
            formatted_output = output_text.strip()

    except Exception as e:
        formatted_output = f"Error parsing response {e}\nRaw response: {raw_response}"

    # Attempt to save to DB, always run regardless of above errors
    try:
        history_to_db(
            body.user_id,
            body.query,
            formatted_output,
            datetime.now(),
            ai_sender_label="ai",
        )
    except Exception as db_err:
        print("Failed to save chat history:", db_err)

    # Optional: still try saving to text/cache but don't block DB insert
    try:
        save_to_txt(formatted_output)
    except Exception as e:
        print("Failed to save to txt:", e)

    try:
        save_to_cache(formatted_output)
    except Exception as e:
        print("Failed to save to cache:", e)

    return {"response": formatted_output}
