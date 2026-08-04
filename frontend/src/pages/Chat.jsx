/**
 * Legal Compass — Chat Page
 * Main interface: Navbar + Sidebar history + Chat messages + Input
 *
 * State:
 *   messages     — current in-session exchanges
 *   history      — DB history shown in sidebar
 *   input        — textarea value
 *   loading      — AI is generating
 *   histLoading  — sidebar is fetching
 *   apiOnline    — FastAPI reachable through Node backend
 *   activeHistId — selected sidebar item
 */
import { useState, useEffect, useRef, useCallback } from 'react';
import api from '../services/api';
import Navbar    from '../components/Navbar';
import Sidebar   from '../components/Sidebar';
import ChatBubble from '../components/ChatBubble';

// Quick-start suggestions shown on the empty state
const SUGGESTIONS = [
  'What is Article 21?',
  'How do I file an FIR?',
  'What is anticipatory bail?',
  'Punishment for murder (IPC 302)',
  'What are my rights as a tenant?',
  'What is Section 498A IPC?',
];

const WELCOME = {
  id:       'welcome',
  type:     'bot',
  message:  '**Welcome to Legal Compass AI! ⚖️**\n\nI\'m your AI-powered assistant for Indian law — fine-tuned on Constitutional law, IPC, and CrPC.\n\nAsk me anything in plain language:\n- **Constitutional Rights** — Articles 14, 19, 21, 32…\n- **IPC** — Sections 302, 376, 420, 498A…\n- **CrPC** — FIR, bail, arrest, anticipatory bail…\n- **General Law** — Contracts, property, consumer rights…',
  category: null,
  sources:  [],
};

export default function Chat() {
  const [messages,    setMessages]    = useState([WELCOME]);
  const [history,     setHistory]     = useState([]);
  const [input,       setInput]       = useState('');
  const [loading,     setLoading]     = useState(false);
  const [histLoading, setHistLoading] = useState(false);
  const [histPage,    setHistPage]    = useState(1);
  const [histHasMore, setHistHasMore] = useState(false);
  const [apiOnline,   setApiOnline]   = useState(false);
  const [activeHistId,setActiveHistId]= useState(null);

  const messagesEndRef = useRef(null);
  const inputRef       = useRef(null);

  // ── Scroll to bottom ────────────────────────────────────────
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };
  useEffect(scrollToBottom, [messages, loading]);

  // ── Load sidebar history ─────────────────────────────────────
  const loadHistory = useCallback(async (page = 1, append = false) => {
    setHistLoading(true);
    try {
      const res = await api.get(`/chat/history?page=${page}&limit=20`);
      const { chats, pagination } = res.data;
      setHistory((prev) => append ? [...prev, ...chats] : chats);
      setHistHasMore(pagination.has_next);
      setHistPage(pagination.page);
      if (page === 1) setApiOnline(true); // backend is responding
    } catch {
      // not fatal — sidebar just stays empty
    } finally {
      setHistLoading(false);
    }
  }, []);

  useEffect(() => { loadHistory(1); }, [loadHistory]);

  // ── Auto-resize textarea ─────────────────────────────────────
  const handleInputChange = (e) => {
    setInput(e.target.value);
    const el = inputRef.current;
    if (el) {
      el.style.height = 'auto';
      el.style.height = Math.min(el.scrollHeight, 120) + 'px';
    }
  };

  // ── Send message ─────────────────────────────────────────────
  const handleSend = async (overrideText) => {
    const question = (overrideText ?? input).trim();
    if (!question || loading) return;

    // Add user bubble
    const userMsg = { id: `u-${Date.now()}`, type: 'user', message: question };
    setMessages((prev) => [...prev.filter((m) => m.id !== 'welcome'), userMsg]);
    setInput('');
    if (inputRef.current) inputRef.current.style.height = 'auto';
    setLoading(true);

    try {
      const res = await api.post('/chat', { question });
      const { id, answer, category, sources, response_time, created_at } = res.data;

      const botMsg = {
        id:           `b-${id || Date.now()}`,
        dbId:         id,
        type:         'bot',
        message:      answer,
        category,
        sources:      sources || [],
        responseTime: response_time,
        timestamp:    created_at,
      };
      setMessages((prev) => [...prev, botMsg]);
      setApiOnline(true);

      // Refresh sidebar to show the new entry at the top
      loadHistory(1);
    } catch (err) {
      const errText =
        err.response?.data?.error ||
        'Could not reach the AI model. Please check that the Node backend is running and PYTHON_API_URL is set correctly in .env.';

      setMessages((prev) => [
        ...prev,
        {
          id:       `err-${Date.now()}`,
          type:     'bot',
          message:  `**Error ⚠️**\n\n${errText}`,
          category: 'general',
          sources:  [],
        },
      ]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  };

  // ── Keyboard: Enter to send, Shift+Enter for newline ─────────
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // ── New chat ─────────────────────────────────────────────────
  const handleNewChat = () => {
    setMessages([WELCOME]);
    setActiveHistId(null);
    setInput('');
    inputRef.current?.focus();
  };

  // ── Click history item: display that Q&A pair ────────────────
  const handleHistorySelect = (item) => {
    setActiveHistId(item.id);
    setMessages([
      {
        id:       `h-u-${item.id}`,
        type:     'user',
        message:  item.question,
      },
      {
        id:           `h-b-${item.id}`,
        type:         'bot',
        message:      item.answer,
        category:     item.category,
        sources:      item.sources || [],
        responseTime: item.response_time,
        timestamp:    item.created_at,
      },
    ]);
  };

  // ── Load more history ─────────────────────────────────────────
  const handleLoadMore = () => {
    loadHistory(histPage + 1, true);
  };

  // ── Whether to show the empty / welcome state ─────────────────
  const showEmptyState = messages.length === 1 && messages[0].id === 'welcome';

  return (
    <div className="chat-layout">
      {/* Background orbs */}
      <div className="orb orb-1" />
      <div className="orb orb-2" />
      <div className="orb orb-3" />

      {/* Sidebar */}
      <Sidebar
        history={history}
        loading={histLoading}
        activeId={activeHistId}
        hasMore={histHasMore}
        onSelect={handleHistorySelect}
        onNewChat={handleNewChat}
        onLoadMore={handleLoadMore}
      />

      {/* Main area */}
      <div className="chat-main">
        <Navbar apiOnline={apiOnline} />

        {/* Empty / welcome state */}
        {showEmptyState ? (
          <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
            <div className="empty-state">
              <div className="empty-icon">⚖️</div>
              <h1 className="empty-title">Legal Compass AI</h1>
              <p className="empty-sub">
                AI-powered answers on Indian Constitutional Law, IPC, and CrPC.
                Ask in plain language — no jargon needed.
              </p>
            </div>

            {/* Quick-start suggestions */}
            <div className="suggestions-row">
              {SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  className="chip"
                  onClick={() => handleSend(s)}
                  disabled={loading}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        ) : (
          /* Messages area */
          <div className="messages-area">
            {messages.map((msg) => (
              <ChatBubble
                key={msg.id}
                message={msg.message}
                type={msg.type}
                category={msg.category}
                sources={msg.sources}
                responseTime={msg.responseTime}
                timestamp={msg.timestamp}
              />
            ))}

            {/* Typing indicator */}
            {loading && (
              <div className="typing-row">
                <div className="msg-avatar" style={{
                  background: 'linear-gradient(135deg, var(--indigo), var(--gold))',
                  width: 36, height: 36, borderRadius: 10,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  flexShrink: 0,
                }}>
                  ⚖️
                </div>
                <div className="typing-bubble">
                  <div className="typing-dot" />
                  <div className="typing-dot" />
                  <div className="typing-dot" />
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}

        {/* Input area — always visible */}
        <div className="input-area">
          <div className="input-row">
            <textarea
              ref={inputRef}
              className="chat-input"
              rows={1}
              value={input}
              onChange={handleInputChange}
              onKeyDown={handleKeyDown}
              placeholder="Ask about Indian law… (e.g. 'What is Article 21?')"
              disabled={loading}
            />
            <button
              className="btn-send"
              onClick={() => handleSend()}
              disabled={loading || !input.trim()}
              aria-label="Send message"
            >
              {loading ? (
                <span className="spinner" />
              ) : (
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none"
                  stroke="white" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="m22 2-7 20-4-9-9-4z"/><path d="M22 2 11 13"/>
                </svg>
              )}
            </button>
          </div>
          <div className="input-hint">
            ⚠️ Informational only — not legal advice. Free legal aid:&nbsp;
            <a href="https://nalsa.gov.in" target="_blank" rel="noreferrer"
              style={{ color: 'var(--gold)' }}>NALSA</a>
            &nbsp;·&nbsp;Shift+Enter for new line
          </div>
        </div>
      </div>
    </div>
  );
}
