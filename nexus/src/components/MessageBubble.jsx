import { EMOJIS } from '../constants'

export default function MessageBubble({
  msg,
  currentUid,
  roomColor,
  pickerOpen,
  onTogglePicker,
  onReply,
  onReact,
}) {
  const isMe = msg.authorUid === currentUid
  const reactionCounts = Object.values(msg.reactions || {}).reduce((acc, emoji) => {
    acc[emoji] = (acc[emoji] || 0) + 1
    return acc
  }, {})
  const myReaction = msg.reactions?.[currentUid]

  const time = msg.timestamp?.toDate
    ? msg.timestamp.toDate().toLocaleTimeString('cs', { hour: '2-digit', minute: '2-digit' })
    : '…'

  return (
    <div className={`message-row ${isMe ? 'mine' : ''}`}>
      {!isMe && <div className="message-avatar">{(msg.nickname || '?')[0].toUpperCase()}</div>}

      <div className="message-stack">
        {!isMe && <div className="message-author" style={{ color: roomColor }}>{msg.nickname}</div>}

        {msg.replyTo && (
          <div className="reply-preview">
            ↩ {msg.replyTo.nickname}: {msg.replyTo.text.slice(0, 80)}
            {msg.replyTo.text.length > 80 ? '…' : ''}
          </div>
        )}

        <div className={`bubble ${isMe ? 'bubble-mine' : 'bubble-other'}`}>
          {msg.text}
        </div>

        <div className="message-time">{time}{isMe ? ' ✓' : ''}</div>

        {Object.keys(reactionCounts).length > 0 && (
          <div className="reaction-summary">
            {Object.entries(reactionCounts).map(([emoji, count]) => (
              <button
                key={emoji}
                className={`reaction-chip ${myReaction === emoji ? 'selected' : ''}`}
                onClick={() => onReact(msg.id, emoji)}
              >
                {emoji} <small>{count}</small>
              </button>
            ))}
          </div>
        )}
      </div>

      <div className="message-actions">
        <button onClick={() => onTogglePicker(msg.id)}>😊</button>
        <button onClick={() => onReply(msg)}>↩</button>
      </div>

      {pickerOpen && (
        <div className={`reaction-picker ${isMe ? 'picker-right' : 'picker-left'}`}>
          {EMOJIS.map((emoji) => (
            <button key={emoji} onClick={() => onReact(msg.id, emoji)}>{emoji}</button>
          ))}
        </div>
      )}
    </div>
  )
}
