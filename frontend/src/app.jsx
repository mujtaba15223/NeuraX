import { useState } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import Sidebar from "./components/layouts/Sidebar";
import Header from "./components/layouts/Header";

import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Inspection from "./pages/Inspection";
import Production from "./pages/Production";
import RootCause from "./pages/RootCause";
import Bottleneck from "./pages/Bottleneck";
import Economics from "./pages/Economics";
import Simulation from "./pages/Simulation";

function ProtectedLayout({ children }) {
  const isLoggedIn =
    sessionStorage.getItem("industrial_logged_in") === "true";

  if (!isLoggedIn) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="app-layout">
      <Sidebar />

      <div className="main-area">
        <Header />

        <main className="content-area">
          {children}
        </main>
      </div>
    </div>
  );
}

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(
    sessionStorage.getItem("industrial_logged_in") === "true"
  );

  const handleLogin = () => {
    setIsLoggedIn(true);
  };

  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/login"
          element={
            isLoggedIn ? (
              <Navigate to="/" replace />
            ) : (
              <Login onLogin={handleLogin} />
            )
          }
        />

        <Route
          path="/*"
          element={
            <ProtectedLayout>
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/inspection" element={<Inspection />} />
                <Route path="/production" element={<Production />} />
                <Route path="/root-cause" element={<RootCause />} />
                <Route path="/bottleneck" element={<Bottleneck />} />
                <Route path="/economics" element={<Economics />} />
                <Route path="/simulation" element={<Simulation />} />
                <Route
                  path="*"
                  element={<Navigate to="/" replace />}
                />
              </Routes>
            </ProtectedLayout>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;