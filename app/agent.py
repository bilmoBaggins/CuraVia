from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor
from models import ResearchResponse
from utils import search_tool, save_tool

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini")
parser = PydanticOutputParser(pydantic_object=ResearchResponse)

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            (
                "You are a chatbot designed to assist with medical diagnosis based on "
                "user description. Use the link to the NHS website for accurate "
                "information: https://www.nhs.uk. Give a list of symptoms that match "
                "the user's query, matched to the illness they might have. Give some "
                "Do's and Don'ts for the user to follow. Tell the user if and when to "
                "see a GP or doctor. If user asks questions unrelated to medical "
                "diagnosis, reply with \"I'm sorry, but I can only assist with medical "
                'diagnosis.", but if user query is following on from a response you '
                "previously gave, provide a helpful response. If user symptoms are "
                'extreme, tell them "Your symptoms are quite severe, I suggest you '
                'call 999 immediately." Always ask '
                "an appropriate question related to the conversation "
                "to encourage further discussion. Provide no other text."
                "{format_instructions}"
            ),
        ),
        ("human", "Conversation history:\n{chat_history}"),
        ("human", "{query}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
).partial(format_instructions=parser.get_format_instructions())

tools = [search_tool, save_tool]


def create_agent(memory):
    agent = create_tool_calling_agent(llm=llm, prompt=prompt, tools=tools)
    agent_executor = AgentExecutor(
        agent=agent, tools=tools, verbose=True, memory=memory, max_iterations=15
    )
    return agent_executor, parser


def format_memory_to_string(memory) -> str:
    messages = memory.load_memory_variables({}).get("chat_history", [])
    # messages are BaseMessage objects (human or ai)
    history_str = ""
    for msg in messages:
        role = "User" if msg.type == "human" else "Assistant"
        history_str += f"{role}: {msg.content}\n"
    return history_str.strip()
