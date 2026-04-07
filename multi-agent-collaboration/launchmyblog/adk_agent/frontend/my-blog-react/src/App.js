import logo from './logo.svg';
import './App.css';
import React, { useState } from "react";
import AgentCard from "./components/AgentCard";

function App() {
  const agents = [
    "mcp_drafting_app",
    "mcp_plagiarism_app",
    "mcp_seo_app",
    "mcp_publishing_app",
    "mcp_seo_app",
  ];

  return (
    <div style={{ padding: "2rem" }}>
      <h1>Agent Dashboard</h1>
      <p>Interact with your FastAPI agents via the orchestrator.</p>
      {agents.map(agent => (
        <AgentCard key={agent} agent={agent} />
      ))}
    </div>
  );
}

export default App;