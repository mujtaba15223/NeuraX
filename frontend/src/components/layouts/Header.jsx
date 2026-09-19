import { Bell, Activity } from "lucide-react";

function Header() {
  return (
    <header className="header">
      <div>
        <span className="header-label">INDUSTRIAL OPERATIONS</span>
        <h1>Decision Intelligence Center</h1>
      </div>

      <div className="header-actions">
        <div className="live-status">
          <Activity size={17} />
          <span>Live Analysis</span>
        </div>

        <button className="icon-button" aria-label="Notifications">
          <Bell size={19} />
        </button>
      </div>
    </header>
  );
}

export default Header;