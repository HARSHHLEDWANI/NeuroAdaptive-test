"use client";

import { useSession } from "next-auth/react";
import { useRouter } from "next/navigation";
import { useEffect, useState, useRef, useCallback } from "react";
import {
  Brain,
  Plus,
  Send,
  ArrowLeft,
  X,
  FileText,
  Target,
} from "lucide-react";
import { MarkdownMessage } from "@/components/MarkdownMessage";

type Message = {
  role: "user" | "bot";
  content: string;
};

export default function ChatPage() {
  const { data: session, status } = useSession();
  const router = useRouter();

  const [prompt, setPrompt] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isHistoryLoading, setIsHistoryLoading] = useState(false);
  const [currentSessionId, setCurrentSessionId] = useState<number | null>(null);
  const [pendingFeedback, setPendingFeedback] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const hasSentFeedback = useRef(false);
  // Ref mirror of currentSessionId so async callbacks always read the latest value
  const currentSessionIdRef = useRef<number | null>(null);

  // ─────────────────────────────────────────────────────
  // PHASE 0 FIX: Scroll helper
  // ─────────────────────────────────────────────────────
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading, scrollToBottom]);

  // Keep ref in sync with state so async callbacks always have the latest session ID
  useEffect(() => {
    currentSessionIdRef.current = currentSessionId;
  }, [currentSessionId]);

  // ─────────────────────────────────────────────────────
  // Unified initialization: runs once on mount.
  // Detects quiz_done, restores session ID, sets pending feedback.
  // ─────────────────────────────────────────────────────
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const sidFromUrl = params.get("sessionId");
    const quizDone = params.get("quiz_done") === "true";

    // Prefer URL param (most reliable); fall back to sessionStorage only if no URL param
    const rawId = sidFromUrl ?? (quizDone ? sessionStorage.getItem("chat_session_id") : null);
    const parsedId = rawId ? parseInt(rawId, 10) : NaN;

    // Guard against parseInt("") = NaN or other invalid values
    if (!isNaN(parsedId)) {
      setCurrentSessionId(parsedId);
      currentSessionIdRef.current = parsedId;
    }

    if (quizDone) {
      const resultsRaw = sessionStorage.getItem("last_quiz_results");
      sessionStorage.removeItem("last_quiz_results");

      if (resultsRaw) {
        try {
          const r = JSON.parse(resultsRaw);
          const missed = r.missed_topics?.length
            ? `I struggled with: ${r.missed_topics.join(", ")}.`
            : "I got everything right!";
          const msg =
            `I just completed the quiz **"${r.title}"** and scored **${r.score}/${r.total}**. ` +
            `${missed} Based on my performance, what should I focus on next? ` +
            `Please give me a structured learning plan for improving my weak areas.`;
          setPendingFeedback(msg);
        } catch {
          // silently ignore malformed JSON
        }
      }

      // Clean URL: drop quiz_done param, keep sessionId
      const cleanUrl = !isNaN(parsedId) ? `/chat?sessionId=${parsedId}` : "/chat";
      window.history.replaceState({}, "", cleanUrl);
    }
  }, []);

  // ─────────────────────────────────────────────────────
  // PHASE 0 FIX: Load history when sessionId + session are both ready
  // ─────────────────────────────────────────────────────
  useEffect(() => {
    if (!currentSessionId || !session?.user?.email) return;

    setIsHistoryLoading(true);
    fetch(`/api/chat/history?sessionId=${currentSessionId}`)
      .then((r) => {
        if (!r.ok) throw new Error("Failed to load history");
        return r.json();
      })
      .then((data: Array<{ role: string; content: string }>) => {
        if (Array.isArray(data)) {
          setMessages(
            data.map((m) => ({ role: m.role as "user" | "bot", content: m.content }))
          );
        }
      })
      .catch(console.error)
      .finally(() => setIsHistoryLoading(false));
  }, [currentSessionId, session?.user?.email]);

  // ─────────────────────────────────────────────────────
  // PHASE 0 FIX: handleSubmit with optional message override
  // ─────────────────────────────────────────────────────
  const handleSubmit = useCallback(
    async (overrideMessage?: string) => {
      const userMessage = (overrideMessage ?? prompt).trim();
      if (!userMessage && !selectedFile) return;

      const displayMessage =
        userMessage || (selectedFile ? `Attached file: ${selectedFile.name}` : "");

      setMessages((prev) => [...prev, { role: "user", content: displayMessage }]);
      setIsLoading(true);
      setPrompt("");

      const formData = new FormData();
      formData.append("prompt", userMessage);
      // Read from ref to always get the latest session ID,
      // even if this callback was captured in a stale closure.
      const sid = currentSessionIdRef.current;
      if (sid) {
        formData.append("session_id", sid.toString());
      }
      if (selectedFile) {
        formData.append("file", selectedFile);
        setSelectedFile(null);
      }

      try {
        const response = await fetch("/api/chat", {
          method: "POST",
          body: formData,
        });

        if (response.ok) {
          const data = await response.json();
          setMessages((prev) => [...prev, { role: "bot", content: data.text }]);

          if (data.session_id && data.session_id !== currentSessionIdRef.current) {
            setCurrentSessionId(data.session_id);
            currentSessionIdRef.current = data.session_id;
            window.history.replaceState({}, "", `/chat?sessionId=${data.session_id}`);
            sessionStorage.setItem("chat_session_id", data.session_id.toString());
          }
        } else {
          const errData = await response.json().catch(() => ({}));
          const errMsg = errData.error ?? "Failed to process request.";
          setMessages((prev) => [
            ...prev,
            { role: "bot", content: `**Error:** ${errMsg}` },
          ]);
        }
      } catch (err) {
        console.error(err);
        setMessages((prev) => [
          ...prev,
          { role: "bot", content: "**Error:** Connection lost. Please try again." },
        ]);
      } finally {
        setIsLoading(false);
      }
    },
    [prompt, selectedFile, currentSessionId]
  );

  // ─────────────────────────────────────────────────────
  // PHASE 0 FIX: Auto-send pending feedback after history loads
  // ─────────────────────────────────────────────────────
  useEffect(() => {
    if (
      pendingFeedback &&
      !isHistoryLoading &&
      !hasSentFeedback.current &&
      session?.user?.email
    ) {
      hasSentFeedback.current = true;
      setPendingFeedback(null);
      handleSubmit(pendingFeedback);
    }
  }, [pendingFeedback, isHistoryLoading, session?.user?.email, handleSubmit]);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setSelectedFile(e.target.files[0]);
    }
  };

  // ─────────────────────────────────────────────────────
  // Loading / auth guard
  // ─────────────────────────────────────────────────────
  if (status === "loading") {
    return (
      <div className="h-screen bg-[#F4F1EA] flex flex-col items-center justify-center font-[family-name:var(--font-kodchasan)]">
        <div className="w-16 h-16 bg-[#FF9F1C] border-2 border-black flex items-center justify-center animate-bounce shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
          <Brain className="w-8 h-8 text-black" strokeWidth={2.5} />
        </div>
        <p className="mt-6 text-xl font-bold tracking-widest uppercase animate-pulse">
          Loading Neuro AI...
        </p>
      </div>
    );
  }

  if (!session) return null;

  return (
    // PHASE 0 FIX: h-screen + overflow-hidden so messages area scrolls, not the page
    <div className="h-screen bg-[#F4F1EA] text-black font-[family-name:var(--font-kodchasan)] flex flex-col overflow-hidden">
      {/* ── NAVBAR ─────────────────────────────────────────── */}
      <nav className="w-full bg-white border-b-2 border-black px-6 py-4 flex items-center justify-between flex-shrink-0">
        <div className="flex items-center gap-3">
          <button
            onClick={() => router.push("/dashboard")}
            className="p-2 hover:bg-gray-100 rounded-full border-2 border-transparent hover:border-black transition-all"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div className="w-10 h-10 bg-purple-500 rounded-lg border-2 border-black flex items-center justify-center shadow-[3px_3px_0px_0px_rgba(0,0,0,1)]">
            <Brain className="w-6 h-6 text-white" strokeWidth={2.5} />
          </div>
          <span className="text-xl font-bold tracking-tight hidden md:block">
            Neuro Chat
          </span>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-3 bg-yellow-100 px-3 py-1.5 rounded-lg border-2 border-black">
            {session.user?.image ? (
              <img
                src={session.user.image}
                alt="Profile"
                className="w-8 h-8 rounded-full border border-black"
              />
            ) : (
              <div className="w-8 h-8 bg-gray-300 rounded-full border border-black flex items-center justify-center">
                <div className="w-4 h-4 bg-gray-400 rounded-full" />
              </div>
            )}
            <span className="font-bold text-sm hidden md:block">
              {session.user?.name?.split(" ")[0]}
            </span>
          </div>
        </div>
      </nav>

      {/* ── CHAT AREA ──────────────────────────────────────── */}
      {/* PHASE 0 FIX: flex-1 + overflow-y-auto makes this area scroll independently */}
      <main className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto w-full px-4 md:px-6 py-6">
          {/* Empty state */}
          {messages.length === 0 && !isHistoryLoading && (
            <div className="flex flex-col items-center justify-center h-full min-h-[50vh] text-center">
              <div className="bg-white border-2 border-black p-8 rounded-2xl shadow-[8px_8px_0px_0px_rgba(0,0,0,1)] max-w-md">
                <Brain className="w-16 h-16 text-purple-600 mx-auto mb-4" />
                <h2 className="text-2xl font-bold mb-2">New Session</h2>
                <p className="text-gray-600 text-sm">
                  Ask a question, attach a file, or request a quiz on any topic.
                </p>
              </div>
            </div>
          )}

          {/* History loading */}
          {isHistoryLoading && (
            <div className="flex items-center justify-center py-12">
              <div className="flex items-center gap-3 bg-white border-2 border-black px-5 py-3 rounded-xl shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]">
                <div className="w-2 h-2 rounded-full bg-purple-500 animate-bounce" />
                <div
                  className="w-2 h-2 rounded-full bg-purple-500 animate-bounce"
                  style={{ animationDelay: "150ms" }}
                />
                <div
                  className="w-2 h-2 rounded-full bg-purple-500 animate-bounce"
                  style={{ animationDelay: "300ms" }}
                />
                <span className="text-sm font-semibold text-gray-500">Loading history...</span>
              </div>
            </div>
          )}

          {/* Messages */}
          {messages.length > 0 && (
            <div className="flex flex-col gap-6">
              {messages.map((msg, index) => {
                // PHASE 0 FIX: strip <quiz> tags from display, preserve rest
                const quizMatch = msg.content.match(/<quiz>([\s\S]*?)<\/quiz>/);
                const cleanContent = msg.content
                  .replace(/<quiz>[\s\S]*?<\/quiz>/, "")
                  .trim();
                const hasQuiz = msg.role === "bot" && quizMatch?.[1];

                return (
                  <div
                    key={index}
                    className={`flex flex-col ${msg.role === "user" ? "items-end" : "items-start"}`}
                  >
                    <div
                      className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"} w-full`}
                    >
                      {msg.role === "bot" && (
                        <div className="w-8 h-8 mr-3 mt-1 bg-purple-500 rounded-lg border-2 border-black flex-shrink-0 flex items-center justify-center shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]">
                          <Brain className="w-5 h-5 text-white" />
                        </div>
                      )}

                      <div
                        className={`max-w-[82%] p-4 rounded-xl border-2 border-black shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] ${
                          msg.role === "user"
                            ? "bg-purple-100 rounded-br-none"
                            : "bg-white rounded-bl-none"
                        }`}
                      >
                        {msg.role === "bot" ? (
                          /* PHASE 0 FIX: Render markdown for bot messages */
                          <MarkdownMessage
                            content={
                              cleanContent ||
                              (hasQuiz
                                ? "I've prepared an assessment for you. Click below when ready."
                                : "...")
                            }
                          />
                        ) : (
                          <p className="text-sm md:text-base whitespace-pre-wrap">
                            {msg.content}
                          </p>
                        )}
                      </div>
                    </div>

                    {/* Quiz CTA button */}
                    {hasQuiz && (
                      <div className="ml-11 mt-3">
                        <button
                          onClick={() => {
                            try {
                              const quizData = JSON.parse(quizMatch![1]);
                              // PHASE 0 FIX: Save session ID before navigating to quiz
                              sessionStorage.setItem(
                                "current_quiz",
                                JSON.stringify(quizData)
                              );
                              sessionStorage.setItem(
                                "chat_session_id",
                                currentSessionId?.toString() ?? ""
                              );
                              router.push("/quiz");
                            } catch (e) {
                              console.error("Failed to parse quiz JSON", e);
                            }
                          }}
                          className="bg-[#FF9F1C] hover:bg-[#ff8c00] border-2 border-black px-6 py-2.5 rounded-lg font-bold shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] transition-all active:translate-x-1 active:translate-y-1 active:shadow-none flex items-center gap-2 text-sm"
                        >
                          <Target className="w-4 h-4" />
                          Start Assessment
                        </button>
                      </div>
                    )}
                  </div>
                );
              })}

              {/* Typing indicator */}
              {isLoading && (
                <div className="flex justify-start">
                  <div className="w-8 h-8 mr-3 mt-1 bg-purple-500 rounded-lg border-2 border-black flex-shrink-0 flex items-center justify-center shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]">
                    <Brain className="w-5 h-5 text-white" />
                  </div>
                  <div className="p-4 rounded-xl border-2 border-black bg-white rounded-bl-none shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-purple-400 animate-bounce" />
                    <div
                      className="w-2 h-2 rounded-full bg-purple-400 animate-bounce"
                      style={{ animationDelay: "150ms" }}
                    />
                    <div
                      className="w-2 h-2 rounded-full bg-purple-400 animate-bounce"
                      style={{ animationDelay: "300ms" }}
                    />
                  </div>
                </div>
              )}

              {/* PHASE 0 FIX: Scroll anchor at bottom of messages */}
              <div ref={messagesEndRef} className="h-2" />
            </div>
          )}
        </div>
      </main>

      {/* ── CHAT INPUT ─────────────────────────────────────── */}
      <div className="flex-shrink-0 w-full bg-[#F4F1EA] border-t-2 border-black px-4 py-4">
        <div className="max-w-3xl mx-auto">
          {/* File attachment pill */}
          {selectedFile && (
            <div className="mb-3 flex items-center gap-2 bg-purple-100 border-2 border-purple-300 w-max px-3 py-1.5 rounded-lg shadow-[2px_2px_0px_0px_rgba(0,0,0,1)]">
              <FileText className="w-4 h-4 text-purple-600" />
              <span className="text-sm font-medium truncate max-w-[200px]">
                {selectedFile.name}
              </span>
              <button
                onClick={() => {
                  setSelectedFile(null);
                  if (fileInputRef.current) fileInputRef.current.value = "";
                }}
                className="p-1 hover:bg-purple-200 rounded-full ml-1 text-gray-500 hover:text-black transition-colors"
              >
                <X className="w-3 h-3" strokeWidth={3} />
              </button>
            </div>
          )}

          <div className="flex items-center bg-white border-2 border-black rounded-full shadow-[4px_4px_0px_0px_rgba(0,0,0,1)] px-4 py-2">
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileSelect}
              className="hidden"
              accept=".pdf,.txt,.md,.csv"
            />

            <button
              onClick={() => fileInputRef.current?.click()}
              className="p-2 hover:bg-gray-100 rounded-full transition-colors flex-shrink-0"
              title="Attach file"
            >
              <Plus className="w-5 h-5" />
            </button>

            <input
              type="text"
              placeholder="Ask anything or attach a file..."
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleSubmit();
                }
              }}
              disabled={isLoading}
              className="flex-1 outline-none px-3 py-2 bg-transparent text-sm md:text-base disabled:opacity-50"
            />

            <button
              onClick={() => handleSubmit()}
              disabled={isLoading || (!prompt.trim() && !selectedFile)}
              className="p-2 bg-black text-white rounded-full hover:bg-gray-800 transition-colors disabled:opacity-40 disabled:cursor-not-allowed flex-shrink-0"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
