from fastapi import FastAPI
from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor
from my_tools import search_tool, save_tool, save_to_txt
import os

# Load environment variables
load_dotenv()

# -------------------------------
# Define Response Model
# -------------------------------
class ResearchResponse(BaseModel):
    summary: str
    symptoms: list[str]
    do: list[str]
    dont: list[str]
    gp: list[str]
    sources: list[str]
    assistance: str

# -------------------------------
# LangChain Setup
# -------------------------------
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
            If user asks questions unrelated to medical diagnosis,reply with "I'm sorry, but I can only assist with medical diagnosis."
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


#--------------------------------
# iteration limiter
#--------------------------------
tools = [search_tool, save_tool]
agent = create_tool_calling_agent(llm=llm, prompt=prompt, tools=tools)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, max_iterations=15)



# -------------------------------
# Chatbot Processing Function
# -------------------------------
async def chatbot_main(query: str) -> str:
    raw_response = await agent_executor.ainvoke({"query": query})

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

# -------------------------------
# FastAPI App
# -------------------------------
app = FastAPI(title="Medical Assistant API", version="1.0")

@app.get("/")
def root():
    return {"message": "Medical assistant API is running"}

class QueryModel(BaseModel):
    query: str

@app.post("/ask")
async def ask_question(body: QueryModel):
    response = await chatbot_main(body.query)
    return {"response": response}
