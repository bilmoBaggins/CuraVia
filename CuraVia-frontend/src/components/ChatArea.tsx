import React from "react";

interface Message {
  sender: "user" | "assistant" | "system";
  text: string;
}

interface ChatAreaProps {
  messages: Message[];
  input: string;
  setInput: (input: string) => void;
  handleSend: () => void;
  isSidebarOpen: boolean;
  setIsSidebarOpen: (open: boolean) => void;
  navigate: (path: string) => void;
  chatName: string;
  isLoading: boolean;
}

const ChatArea: React.FC<ChatAreaProps> = ({
  messages,
  input,
  setInput,
  handleSend,
  isSidebarOpen,
  setIsSidebarOpen,
  navigate,
  chatName,
  isLoading,
}) => {
  const isLoggedIn = Boolean(localStorage.getItem("token"));
  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user_id");
    window.location.reload();
  };
  const messagesEndRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  return (
    <main className="flex-1 flex flex-col bg-white relative">
      <header className="flex justify-between items-center p-4 border-b border-gray-300">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            className="p-2 rounded-lg hover:bg-gray-100"
            aria-label="Toggle sidebar"
            aria-expanded={isSidebarOpen}
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={2}
              stroke="currentColor"
              className="w-6 h-6"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M3.75 6h16.5M3.75 12h16.5M3.75 18h16.5"
              />
            </svg>
          </button>
          {/* Chat name to the right of menu button */}
          <h2 className="font-bold text-lg truncate max-w-xs">{chatName}</h2>
        </div>
        {!isLoggedIn && (
          <div className="space-x-2">
            <button
              onClick={() => navigate("/login")}
              className="bg-blue-500 text-white px-4 py-1 rounded-lg hover:bg-blue-600"
            >
              Login
            </button>
            <button
              onClick={() => navigate("/signup")}
              className="bg-gray-200 px-4 py-1 rounded-lg hover:bg-gray-300"
            >
              Sign Up
            </button>
          </div>
        )}
      </header>
      <div className="flex-1 overflow-y-auto p-4 space-y-3 pb-32">
        {messages.map((msg, index) =>
          msg.sender === "system" ? (
            <div key={index} className="flex justify-center">
              <div className="text-xs text-gray-500 py-2 px-2 text-center">
                {msg.text}
              </div>
            </div>
          ) : (
            <div
              key={index}
              className={`flex ${
                msg.sender === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`px-4 py-2 rounded-lg max-w-xl whitespace-pre-line break-words align-top ${
                  msg.sender === "user"
                    ? "bg-gray-300 text-black"
                    : "bg-blue-500/30 text-black"
                }`}
                style={{
                  display: "inline-block",
                  minHeight: "40px",
                  verticalAlign: "top",
                  whiteSpace: "pre-line",
                }}
              >
                {msg.text}
              </div>
            </div>
          ),
        )}
        {isLoading && (
          <div className="flex justify-start">
            <div
              className="px-4 py-2 rounded-lg max-w-xl align-top bg-blue-500/30 text-black flex items-center"
              style={{ minHeight: "40px" }}
            >
              <svg
                className="animate-spin h-5 w-5 mr-2 text-blue-500"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
                />
              </svg>
              <span>Thinking...</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <div className="p-4 flex items-center gap-2 absolute bottom-0 left-0 right-0 bg-white">
        <div className="flex-1 bg-gray-100 rounded-full flex items-center px-4 py-2">
          <div className="flex-1 flex items-center relative">
            <textarea
              value={input}
              onChange={(e) => {
                let val = e.target.value;
                // Capitalise first letter of every line
                val = val.replace(
                  /(^|\n)([a-zA-Z])/g,
                  (m, p1, p2) => p1 + p2.toUpperCase(),
                );
                // Capitalise first letter after a full stop and space
                val = val.replace(
                  /(\.\s+)([a-zA-Z])/g,
                  (m, p1, p2) => p1 + p2.toUpperCase(),
                );
                setInput(val);
              }}
              onKeyDown={(e) => {
                if (isLoading && e.key === "Enter") {
                  e.preventDefault();
                } else if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
              className="flex-1 bg-transparent outline-none resize-none py-2"
              rows={1}
              style={{
                minHeight: "40px",
                maxHeight: "120px",
                overflowY: "auto",
              }}
            />
            {!input && (
              <span
                className="absolute text-gray-400 pointer-events-none select-none"
                style={{ top: "50%", transform: "translateY(-50%)", left: 0 }}
              >
                Type a message...
              </span>
            )}
          </div>
          <button
            onClick={handleSend}
            disabled={isLoading}
            className={`flex items-center justify-center w-10 h-10 rounded-full 
            ${isLoading ? "bg-gray-400 cursor-not-allowed" : "bg-blue-500 hover:bg-blue-600"}`}
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth="2"
              stroke="white"
              className="w-5 h-5"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M4.5 19.5l15-7.5-15-7.5v6l10 1-10 1v6z"
              />
            </svg>
          </button>
        </div>
      </div>
    </main>
  );
};

export default ChatArea;
