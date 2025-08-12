from fastapi import FastAPI
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.memory import ConversationBufferMemory
from my_tools import search_tool, save_tool, save_to_txt
import os
import pickle

# Load environment variables
load_dotenv()

# Response model
class ResearchResponse(BaseModel):
    summary: str
    symptoms: list[str]
    do: list[str]
    dont: list[str]
    gp: list[str]
    sources: list[str]
    assistance: str

# LLM and parser setup
llm = ChatOpenAI(model="gpt-4o-mini")
parser = PydanticOutputParser(pydantic_object=ResearchResponse)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are a chatbot designed to assist with medical diagnosis based on user description.
            Use the link to the NHS website for accurate information: https://www.nhs.uk
            Give a list of symptoms that match the user's query, matched to the illness they might have.
            Give some Do's and Don'ts for the user to follow.
            Tell the user if and when to see a GP or doctor.
            Offer extra assistance or guidance that you can give related to user's query if needed.
            Provide no other text.
            {format_instructions}
            """,
        ),
        ("placeholder", "{chat_history}"),
        ("human", "{query}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
).partial(format_instructions=parser.get_format_instructions())

# Tools
tools = [search_tool, save_tool]

# Multi-user memory store
MEMORY_DIR = "user_memories"
os.makedirs(MEMORY_DIR, exist_ok=True)

def load_memory(user_id: str) -> ConversationBufferMemory:
    filepath = os.path.join(MEMORY_DIR, f"{user_id}.pkl")
    if os.path.exists(filepath):
        with open(filepath, "rb") as f:
            return pickle.load(f)
    return ConversationBufferMemory(memory_key="chat_history", return_messages=True)

def save_memory(user_id: str, memory: ConversationBufferMemory):
    filepath = os.path.join(MEMORY_DIR, f"{user_id}.pkl")
    with open(filepath, "wb") as f:
        pickle.dump(memory, f)

# Chatbot function
async def chatbot_main(query: str, user_id: str) -> str:
    memory = load_memory(user_id)
    agent = create_tool_calling_agent(llm=llm, prompt=prompt, tools=tools)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, memory=memory)

    raw_response = await agent_executor.ainvoke({"query": query})
    save_memory(user_id, memory)

    try:
        structured_response = parser.parse(raw_response.get("output"))
        formatted_output = structured_response.summary

        if structured_response.symptoms:
            formatted_output += f"\n\nCommon symptoms:\n- " + "\n- ".join(structured_response.symptoms)
        if structured_response.do:
            formatted_output += f"\n\nDo's:\n- " + "\n- ".join(structured_response.do)
        if structured_response.dont:
            formatted_output += f"\n\nDon'ts:\n- " + "\n- ".join(structured_response.dont)
        if structured_response.gp:
            formatted_output += f"\n\nWhen to see a GP:\n- " + "\n- ".join(structured_response.gp)
        if structured_response.sources:
            formatted_output += f"\n\nSources:\n- " + "\n- ".join(structured_response.sources)
        if structured_response.assistance:
            formatted_output += f"\n\n--------------------\n\n{structured_response.assistance}"

        save_to_txt(formatted_output)
        return formatted_output
    except Exception as e:
        return f"Error parsing response {e}\nRaw response: {raw_response}"

# FastAPI app
app = FastAPI(title="CuraVia", version="1.0")

@app.get("/")
def root():
    return {"message": "CuraVia is running"}

class QueryModel(BaseModel):
    query: str
    user_id: str

@app.post("/ask")
async def ask_question(body: QueryModel):
    response = await chatbot_main(body.query, body.user_id)
    return {"response": response}
