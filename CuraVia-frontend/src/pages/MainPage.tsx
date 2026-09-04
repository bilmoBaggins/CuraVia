import React, { useEffect, useState } from "react";
import backIcon from "../assets/back.png";
// ...existing code...
import api from "../api";
import { useNavigate } from "react-router-dom";
import Sidebar, { Chat } from "../components/Sidebar";
import ChatArea from "../components/ChatArea";
import HomeChatArea from "../components/HomeChatArea";

const MainPage: React.FC = () => {
  const navigate = useNavigate();
  const [chats, setChats] = useState<Chat[]>([]);
  const [editingChatId, setEditingChatId] = useState<number | null>(null);
  const [selectedConvoId, setSelectedConvoId] = useState<number | null>(null);
  const [messages, setMessages] = useState<
    { sender: "user" | "assistant" | "system"; text: string; _id?: number }[]
  >([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [accountMenuOpen, setAccountMenuOpen] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  useEffect(() => {
    const mq = window.matchMedia("(min-width: 768px)");
    const apply = () => setIsSidebarOpen(mq.matches);
    apply();
    if (mq.addEventListener) {
      mq.addEventListener("change", apply);
      return () => mq.removeEventListener("change", apply);
    } else {
      // Safari fallback
      // @ts-ignore
      mq.addListener(apply);
      // @ts-ignore
      return () => mq.removeListener(apply);
    }
  }, []);

  // Fetch all conversations for sidebar on mount
  useEffect(() => {
    const token = localStorage.getItem("token");
    const userObj = localStorage.getItem("user");
    let userId = 0;
    let closedChats: number[] = [];
    if (token && userObj) {
      try {
        const parsed = JSON.parse(userObj);
        if (parsed && parsed.user_id) {
          userId = Number(parsed.user_id);
        }
      } catch {}
      api.get(`/users/${userId}/closed_chats`).then((closedRes) => {
        if (Array.isArray(closedRes.data)) {
          closedChats = closedRes.data;
        }

        api.get(`/conversations?user_id=${userId}`).then((res) => {
          console.log("Fetched conversations:", res.data);
          if (Array.isArray(res.data)) {
            // Filter out closedChats
            setChats(
              res.data
                .filter((c: any) => !closedChats.includes(c.id))
                .map((c: any, idx: number) => ({
                  id: idx + 1,
                  name: c.title,
                  convo_id: c.id,
                })),
            );
            // Select first available chat if any
            const openConvos = res.data.filter(
              (c: any) => !closedChats.includes(c.id),
            );
            if (openConvos.length > 0) {
              setSelectedConvoId(null);
            }
          }
        });
      });
    }
  }, []);

  // Fetch messages for selected conversation
  useEffect(() => {
    if (!selectedConvoId) return;
    const userObj = localStorage.getItem("user");
    let userId = 0;
    if (userObj) {
      try {
        const parsed = JSON.parse(userObj);
        if (parsed && parsed.user_id) {
          userId = Number(parsed.user_id);
        }
      } catch {}
    }
    api
      .get(`/messages?conversation_id=${selectedConvoId}&user_id=${userId}`)
      .then((res) => {
        if (Array.isArray(res.data)) {
          const msgs = res.data.map((msg: any) => ({
            sender: msg.sender,
            text: msg.text,
          }));
          setMessages(msgs);
        }
      });
  }, [selectedConvoId]);

  const storedUser = localStorage.getItem("user");
  let displayName = "Guest";

  if (storedUser) {
    try {
      const user = JSON.parse(storedUser);
      if (user.first_name && user.last_name) {
        displayName = `${user.first_name ?? ""} ${user.last_name ?? ""}`.trim();
      } else {
        displayName = user.username;
      }
    } catch (error) {
      console.error("Error parsing user data:", error);
    }
  }

  const username = displayName;
  const profileImage = "";

  const handleAddChat = async () => {
    const token = localStorage.getItem("token");
    const userObj = localStorage.getItem("user");
    let userId = 0;
    if (token && userObj) {
      try {
        const parsed = JSON.parse(userObj);
        if (parsed && parsed.user_id) {
          userId = Number(parsed.user_id);
        }
      } catch {}
    }

    // Guests (no token) can only have one chat
    if (!token && chats.length > 0) {
      const msgObj = {
        sender: "system" as const,
        text: "Please sign up to create multiple chats.",
        _id: Date.now() + Math.random(),
      };
      setMessages((prev) => [...prev, msgObj]);
      setTimeout(() => {
        setMessages((prev) => prev.filter((m) => m._id !== msgObj._id));
      }, 5000);
      return;
    }

    // For signed up/logged in users, allow multiple chats
    const title = `Chat ${chats.length + 1}`;
    try {
      const res = await api.post("/conversations", {
        user_id: userId,
        title,
      });
      // Use returned convo_id to append new chat to list
      if (res && res.data && res.data.message) {
        // Extract convo_id from message string
        const match = res.data.message.match(/ID: (\d+)/);
        const convo_id = match ? Number(match[1]) : chats.length + 1;
        setChats((prev) => [
          { id: prev.length + 1, name: title, convo_id },
          ...prev,
        ]);
        setSelectedConvoId(convo_id);
      } else {
        // Fallback for guests if backend does not return id
        setChats((prev) => {
          if (!prev || prev.length > 0) return prev || [];
          return [{ id: 1, name: title, convo_id: 1 }];
        });
        setSelectedConvoId(1);
      }
    } catch {
      // Fallback for guests if request fails
      setChats([{ id: 1, name: title, convo_id: 1 }]);
      setSelectedConvoId(1);
    }
  };

  const handleRenameChat = (id: number, newName: string) => {
    setChats(
      chats.map((chat) => (chat.id === id ? { ...chat, name: newName } : chat)),
    );
    setEditingChatId(null);
    // Update backend conversation title immediately
    const chat = chats.find((c) => c.id === id);
    if (chat) {
      const token = localStorage.getItem("token");
      const userObj = localStorage.getItem("user");
      let userId = 0;
      if (token && userObj) {
        try {
          const parsed = JSON.parse(userObj);
          if (parsed && parsed.user_id) {
            userId = Number(parsed.user_id);
          }
        } catch {}
      }
      if (userId) {
        api.patch(`/conversations/${chat.convo_id}`, { title: newName });
      }
    }
  };

  const handleDeleteChat = (id: number) => {
    // Only remove chat from UI, do not delete from backend
    const chat = chats.find((c) => c.id === id);
    setChats(chats.filter((chat) => chat.id !== id));
    // Persist closed chat convo_id in backend for logged-in users
    if (chat) {
      const userObj = localStorage.getItem("user");
      let userId = 0;
      if (userObj) {
        try {
          const parsed = JSON.parse(userObj);
          if (parsed && parsed.user_id) {
            userId = Number(parsed.user_id);
          }
        } catch {}
      }
      if (userId) {
        // Update closedChats in backend
        api.post(`/users/${userId}/closed_chats`, { convo_id: chat.convo_id });
      }
    }
    setSelectedConvoId(null);
  };

  const handleSend = async () => {
    if ((!input.trim() || !selectedConvoId) && !isLoading) return;
    const userMessage = input;
    setInput("");
    let userId = 0;
    const userObj = localStorage.getItem("user");
    if (userObj) {
      try {
        const parsed = JSON.parse(userObj);
        if (parsed && parsed.user_id) {
          userId = Number(parsed.user_id);
        }
      } catch {}
    }
    // Optimistically add user message immediately
    setMessages((prev) => [...prev, { sender: "user", text: userMessage }]);
    setIsLoading(true);

    try {
      let prompt = userMessage;
      const response = await api.post("/ask", {
        user_id: userId,
        query: prompt,
        convo_id: selectedConvoId,
      });
      const botText = response.data?.message || "No response from bot.";
      setMessages((prev) => {
        const newMsgs = [
          ...prev,
          { sender: "assistant" as const, text: botText },
        ];
        const token = localStorage.getItem("token");
        if (!token) {
          const sysMsg = {
            sender: "system" as const,
            text: "Please sign up to access features such as follow up questions and chat history.",
            _id: Date.now() + Math.random(),
          };
          setTimeout(() => {
            setMessages((prev2) => prev2.filter((m) => m._id !== sysMsg._id));
          }, 5000);
          setIsLoading(false);
          return [...newMsgs, sysMsg];
        }
        setIsLoading(false);
        return newMsgs;
      });
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        { sender: "assistant", text: "Error: Could not reach chatbot." },
      ]);
      setIsLoading(false);
    }
  };

  const isLoggedIn = Boolean(localStorage.getItem("token"));
  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("user");
    navigate("/login");
  };
  return (
    <div className="flex h-screen relative">
      <Sidebar
        chats={chats}
        editingChatId={editingChatId}
        isSidebarOpen={isSidebarOpen}
        accountMenuOpen={accountMenuOpen}
        username={username}
        profileImage={profileImage}
        setIsSidebarOpen={setIsSidebarOpen}
        setEditingChatId={setEditingChatId}
        setAccountMenuOpen={setAccountMenuOpen}
        handleAddChat={handleAddChat}
        handleRenameChat={handleRenameChat}
        handleDeleteChat={handleDeleteChat}
        navigate={navigate}
        selectedConvoId={selectedConvoId}
        setSelectedConvoId={setSelectedConvoId}
      />
      {selectedConvoId === null ? (
        <HomeChatArea
          isSidebarOpen={isSidebarOpen}
          setIsSidebarOpen={setIsSidebarOpen}
          handleAddChat={handleAddChat}
        />
      ) : (
        <ChatArea
          messages={messages}
          input={input}
          setInput={setInput}
          handleSend={handleSend}
          isSidebarOpen={isSidebarOpen}
          setIsSidebarOpen={setIsSidebarOpen}
          navigate={navigate}
          chatName={(() => {
            const chat = chats.find((c) => c.convo_id === selectedConvoId);
            return chat ? chat.name : "";
          })()}
          isLoading={isLoading}
        />
      )}
      {isLoggedIn && (
        <button
          onClick={handleLogout}
          className="absolute top-4 right-0 mr-4 p-2 rounded-full hover:bg-gray-200"
          title="Logout"
        >
          <img src={backIcon} alt="Back" className="w-5 h-5 object-contain" />
        </button>
      )}
    </div>
  );
};

export default MainPage;
