import React from "react";
import { Routes, Route } from "react-router-dom";
import { AuthProvider } from "./contexts/AuthContext";
import Navbar from "./components/Navbar";
import Home from "./pages/Home";
import AuthPage from "./pages/Auth";
import AgentIframe from "./pages/AgentIframe";

export default function App() {
  return (
    <AuthProvider>
      <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100">
        <Navbar />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/auth" element={<AuthPage />} />
          <Route path="/agent/:agentId" element={<AgentRoute />} />
          <Route path="/agents" element={<AgentsList />} />
        </Routes>
      </div>
    </AuthProvider>
  );
}

function AgentRoute() {
  const agentId = window.location.pathname.split("/").pop();
  return <AgentIframe agentId={agentId} />;
}

function AgentsList() {
  return (
    <div className="max-w-6xl mx-auto p-6">
      <h2 className="text-3xl font-bold text-gray-900 mb-8">Available Agents</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {[
          { name: "WriteAiDaily", link: "/agent/writeaidaily", desc: "Your AI-powered writing companion." },
          { name: "Agent 2", link: "#", desc: "Coming soon — new AI agent tools." },
          { name: "Agent 3", link: "#", desc: "Coming soon — more powerful agents." },
        ].map((agent, idx) => (
          <a
            key={idx}
            href={agent.link}
            className={`p-6 bg-white rounded-xl shadow hover:shadow-md transition hover:translate-y-[-2px] block ${
              agent.link === "#" ? "cursor-not-allowed opacity-60" : ""
            }`}
          >
            <h3 className="font-semibold text-lg text-gray-900">{agent.name}</h3>
            <p className="mt-2 text-sm text-gray-600">{agent.desc}</p>
          </a>
        ))}
      </div>
    </div>
  );
}
