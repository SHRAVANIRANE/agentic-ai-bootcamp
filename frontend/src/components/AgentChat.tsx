import { useState } from "react";

const API = import.meta.env.VITE_API_URL;

interface Message { role: "user" | "agent"; text: string }

export default function AgentChat({ storeId, productId }: { storeId: string; productId: string }) {
  const [messages, setMessages] = useState<Message[]>([
    { role: "agent", text: "Hi! Ask me anything about inventory, forecasts, or reorder decisions." },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const send = async () => {
    if (!input.trim()) return;
    const userMsg: Message = { role: "user", text: input };
    setMessages((m) => [...m, userMsg]);
    setInput("");
    setLoading(true);

    const res = await fetch(`${API}/agent/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: input, store_id: storeId, product_id: productId }),
    });
    const data = await res.json();
    setMessages((m) => [...m, { role: "agent", text: data.response }]);
    setLoading(false);
  };

  return (
    <div style={{ background: "#fff", borderRadius: "8px", padding: "16px", boxShadow: "0 1px 4px rgba(0,0,0,0.1)" }}>
      <h3>🤖 Ask the Inventory Agent (Llama 3)</h3>
      <div style={{ height: "200px", overflowY: "auto", border: "1px solid #e5e7eb", borderRadius: "6px", padding: "12px", marginBottom: "12px" }}>
        {messages.map((m, i) => (
          <div key={i} style={{ marginBottom: "8px", textAlign: m.role === "user" ? "right" : "left" }}>
            <span style={{
              display: "inline-block", padding: "6px 12px", borderRadius: "12px", fontSize: "13px",
              background: m.role === "user" ? "#2563eb" : "#f3f4f6",
              color: m.role === "user" ? "#fff" : "#111",
            }}>
              {m.text}
            </span>
          </div>
        ))}
        {loading && <p style={{ color: "#999", fontSize: "13px" }}>Agent is thinking...</p>}
      </div>
      <div style={{ display: "flex", gap: "8px" }}>
        <input value={input} onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}
          placeholder="e.g. Should I reorder P001 at S001 with 50 units left?"
          style={{ flex: 1, padding: "8px 12px", borderRadius: "6px", border: "1px solid #d1d5db" }} />
        <button onClick={send} disabled={loading}
          style={{ padding: "8px 16px", background: "#2563eb", color: "#fff", border: "none", borderRadius: "6px", cursor: "pointer" }}>
          Send
        </button>
      </div>
    </div>
  );
}
