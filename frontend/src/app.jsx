import { BrowserRouter, Routes, Route } from "react-router-dom";

import Sidebar from "./components/layouts/Sidebar";
import Header from "./components/layouts/Header";

import Dashboard from "./pages/Dashboard";
import Inspection from "./pages/Inspection";
import Production from "./pages/Production";
import RootCause from "./pages/RootCause";
import Bottleneck from "./pages/Bottleneck";
import Economics from "./pages/Economics";
import Simulation from "./pages/Simulation";

function App() {
  return (
    <BrowserRouter>
      <div className="app-layout">
        <Sidebar />

        <div className="main-area">
          <Header />

          <main className="content-area">
            <Routes>
              <Route
                path="/"
                element={<Dashboard />}
              />

              <Route
                path="/inspection"
                element={<Inspection />}
              />

              <Route
                path="/production"
                element={<Production />}
              />

              <Route
                path="/root-cause"
                element={<RootCause />}
              />

              <Route
                path="/bottleneck"
                element={<Bottleneck />}
              />

              <Route
                path="/economics"
                element={<Economics />}
              />

              <Route
                path="/simulation"
                element={<Simulation />}
              />
            </Routes>
          </main>
        </div>
      </div>
    </BrowserRouter>
  );
}

export default App;