import {
  LayoutDashboard,
  ScanSearch,
  Factory,
  GitBranch,
  AlertTriangle,
  IndianRupee,
  FlaskConical,
} from "lucide-react";

import { NavLink } from "react-router-dom";

const navigation = [
  {
    label: "Dashboard",
    path: "/",
    icon: LayoutDashboard,
  },
  {
    label: "Inspection",
    path: "/inspection",
    icon: ScanSearch,
  },
  {
    label: "Production",
    path: "/production",
    icon: Factory,
  },
  {
    label: "Root Cause",
    path: "/root-cause",
    icon: GitBranch,
  },
  {
    label: "Bottleneck",
    path: "/bottleneck",
    icon: AlertTriangle,
  },
  {
    label: "Economics",
    path: "/economics",
    icon: IndianRupee,
  },
  {
    label: "Simulation",
    path: "/simulation",
    icon: FlaskConical,
  },
];

function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="brand-mark">AI</div>

        <div>
          <h2>Industrial AI</h2>
          <span>Decision Support</span>
        </div>
      </div>

      <nav className="sidebar-nav">
        {navigation.map(
          ({ label, path, icon: Icon }) => (
            <NavLink
              key={label}
              to={path}
              end={path === "/"}
              className={({ isActive }) =>
                `nav-item ${
                  isActive ? "active" : ""
                }`
              }
            >
              <Icon size={19} />
              <span>{label}</span>
            </NavLink>
          )
        )}
      </nav>
    </aside>
  );
}

export default Sidebar;