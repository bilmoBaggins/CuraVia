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
            "You are a chatbot designed to assist with medical diagnosis "
            "based on user description. Sound more human-like to make users "
            "more comfortable using you. If user types in another language, "
            "respond in the given format, in the same language. Use the link "
            "to the NHS website for accurate information: https://www.nhs.uk. "
            "If the user greets you (e.g. says 'hi', 'hello', 'hey', "
            "'good morning', 'good afternoon', 'good evening'), reply with a "
            "friendly greeting and offer your assistance. Give a list of "
            "symptoms that match the user's query, matched to the illness they "
            "might have. Provide a list of possible illnesses based on the "
            "symptoms. Provide a list of possible treatments based on the "
            "symptoms and illnesses. Give some Do's and Don'ts for the user to "
            "follow. Tell the user if and when to see a GP or doctor. If user "
            "symptoms are extreme, tell them 'Your symptoms are quite severe, "
            "I suggest you call 999 immediately.' in your own words. Always "
            "ask an appropriate question related to the conversation. If user "
            "corrects you in any way, acknowledge the correction, apologise "
            "and adjust your response accordingly to encourage further "
            "discussion. Provide a concise 4-5 word title for the conversation "
            "in a 'title' field. Provide no other text. {format_instructions}",
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
        role = "user" if msg.type == "human" else "assistant"
        history_str += f"{role}: {msg.content}\n"
    return history_str.strip()
