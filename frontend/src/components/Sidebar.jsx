/**
 * Legal Compass — Sidebar Component
 * Shows past chat history fetched from PostgreSQL.
 * Clicking a history item calls onSelect(item).
 *
 * Props:
 *   history       {Array}    — list of chat objects from DB
 *   loading       {boolean}
 *   activeId      {number?}  — currently selected chat id
 *   hasMore       {boolean}
 *   onSelect      {fn(item)} — called when user clicks a history item
 *   onNewChat     {fn}       — called when "New Chat" is clicked
 *   onLoadMore    {fn}       — called to load next page
 */

const CAT_CLASSES = {
  constitution: 'cat-constitution',
  ipc:          'cat-ipc',
  crpc:         'cat-crpc',
  general:      'cat-general',
};

function relativeDate(iso) {
  try {
    const d   = new Date(iso);
    const now = new Date();
    const diffDays = Math.floor((now - d) / 86_400_000);
    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7)  return `${diffDays}d ago`;
    return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short' });
  } catch {
    return '';
  }
}

export default function Sidebar({
  history  = [],
  loading  = false,
  activeId = null,
  hasMore  = false,
  onSelect,
  onNewChat,
  onLoadMore,
}) {
  return (
    <aside className="sidebar">
      {/* Logo */}
      <div className="sidebar-header">
        <div className="sidebar-logo-icon">⚖️</div>
        <div className="sidebar-logo-text">
          Legal<span>Compass</span>
        </div>
      </div>

      {/* New Chat button */}
      <button className="btn-new-chat" onClick={onNewChat}>
        <span>＋</span> New Chat
      </button>

      {/* History list */}
      <div className="sidebar-section-label">Recent Chats</div>

      <div className="sidebar-list">
        {loading && history.length === 0 ? (
          <div className="sidebar-empty">Loading history…</div>
        ) : history.length === 0 ? (
          <div className="sidebar-empty">
            No chats yet.<br />Ask your first legal question!
          </div>
        ) : (
          history.map((item) => (
            <div
              key={item.id}
              className={`sidebar-item${activeId === item.id ? ' active' : ''}`}
              onClick={() => onSelect(item)}
              title={item.question}
            >
              <div className="sidebar-item-q">{item.question}</div>
              <div className="sidebar-item-meta">
                {item.category && (
                  <span className={`cat-badge ${CAT_CLASSES[item.category] || 'cat-general'}`}
                    style={{ fontSize: '0.6rem' }}>
                    {item.category}
                  </span>
                )}
                <span className="sidebar-item-time">
                  {relativeDate(item.created_at)}
                </span>
              </div>
            </div>
          ))
        )}

        {hasMore && (
          <button className="sidebar-load-more" onClick={onLoadMore} disabled={loading}>
            {loading ? 'Loading…' : 'Load more'}
          </button>
        )}
      </div>
    </aside>
  );
}
