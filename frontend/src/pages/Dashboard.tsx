import { useState } from "react";
import ForecastChart from "../components/ForecastChart";
import ReorderTable from "../components/ReorderTable";
import AgentChat from "../components/AgentChat";

export default function Dashboard() {
  const [storeId, setStoreId] = useState("S001");
  const [productId, setProductId] = useState("P001");

  return (
    <div style={{ fontFamily: "Inter, sans-serif", padding: "24px", maxWidth: "1200px", margin: "0 auto" }}>
      <h1>📦 Inventory Demand Forecasting Agent</h1>

      <div style={{ display: "flex", gap: "12px", marginBottom: "24px" }}>
        <label>
          Store ID:
          <input value={storeId} onChange={(e) => setStoreId(e.target.value)}
            style={{ marginLeft: "8px", padding: "4px 8px" }} />
        </label>
        <label>
          Product ID:
          <input value={productId} onChange={(e) => setProductId(e.target.value)}
            style={{ marginLeft: "8px", padding: "4px 8px" }} />
        </label>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "24px" }}>
        <ForecastChart storeId={storeId} productId={productId} />
        <ReorderTable storeId={storeId} productId={productId} />
      </div>

      <div style={{ marginTop: "24px" }}>
        <AgentChat storeId={storeId} productId={productId} />
      </div>
    </div>
  );
}
