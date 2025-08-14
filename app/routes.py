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

            save_to_txt(formatted_output)
            save_to_cache(formatted_output)
            history_to_db(body.user_id, body.query, formatted_output, datetime.now())
            return {"response": formatted_output}

        except Exception:
            return output_text.strip()

    except Exception as e:
        return {"response": f"Error parsing response {e}\nRaw response: {raw_response}"}
