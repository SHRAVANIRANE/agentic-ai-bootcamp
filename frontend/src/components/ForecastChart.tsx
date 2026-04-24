import { useEffect, useState } from "react";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  Legend, Area, ComposedChart, ResponsiveContainer,
} from "recharts";

const API = import.meta.env.VITE_API_URL;

interface ForecastPoint {
  date: string;
  predicted_units: number;
  lower_bound: number;
  upper_bound: number;
}

export default function ForecastChart({ storeId, productId }: { storeId: string; productId: string }) {
  const [data, setData] = useState<ForecastPoint[]>([]);
  const [summary, setSummary] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    fetch(`${API}/forecast/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ store_id: storeId, product_id: productId, horizon_days: 30 }),
    })
      .then((r) => r.json())
      .then((res) => {
        setData(res.forecast ?? []);
        setSummary(res.trend_summary ?? "");
      })
      .finally(() => setLoading(false));
  }, [storeId, productId]);

  return (
    <div style={{ background: "#fff", borderRadius: "8px", padding: "16px", boxShadow: "0 1px 4px rgba(0,0,0,0.1)" }}>
      <h3>📈 30-Day Demand Forecast</h3>
      {loading ? <p>Loading...</p> : (
        <>
          <ResponsiveContainer width="100%" height={260}>
            <ComposedChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" tick={{ fontSize: 10 }} />
              <YAxis />
              <Tooltip />
              <Legend />
              <Area type="monotone" dataKey="upper_bound" fill="#dbeafe" stroke="none" name="Upper" />
              <Area type="monotone" dataKey="lower_bound" fill="#fff" stroke="none" name="Lower" />
              <Line type="monotone" dataKey="predicted_units" stroke="#2563eb" dot={false} name="Forecast" />
            </ComposedChart>
          </ResponsiveContainer>
          {summary && <p style={{ fontSize: "13px", color: "#555", marginTop: "8px" }}>{summary}</p>}
        </>
      )}
    </div>
  );
}
