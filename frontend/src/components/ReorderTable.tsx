import { useEffect, useState } from "react";

const API = import.meta.env.VITE_API_URL;

interface Recommendation {
  reorder_now: boolean;
  recommended_quantity: number;
  reorder_point: number;
  safety_stock: number;
  reasoning: string;
}

export default function ReorderTable({ storeId, productId }: { storeId: string; productId: string }) {
  const [rec, setRec] = useState<Recommendation | null>(null);
  const [inventory, setInventory] = useState(100);
  const [loading, setLoading] = useState(false);

  const fetchReorder = () => {
    setLoading(true);
    fetch(`${API}/reorder/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ store_id: storeId, product_id: productId, current_inventory: inventory }),
    })
      .then((r) => r.json())
      .then(setRec)
      .finally(() => setLoading(false));
  };

  useEffect(() => { fetchReorder(); }, [storeId, productId]);

  const badge = rec?.reorder_now
    ? { label: "⚠️ REORDER NOW", color: "#dc2626" }
    : { label: "✅ STOCK OK", color: "#16a34a" };

  return (
    <div style={{ background: "#fff", borderRadius: "8px", padding: "16px", boxShadow: "0 1px 4px rgba(0,0,0,0.1)" }}>
      <h3>🔄 Reorder Recommendation</h3>
      <div style={{ marginBottom: "12px" }}>
        <label>Current Inventory: </label>
        <input type="number" value={inventory} onChange={(e) => setInventory(Number(e.target.value))}
          style={{ width: "80px", marginLeft: "8px", padding: "4px" }} />
        <button onClick={fetchReorder} style={{ marginLeft: "8px", padding: "4px 12px" }}>Check</button>
      </div>
      {loading ? <p>Calculating...</p> : rec && (
        <>
          <div style={{ fontSize: "18px", fontWeight: "bold", color: badge.color, marginBottom: "12px" }}>
            {badge.label}
          </div>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "14px" }}>
            <tbody>
              {[
                ["Recommended Order Qty", rec.recommended_quantity],
                ["Reorder Point", rec.reorder_point],
                ["Safety Stock", rec.safety_stock],
              ].map(([label, val]) => (
                <tr key={label as string}>
                  <td style={{ padding: "4px 0", color: "#666" }}>{label}</td>
                  <td style={{ fontWeight: "600" }}>{val} units</td>
                </tr>
              ))}
            </tbody>
          </table>
          <p style={{ fontSize: "13px", color: "#555", marginTop: "12px", fontStyle: "italic" }}>
            💡 {rec.reasoning}
          </p>
        </>
      )}
    </div>
  );
}
