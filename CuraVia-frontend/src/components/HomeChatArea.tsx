import React from "react";
import logo from "../assets/1.png";
import backIcon from "../assets/back.png";

interface HomeChatAreaProps {
  isSidebarOpen: boolean;
  setIsSidebarOpen: (open: boolean) => void;
  handleAddChat: () => void;
}

const HomeChatArea: React.FC<HomeChatAreaProps> = ({
  isSidebarOpen,
  setIsSidebarOpen,
  handleAddChat,
}) => {
  const isLoggedIn = Boolean(localStorage.getItem("token"));
  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    window.location.href = "login";
  };
  // handleAddChat is now received as a prop
  return (
    <main className="flex-1 flex flex-col items-center justify-center bg-white relative">
      <header className="flex justify-between items-center p-4 border-b border-gray-300 w-full absolute top-0 left-0">
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
        </div>
        {isLoggedIn ? null : (
          <div className="flex items-center gap-2">
            <button
              onClick={() => (window.location.href = "login")}
              className="bg-blue-500 text-white px-4 py-1 rounded-lg hover:bg-blue-600"
            >
              Login
            </button>
            <button
              onClick={() => (window.location.href = "signup")}
              className="bg-gray-200 px-4 py-1 rounded-lg hover:bg-gray-300"
            >
              Sign Up
            </button>
          </div>
        )}
      </header>
      <div className="flex flex-col items-center justify-center w-full h-full mt-16">
        <img src={logo} alt="Curavia Logo" className="w-32 h-32 mb-6" />
        <h2 className="text-2xl font-bold text-gray-700 mb-2 text-center">
          Welcome to CuraVia
        </h2>
        <p className="text-lg text-gray-500 text-center">
          Press{" "}
          <button
            className="font-bold text-blue-600 hover:text-blue-800 transition"
            onClick={handleAddChat}
          >
            New Chat
          </button>{" "}
          to get started
        </p>
      </div>
    </main>
  );
};

export default HomeChatArea;
