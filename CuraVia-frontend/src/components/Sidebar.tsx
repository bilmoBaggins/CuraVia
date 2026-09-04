import React, { useRef, useEffect } from "react";
import CuraviaLogo from "../assets/3.png";

export interface Chat {
  id: number;
  name: string;
  convo_id: number;
}

interface SidebarProps {
  chats: Chat[];
  editingChatId: number | null;
  isSidebarOpen: boolean;
  accountMenuOpen: boolean;
  username: string;
  profileImage?: string;
  setIsSidebarOpen: (open: boolean) => void;
  setEditingChatId: (id: number | null) => void;
  setAccountMenuOpen: (open: boolean) => void;
  handleAddChat: () => void;
  handleRenameChat: (id: number, name: string) => void;
  handleDeleteChat: (id: number) => void;
  navigate: (path: string) => void;
  selectedConvoId: number | null;
  setSelectedConvoId: (id: number | null) => void;
}

const Sidebar: React.FC<SidebarProps> = ({
  chats,
  editingChatId,
  isSidebarOpen,
  accountMenuOpen,
  username,
  profileImage,
  setIsSidebarOpen,
  setEditingChatId,
  setAccountMenuOpen,
  handleAddChat,
  handleRenameChat,
  handleDeleteChat,
  navigate,
  selectedConvoId,
  setSelectedConvoId,
}) => {
  const accountMenuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        accountMenuRef.current &&
        !accountMenuRef.current.contains(event.target as Node)
      ) {
        setAccountMenuOpen(false);
      }
    }
    if (accountMenuOpen) {
      document.addEventListener("mousedown", handleClickOutside);
    }
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, [accountMenuOpen, setAccountMenuOpen]);

  return (
    <>
      {/* Overlay for mobile sidebar */}
      {isSidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-30 z-30 md:hidden"
          onClick={() => setIsSidebarOpen(false)}
          aria-hidden="true"
        />
      )}
      {isSidebarOpen && (
        <aside
          className={[
            "bg-gray-200 flex flex-col justify-between z-40 overflow-hidden",
            "fixed inset-y-0 left-0 w-64 transform transition-transform duration-200",
            isSidebarOpen ? "translate-x-0" : "-translate-x-full",
            "md:static md:inset-auto md:transform-none md:transition-[width] md:duration-200",
            isSidebarOpen
              ? "md:w-64 md:border-r md:border-gray-300 md:pointer-events-auto"
              : "md:w-0 md:border-0 md:pointer-events-none",
          ].join(" ")}
          aria-hidden={!isSidebarOpen}
        >
          <div>
            <div className="flex items-center gap-2 p-4 border-b border-gray-300">
              <img
                src={CuraviaLogo}
                alt="Curavia Logo"
                className="h-8 w-auto"
              />
              <h1 className="font-bold text-lg">CuraVia</h1>
            </div>
            <button
              onClick={() => setSelectedConvoId(null)}
              className={`w-full text-left px-3 py-2 hover:bg-gray-400 ${selectedConvoId === null ? "bg-blue-200" : "bg-gray-300"}`}
              style={
                selectedConvoId === null ? {} : { backgroundColor: "#e2e8f0" }
              }
            >
              🏠︎ Home
            </button>
            <button
              onClick={handleAddChat}
              className={`w-full text-left px-3 py-2 hover:bg-gray-400 ${chats.length === 0 && selectedConvoId === null ? "bg-blue-200" : "bg-gray-300"}`}
            >
              ＋ New Chat
            </button>
            <div className="mt-2">
              {chats.map((chat: Chat) => (
                <div
                  key={chat.id}
                  className={`group flex items-center justify-between px-3 py-2 rounded-lg hover:bg-gray-300 cursor-pointer ${selectedConvoId === chat.convo_id ? "bg-blue-200" : ""}`}
                  onClick={() => setSelectedConvoId(chat.convo_id)}
                >
                  {editingChatId === chat.id ? (
                    <input
                      autoFocus
                      defaultValue={chat.name}
                      onBlur={(e) =>
                        handleRenameChat(chat.id, e.target.value || chat.name)
                      }
                      className="bg-transparent border-b border-gray-400 outline-none flex-1 mr-2"
                    />
                  ) : (
                    <span
                      onDoubleClick={() => setEditingChatId(chat.id)}
                      className="flex-1"
                    >
                      {chat.name}
                    </span>
                  )}
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeleteChat(chat.id);
                    }}
                    className="text-red-500 hover:text-red-700 ml-2 opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    ✕
                  </button>
                </div>
              ))}
            </div>
          </div>
          <div className="p-4 relative">
            <button
              onClick={() => setAccountMenuOpen(!accountMenuOpen)}
              className="w-full flex items-center justify-start gap-3 bg-gray-300/70 text-black rounded-full py-2 px-3 hover:bg-gray-400/70 transition"
            >
              {profileImage ? (
                <img
                  src={profileImage}
                  alt="Profile"
                  className="w-6 h-6 rounded-full object-cover"
                />
              ) : (
                <div className="w-8 h-8 rounded-full bg-[#0D80F2] flex items-center justify-center text-white font-bold">
                  {username
                    .split(" ")
                    .map((n: string) => n[0])
                    .join("")
                    .toUpperCase()}
                </div>
              )}
              <span>{username}</span>
            </button>
            {accountMenuOpen && (
              <div
                ref={accountMenuRef}
                className="absolute bottom-14 left-4 bg-white/90 backdrop-blur rounded-lg shadow-lg w-40 py-2"
              >
                <button
                  onClick={() => alert("Settings")}
                  className="block w-full text-left px-4 py-2 hover:bg-gray-200"
                >
                  Settings
                </button>
                <button
                  onClick={() => {
                    localStorage.removeItem("token"); // Clear JWT token
                    localStorage.removeItem("user"); // Clear user data
                    navigate("/login"); // Redirect to login
                  }}
                  className="block w-full text-left px-4 py-2 hover:bg-gray-200"
                >
                  Sign Out
                </button>
              </div>
            )}
          </div>
        </aside>
      )}
    </>
  );
};

export default Sidebar;
