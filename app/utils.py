from langchain_community.tools import DuckDuckGoSearchRun
from langchain.tools import Tool
from datetime import datetime


def save_to_txt(data: str, filename: str = "history.txt"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted_text = ("--- Research Output ---\n" "Timestamp: {}\n\n{}\n\n").format(
        timestamp, data
    )

    with open(filename, "a", encoding="utf-8") as f:
        f.write(formatted_text)

    return "Data successfully saved to {}".format(filename)


def save_to_cache(text: str, filename="latest_response.txt"):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)


save_tool = Tool(
    name="save_text_to_file",
    func=save_to_txt,
    description="Saves structured research data to a text file.",
)

search = DuckDuckGoSearchRun()
search_tool = Tool(
    name="search",
    func=search.run,
    description="Search the web for information.",
)
