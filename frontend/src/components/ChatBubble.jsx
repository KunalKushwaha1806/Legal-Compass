/**
 * Legal Compass — ChatBubble Component
 * Renders a single user or bot message.
 * Bot messages are rendered as Markdown.
 *
 * Props:
 *   message       {string}  — raw text (user) or markdown (bot)
 *   type          {'user'|'bot'}
 *   category      {string?} — e.g. 'constitution', 'ipc', 'crpc', 'general'
 *   sources       {string[]} — cited provisions
 *   responseTime  {number?} — seconds taken by the model
 *   timestamp     {string?} — ISO date string
 */
import { useMemo } from 'react';
import { marked } from 'marked';

// Configure marked once
marked.setOptions({ breaks: true, gfm: true });

const CAT_LABELS = {
  constitution: '⚖️ Constitutional',
  ipc:          '🔴 IPC',
  crpc:         '🔵 CrPC',
  general:      '📋 General',
};

function formatTime(iso) {
  if (!iso) return '';
  try {
    return new Date(iso).toLocaleTimeString('en-IN', {
      hour: '2-digit', minute: '2-digit',
    });
  } catch {
    return '';
  }
}

export default function ChatBubble({
  message,
  type,
  category,
  sources    = [],
  responseTime,
  timestamp,
}) {
  const isBot = type === 'bot';

  // Parse markdown for bot messages
  const htmlContent = useMemo(() => {
    if (!isBot) return null;
    return marked.parse(message || '');
  }, [message, isBot]);

  return (
    <div className={`msg-row ${type}`}>
      {/* Avatar */}
      <div className="msg-avatar">
        {isBot ? '⚖️' : '👤'}
      </div>

      {/* Content */}
      <div className="msg-body">
        <div className="msg-bubble">
          {isBot ? (
            <div
              dangerouslySetInnerHTML={{ __html: htmlContent }}
            />
          ) : (
            message
          )}
        </div>

        {/* Meta row — only for bot */}
        {isBot && (
          <div className="msg-meta">
            {category && (
              <span className={`cat-badge cat-${category}`}>
                {CAT_LABELS[category] || category}
              </span>
            )}
            {sources.length > 0 && (
              <span className="msg-src">
                📎 {sources.join(', ')}
              </span>
            )}
            {responseTime != null && (
              <span className="msg-resp-time">
                ⏱ {Number(responseTime).toFixed(2)}s
              </span>
            )}
            {timestamp && (
              <span className="msg-time">{formatTime(timestamp)}</span>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
