import { ROOMS } from '../constants'

export default function Sidebar({ online, room, onRoomChange, nickname, onLogout }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-top">
        <div className="brand-row">
          <div className="brand-icon">⚡</div>
          <strong>NEXUS</strong>
          <span className="online-pill">🟡 {online.length}</span>
        </div>

        <div className="section-label">MÍSTNOSTI</div>
        {ROOMS.map((item) => {
          const count = online.filter((user) => user.room === item.id).length
          return (
            <button
              key={item.id}
              className={`room-button ${room === item.id ? 'active' : ''}`}
              onClick={() => onRoomChange(item.id)}
              style={{ '--room-color': item.color }}
            >
              <span>{item.emoji}</span>
              <span># {item.name}</span>
              {count > 0 && <span className="room-count">{count}</span>}
            </button>
          )
        })}
      </div>

      <div className="online-list">
        <div className="section-label">ONLINE — {online.length}</div>
        {online.map((user) => (
          <div className="online-user" key={user.uid}>
            <div className="avatar">{(user.nickname || '?')[0].toUpperCase()}</div>
            <div className="online-user-copy">
              <div>{user.nickname}</div>
              <small>#{ROOMS.find((item) => item.id === user.room)?.name || user.room}</small>
            </div>
            <span className="green-dot" />
          </div>
        ))}
      </div>

      <div className="me-row">
        <div className="avatar">{nickname[0].toUpperCase()}</div>
        <div className="me-copy">
          <strong>{nickname}</strong>
          <small>● Online</small>
        </div>
        <button className="ghost-button" onClick={onLogout} title="Odhlásit">↪</button>
      </div>
    </aside>
  )
}
