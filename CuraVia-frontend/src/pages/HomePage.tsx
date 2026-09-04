import React from "react";
import CuraviaLogo from "../assets/3.png";
import BubbleImage from "../assets/1.png";
import { useNavigate } from "react-router-dom";

const HomePage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div
      className="relative flex min-h-screen flex-col bg-white group/design-root overflow-x-hidden"
      style={{ fontFamily: 'Lexend, "Noto Sans", sans-serif' }}
    >
      <div className="layout-container flex h-full grow flex-col">
        <header className="flex items-center justify-between whitespace-nowrap border-b border-solid border-b-[#f0f3f4] px-4 md:px-10 py-3">
          <div className="flex items-center gap-2 md:gap-4 text-[#111618]">
            <img src={CuraviaLogo} alt="Curavia Logo" className="h-8 w-auto" />
            <h2 className="text-[#111618] text-lg font-bold leading-tight tracking-[-0.015em]">
              Curavia
            </h2>
          </div>
          <div className="flex items-center gap-2 md:gap-8">
            <button
              className="text-[#111618] text-sm font-medium leading-normal"
              onClick={() => navigate("/login")}
            >
              Login
            </button>
            <button
              className="flex min-w-[84px] max-w-[180px] cursor-pointer items-center justify-center overflow-hidden rounded-xl h-8 px-4 bg-[#30bae8] text-[#111618] text-sm font-bold leading-normal tracking-[0.015em]"
              onClick={() => navigate("/signup")}
            >
              <span className="truncate">Sign up</span>
            </button>
          </div>
        </header>
        <div className="px-4 md:px-40 flex flex-1 justify-center py-5">
          <div className="layout-content-container flex flex-col max-w-full md:max-w-[960px] flex-1">
            <div className="flex min-h-[320px] md:min-h-[480px] flex-col gap-6 items-center justify-center p-2 md:p-4">
              <img
                src={BubbleImage}
                alt="Bubble Image"
                className="mb-6 w-60 md:w-80 h-auto"
              />
              <div className="bg-gray-200 rounded-xl shadow-md flex flex-col items-center justify-center p-4 md:p-8 w-full max-w-md md:max-w-xl">
                <h1 className="text-[#111618] text-2xl md:text-4xl font-black leading-tight tracking-[-0.033em] mb-2 text-center">
                  Welcome to Curavia
                </h1>
                <h2 className="text-[#111618] text-xs md:text-sm font-normal leading-normal mb-6 text-center">
                  Your personal AI health assistant. Get instant answers to your
                  health questions and personalized advice.
                </h2>
                <button
                  className="flex min-w-[84px] max-w-[480px] cursor-pointer items-center justify-center overflow-hidden rounded-xl h-10 px-4 bg-[#30bae8] text-[#111618] text-sm font-bold leading-normal tracking-[0.015em]"
                  onClick={() => navigate("/main")}
                >
                  <span className="truncate">Ask a Question</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
