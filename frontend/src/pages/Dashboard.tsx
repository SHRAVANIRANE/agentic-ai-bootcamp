import { useState, useEffect } from "react";
import ForecastChart from "../components/ForecastChart";
import ReorderTable from "../components/ReorderTable";
import AgentChat from "../components/AgentChat";
import DataUpload from "../components/DataUpload";

const API = import.meta.env.VITE_API_URL;

export default function Dashboard() {
  const [stores, setStores] = useState<string[]>([]);
  const [products, setProducts] = useState<string[]>([]);
  const [storeId, setStoreId] = useState("S001");
  const [productId, setProductId] = useState("P0001");
  const [applied, setApplied] = useState({ storeId: "S001", productId: "P0001" });
  const [dataInfo, setDataInfo] = useState({ rows: 0, source: "default", totalProducts: 0 });
  const [activeTab, setActiveTab] = useState<"forecast" | "chat" | "upload">("forecast");
  const [refreshKey, setRefreshKey] = useState(0);

  useEffect(() => {
    fetch(`${API}/forecast/stores`)
      .then((r) => r.json())
      .then((d) => setStores(d.stores || []))
      .catch(() => setStores(["S001", "S002", "S003", "S004", "S005"]));
    fetch(`${API}/data/info`)
      .then((r) => r.json())
      .then((d) => setDataInfo({ rows: d.rows, source: d.source, totalProducts: d.total_products }))
      .catch(() => {});
  }, [refreshKey]);

  useEffect(() => {
    fetch(`${API}/forecast/products?store_id=${storeId}`)
      .then((r) => r.json())
      .then((d) => {
        const prods = d.products || [];
        setProducts(prods);
        setProductId(prods[0] || "P0001");
      })
      .catch(() => setProducts(["P0001"]));
  }, [storeId]);

  const tabs = [
    { id: "forecast", label: "Forecast" },
    { id: "chat", label: "AI Chat" },
    { id: "upload", label: "Data" },
  ] as const;

  const stats = [
    { label: "Stores", value: stores.length || 5, icon: null, cls: "blue" },
    { label: "Products", value: dataInfo.totalProducts || products.length, icon: null, cls: "purple" },
    { label: "Data Rows", value: dataInfo.rows ? dataInfo.rows.toLocaleString() : "73,100", icon: null, cls: "green" },
    { label: "Source", value: dataInfo.source === "default" ? "Default" : dataInfo.source.slice(0, 12), icon: null, cls: "orange" },
  ];

  return (
    <div>
      {/* Navbar */}
      <nav className="navbar">
        <div className="navbar-brand">
          <div className="navbar-brand-icon">INV</div>
          <div>
            <div className="navbar-title">Inventory Forecasting Agent</div>
            <div className="navbar-subtitle">XGBoost · Gemma AI · LangChain</div>
          </div>
        </div>
        <div className="nav-tabs">
          {tabs.map((t) => (
            <button key={t.id} className={`nav-tab ${activeTab === t.id ? "active" : "inactive"}`}
              onClick={() => setActiveTab(t.id)}>
              {t.label}
            </button>
          ))}
        </div>
      </nav>

      <div className="main">
        {/* Stats */}
        <div className="stats-grid">
          {stats.map((s) => (
            <div key={s.label} className={`stat-card ${s.cls}`}>
              <div className="stat-value" style={{ color: s.cls === "blue" ? "var(--accent-blue)" : s.cls === "purple" ? "var(--accent-purple)" : s.cls === "green" ? "var(--accent-green)" : "var(--accent-orange)" }}>
                {s.value}
              </div>
              <div className="stat-label">{s.label}</div>
            </div>
          ))}
        </div>

        {/* Selector */}
        <div className="selector-bar">
          <div className="selector-group">
            <label className="selector-label">Store</label>
            <select className="selector-select" value={storeId} onChange={(e) => setStoreId(e.target.value)}>
              {stores.map((s) => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>
          <div className="selector-group">
            <label className="selector-label">Product</label>
            <select className="selector-select" value={productId} onChange={(e) => setProductId(e.target.value)}>
              {products.map((p) => <option key={p} value={p}>{p}</option>)}
            </select>
          </div>
          <button className="btn btn-primary" onClick={() => setApplied({ storeId, productId })}>
          Analyze
          </button>
          <div className="analyzing-badge">
            <span className="blue">{applied.storeId}</span> / <span className="purple">{applied.productId}</span>
          </div>
        </div>

        {/* Content */}
        {activeTab === "forecast" && (
          <div className="content-grid">
            <ForecastChart storeId={applied.storeId} productId={applied.productId} />
            <ReorderTable storeId={applied.storeId} productId={applied.productId} />
          </div>
        )}
        {activeTab === "chat" && (
          <AgentChat storeId={applied.storeId} productId={applied.productId} />
        )}
        {activeTab === "upload" && (
          <DataUpload onUploadSuccess={(newStores, newProducts) => {
            setStores(newStores);
            const firstStore = newStores[0] || "S001";
            const firstProduct = newProducts[0] || "P0001";
            setStoreId(firstStore);
            setProductId(firstProduct);
            setProducts(newProducts);
            setApplied({ storeId: firstStore, productId: firstProduct });
            setRefreshKey(k => k + 1);
            setActiveTab("forecast");
          }} />
        )}
      </div>
    </div>
  );
}
