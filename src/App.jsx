import React, { useState, useEffect } from "react";
import {
  AreaChart,
  Area,
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ComposedChart,
} from "recharts";
import {
  Users,
  TrendingUp,
  Layers,
  BarChart3,
  Scale,
  AlertTriangle,
  Database,
  Search,
  Smartphone,
  ArrowUpRight,
  Loader,
  Brain,
  Activity,
} from "lucide-react";
import "./App.css";

const API_BASE = "/api";

function useApi(endpoint) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    fetch(`${API_BASE}${endpoint}`)
      .then((r) => r.json())
      .then(setData)
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, [endpoint]);
  return { data, loading };
}

function SoftTooltip({ active, payload, label }) {
  if (!active || !payload || !payload.length) return null;
  return (
    <div className="tooltip">
      <div className="tooltipTitle">{label}</div>
      {payload.map((p) => (
        <div key={p.dataKey} className="tooltipRow">
          <span className="dot" style={p.color ? { background: p.color } : {}} />
          <span className="tooltipKey">{p.name ?? p.dataKey}</span>
          <span className="tooltipVal">
            {typeof p.value === "number" ? p.value.toLocaleString() : p.value}
          </span>
        </div>
      ))}
    </div>
  );
}

function Pill({ children, muted }) {
  return <span className={`pill ${muted ? "pillMuted" : ""}`}>{children}</span>;
}

function Card({ title, icon, right, children, className }) {
  return (
    <div className={`card ${className || ""}`}>
      <div className="cardTop">
        <div className="cardTitle">
          {icon ? <span className="cardIcon">{icon}</span> : null}
          <span>{title}</span>
        </div>
        {right ? <div className="cardRight">{right}</div> : null}
      </div>
      <div className="cardBody">{children}</div>
    </div>
  );
}

function LoadingState() {
  return (
    <div className="loadingWrap">
      <Loader size={20} className="spinner" />
      <span className="muted">Loading data...</span>
    </div>
  );
}

function Header() {
  return (
    <div className="header">
      <div className="brand">
        <div className="brandMark">
          <Users size={18} />
        </div>
        <div className="brandText">
          <div className="brandTitle">Gig Economy Observatory</div>
          <div className="brandSub">Platform-Based Employment Intelligence</div>
        </div>
      </div>
      <div className="headerControls">
        <div className="methodBadge">
          <Database size={14} />
          <span>Tadawul-Anchored</span>
        </div>
        <div className="methodBadge">
          <Scale size={14} />
          <span>Multi-Source Triangulation</span>
        </div>
      </div>
    </div>
  );
}

function KpiRow({ data }) {
  if (!data) return <LoadingState />;

  const platforms = data.platforms || {};
  const platformNames = Object.values(platforms).map((p) => p.name);

  return (
    <div className="kpiGrid">
      <Card title="Estimated Gig Workers" icon={<Users size={18} />}>
        <div className="kpiMain">
          <div className="kpiValue">
            {(data.unique_workers_estimate / 1000).toFixed(0)}k
          </div>
          <div className="kpiSub">
            <Pill muted>
              Range: {(data.confidence_low / 1000).toFixed(0)}k →{" "}
              {(data.confidence_high / 1000).toFixed(0)}k
            </Pill>
          </div>
        </div>
      </Card>

      <Card title="Blind Spot Gap" icon={<AlertTriangle size={18} />}>
        <div className="kpiMain">
          <div className="kpiValue kpiWarn">
            +{(data.gap / 1000).toFixed(0)}k
          </div>
          <div className="kpiSub">
            <Pill muted>{data.gap_pct}% unregistered in GOSI</Pill>
          </div>
          <div className="gapBar">
            <div
              className="gapBarOfficial"
              style={{ width: `${(data.official_gosi / data.unique_workers_estimate) * 100}%` }}
            >
              <span>GOSI</span>
            </div>
            <div className="gapBarGap">
              <span>Gap</span>
            </div>
          </div>
        </div>
      </Card>

      <Card title="Coverage" icon={<Layers size={18} />}>
        <div className="coverage">
          <div className="coverageRow">
            <div className="coverageKey">Platforms Tracked:</div>
            <div className="coverageVal">{platformNames.length}</div>
          </div>
          <div className="coverageList">
            {platformNames.map((p) => (
              <span className="chip" key={p}>{p}</span>
            ))}
          </div>
          <div className="coverageMeta">
            <span className="muted">Quarter:</span>{" "}
            <span>{data.quarter?.replace("_", " ")}</span>
          </div>
        </div>
      </Card>

      <Card title="Official vs Estimated" icon={<BarChart3 size={18} />}>
        <div className="gap">
          <div className="gapCompare">
            <div className="gapCompareItem">
              <div className="gapCompareLabel muted">GOSI Registered</div>
              <div className="gapCompareValue">{(data.official_gosi / 1000).toFixed(1)}k</div>
            </div>
            <div className="gapCompareDivider">vs</div>
            <div className="gapCompareItem">
              <div className="gapCompareLabel muted">Our Estimate</div>
              <div className="gapCompareValue kpiPositive">
                {(data.unique_workers_estimate / 1000).toFixed(1)}k
              </div>
            </div>
          </div>
          <div className="muted" style={{ marginTop: 6, fontWeight: 700 }}>
            Overlap correction: {(data.overlap_rate * 100).toFixed(0)}% multi-platform
          </div>
        </div>
      </Card>
    </div>
  );
}

function WorkforceChart({ data }) {
  if (!data)
    return (
      <Card title="Estimated vs Official Workforce" className="bigCard">
        <LoadingState />
      </Card>
    );

  const historical = (data.historical || []).map((d) => ({
    q: d.quarter.replace("_", " "),
    estimated: d.estimated,
    official: d.official,
    gap: d.gap,
    low: d.confidence_low,
    high: d.confidence_high,
  }));

  const forecast = (data.forecast || []).map((d) => ({
    q: d.quarter.replace("_", " "),
    forecast: d.forecast,
    forecastLow: d.confidence_low,
    forecastHigh: d.confidence_high,
  }));

  const gosiForecast = (data.gosi_forecast || []).map((d) => ({
    q: d.quarter.replace("_", " "),
    gosiForecast: d.forecast,
  }));

  const merged = [...historical];
  if (historical.length && forecast.length) {
    const last = historical[historical.length - 1];
    forecast[0] = { ...forecast[0], estimated: last.estimated, official: last.official };
  }
  forecast.forEach((f, i) => {
    merged.push({ ...f, ...(gosiForecast[i] || {}) });
  });

  return (
    <Card
      title={
        <span>
          Estimated vs Official Workforce <span className="muted">(Quarterly)</span>
        </span>
      }
      right={
        <span className="legendHint">
          <span className="legendDot" /> Estimate
          <span className="legendDot legendDotMuted" /> GOSI
        </span>
      }
      className="bigCard"
    >
      <div className="chartWrap">
        <ResponsiveContainer width="100%" height={300}>
          <ComposedChart data={merged} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="estFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="10%" stopColor="rgba(47,109,85,0.3)" stopOpacity={1} />
                <stop offset="95%" stopColor="rgba(47,109,85,0.02)" stopOpacity={1} />
              </linearGradient>
              <linearGradient id="fcFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="10%" stopColor="rgba(196,156,84,0.25)" stopOpacity={1} />
                <stop offset="95%" stopColor="rgba(196,156,84,0.02)" stopOpacity={1} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="4 10" opacity={0.35} />
            <XAxis dataKey="q" tickMargin={10} />
            <YAxis tickMargin={10} />
            <Tooltip content={<SoftTooltip />} />
            <Area type="monotone" dataKey="high" name="High" strokeOpacity={0} fill="url(#estFill)" />
            <Area type="monotone" dataKey="low" name="Low" strokeOpacity={0} fillOpacity={0} />
            <Area type="monotone" dataKey="forecastHigh" name="Forecast High" strokeOpacity={0} fill="url(#fcFill)" />
            <Area type="monotone" dataKey="forecastLow" name="Forecast Low" strokeOpacity={0} fillOpacity={0} />
            <Line type="monotone" dataKey="estimated" name="Our Estimate" stroke="rgba(47,109,85,0.9)" strokeWidth={3} dot={false} />
            <Line type="monotone" dataKey="official" name="GOSI Official" stroke="rgba(47,109,85,0.35)" strokeWidth={2} strokeDasharray="6 4" dot={false} />
            <Line type="monotone" dataKey="forecast" name="Forecast" stroke="rgba(196,156,84,0.85)" strokeWidth={3} strokeDasharray="8 4" dot={false} />
            <Line type="monotone" dataKey="gosiForecast" name="GOSI Projected" stroke="rgba(196,156,84,0.4)" strokeWidth={2} strokeDasharray="4 4" dot={false} />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
      <div className="chartLegendRow">
        <div className="legendItem"><span className="legendSwatch swatchLine" /> Our Estimate</div>
        <div className="legendItem"><span className="legendSwatch swatchDash" /> GOSI Official</div>
        <div className="legendItem"><span className="legendSwatch swatchForecast" /> Forecast</div>
        <div className="legendItem"><span className="legendSwatch swatchBand" /> Confidence</div>
      </div>
    </Card>
  );
}

function TriangulationChart({ data }) {
  if (!data)
    return (
      <Card title="Triangulated Estimation" className="bigCard">
        <LoadingState />
      </Card>
    );

  const methods = (data.methods || []).map((m) => ({
    name: m.name,
    estimate: m.estimate_jahez,
    confidence: m.confidence,
    weight: m.weight * 100,
    description: m.description,
    source: m.source,
  }));

  return (
    <Card
      title="Triangulated Estimation"
      right={<span className="muted"><Scale size={16} style={{ verticalAlign: "middle" }} /> Jahez anchor</span>}
      className="bigCard"
    >
      <div className="triangulationGrid">
        {methods.map((m) => (
          <div className="triMethod" key={m.name}>
            <div className="triHeader">
              <span className="triName">{m.name}</span>
              <span className={`triBadge triBadge-${m.confidence}`}>{m.confidence}</span>
            </div>
            <div className="triValue">{m.estimate.toLocaleString()}</div>
            <div className="triSource muted">{m.source}</div>
            <div className="triWeight">
              <div className="triWeightBar">
                <div className="triWeightFill" style={{ width: `${m.weight}%` }} />
              </div>
              <span className="muted">Weight: {m.weight}%</span>
            </div>
          </div>
        ))}
      </div>
      <div className="formula">
        <span className="muted">Method: </span>{data.formula}
      </div>
      <div className="triResult">
        <span className="muted">Triangulated Total (all platforms):</span>
        <span className="triResultValue">{data.triangulated_estimate?.toLocaleString()} workers</span>
      </div>
    </Card>
  );
}

function PlatformBreakdown({ data }) {
  if (!data) return <Card title="Platform Breakdown"><LoadingState /></Card>;

  const platforms = data.platforms || {};
  const entries = Object.entries(platforms);
  const maxWorkers = Math.max(...entries.map(([, p]) => p.confidence_high || p.estimated_workers));

  return (
    <Card
      title={<span>Platform Breakdown <span className="muted">(Workers)</span></span>}
      right={<span className="muted">Q: {data.quarter?.replace("_", " ")}</span>}
    >
      <div className="rangeList">
        {entries.map(([key, p]) => {
          const low = p.confidence_low;
          const high = p.confidence_high;
          const left = (low / maxWorkers) * 100;
          const width = ((high - low) / maxWorkers) * 100;
          return (
            <div className="rangeRow" key={key}>
              <div className="rangeLabel">{p.name}</div>
              <div className="rangeTrack">
                <div className="rangeFill" style={{ marginLeft: `${left}%`, width: `${width}%` }} />
              </div>
              <div className="rangeVal muted">{(low / 1000).toFixed(1)}–{(high / 1000).toFixed(1)}k</div>
            </div>
          );
        })}
      </div>
      <div className="muted miniFoot">
        Overlap correction: {(data.overlap_rate * 100).toFixed(0)}% multi-platform ·
        Total unique: {(data.total_unique / 1000).toFixed(1)}k
      </div>
    </Card>
  );
}

function TrendsCard({ data }) {
  if (!data) return <Card title="Search Interest"><LoadingState /></Card>;

  const consumer = data.consumer_demand?.data || [];
  const terms = data.consumer_demand?.terms || [];

  // Average the last 4 weeks for a stable snapshot
  const recentWeeks = consumer.slice(-4);
  const bars = terms
    .map((term) => {
      const avg = recentWeeks.reduce((sum, d) => sum + (d[term] || 0), 0) / (recentWeeks.length || 1);
      return { platform: term, score: Math.round(avg) };
    })
    .sort((a, b) => b.score - a.score);

  return (
    <Card
      title={<span>Search Interest <span className="muted">(Google Trends)</span></span>}
      right={<span className="kpiTinyUp"><TrendingUp size={14} /> Consumer</span>}
    >
      <div className="hbarList">
        {bars.map((r) => (
          <div className="hbarRow" key={r.platform}>
            <div className="hbarLabel" style={{ fontSize: 12 }}>{r.platform}</div>
            <div className="hbarTrack">
              <div className="hbarFill" style={{ width: `${r.score}%` }} />
            </div>
            <div className="hbarVal muted">{r.score}</div>
          </div>
        ))}
      </div>
      <div className="muted miniFoot">Latest month snapshot · Saudi Arabia</div>
    </Card>
  );
}

function DriverSupplyCard({ data }) {
  if (!data) return <Card title="Driver Registration Intent"><LoadingState /></Card>;

  const driverData = data.driver_supply?.data || [];
  const terms = data.driver_supply?.terms || [];

  // Aggregate weekly data into monthly averages to avoid duplicate x-axis keys
  const monthly = {};
  driverData.forEach((d) => {
    const month = d.date?.slice(0, 7);
    if (!month) return;
    if (!monthly[month]) monthly[month] = { count: 0 };
    monthly[month].count++;
    terms.forEach((t) => {
      monthly[month][t] = (monthly[month][t] || 0) + (d[t] || 0);
    });
  });
  const chartData = Object.entries(monthly).map(([month, vals]) => {
    const point = { date: month };
    terms.forEach((t) => { point[t] = Math.round((vals[t] || 0) / vals.count); });
    return point;
  });

  const colors = [
    "rgba(47,109,85,0.9)",
    "rgba(196,156,84,0.85)",
    "rgba(80,60,140,0.75)",
    "rgba(180,80,80,0.75)",
  ];

  return (
    <Card
      title={<span>Driver Registration Intent <span className="muted">(Supply)</span></span>}
      right={<span className="kpiTinyUp"><ArrowUpRight size={14} /> Supply</span>}
    >
      <div className="miniChart">
        <ResponsiveContainer width="100%" height={160}>
          <LineChart data={chartData} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="4 10" opacity={0.25} />
            <XAxis dataKey="date" hide />
            <YAxis hide />
            <Tooltip content={<SoftTooltip />} />
            {terms.map((t, i) => (
              <Line key={t} type="monotone" dataKey={t} name={t} stroke={colors[i % colors.length]} strokeWidth={2} dot={false} />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
      <div className="muted miniFoot">"Register as driver" search volume · 12 months</div>
    </Card>
  );
}

function MethodologyCard({ data }) {
  if (!data) return null;
  const m = data.methodology || {};
  return (
    <Card title="Methodology" icon={<Database size={18} />} className="methodCard">
      <div className="methodGrid">
        <div className="methodItem">
          <div className="methodItemIcon"><Database size={16} /></div>
          <div>
            <div className="methodItemTitle">Anchor</div>
            <div className="methodItemDesc">{m.anchor}</div>
          </div>
        </div>
        <div className="methodItem">
          <div className="methodItemIcon"><Smartphone size={16} /></div>
          <div>
            <div className="methodItemTitle">Scaling</div>
            <div className="methodItemDesc">{m.scaling}</div>
          </div>
        </div>
        <div className="methodItem">
          <div className="methodItemIcon"><Users size={16} /></div>
          <div>
            <div className="methodItemTitle">Overlap</div>
            <div className="methodItemDesc">{m.overlap}</div>
          </div>
        </div>
        <div className="methodItem">
          <div className="methodItemIcon"><Search size={16} /></div>
          <div>
            <div className="methodItemTitle">Validation</div>
            <div className="methodItemDesc">{m.validation}</div>
          </div>
        </div>
      </div>
    </Card>
  );
}

function MLExplainCard({ data }) {
  if (!data)
    return (
      <Card title="Next-Quarter Workforce Forecast" className="bigCard">
        <LoadingState />
      </Card>
    );
  if (data.error)
    return (
      <Card title="ML Forecast" className="bigCard">
        <div className="muted">{data.error}</div>
      </Card>
    );

  const perf = data.performance || {};
  const features = data.feature_importance || [];
  const forecast = data.next_quarter_forecast || {};
  const breakdown = forecast.shap_breakdown || [];
  const validation = data.validation_results || [];

  return (
    <Card
      title={
        <span>
          Next-Quarter Workforce Forecast{" "}
          <span className="muted">(XGBoost + SHAP)</span>
        </span>
      }
      icon={<Brain size={18} />}
      right={
        <span className="mlPerfBadge">
          <Activity size={14} />
          MAPE {perf.mape_pct}%
        </span>
      }
      className="bigCard"
    >
      {/* Forecast headline */}
      <div className="mlForecastBanner">
        <div className="mlForecastFrom">
          <span className="muted">Based on</span>
          <span>{forecast.input_quarter?.replace("_", " ")}</span>
        </div>
        <div className="mlForecastArrow">→</div>
        <div className="mlForecastTo">
          <span className="muted">Forecast for</span>
          <span className="mlForecastValue">
            {forecast.forecast_quarter?.replace("_", " ")}:{" "}
            {forecast.predicted_workers?.toLocaleString()} workers
          </span>
        </div>
      </div>

      <div className="mlGrid">
        {/* Feature Importance */}
        <div className="mlSection">
          <div className="mlSectionTitle">Which signals best predict next quarter? (SHAP)</div>
          <div className="mlBarList">
            {features.map((f) => (
              <div className="mlBarRow" key={f.feature}>
                <div className="mlBarLabel">{f.label}</div>
                <div className="mlBarTrack">
                  <div
                    className="mlBarFill"
                    style={{ width: `${Math.min(f.importance_pct, 100)}%` }}
                  />
                </div>
                <div className="mlBarVal">{f.importance_pct}%</div>
              </div>
            ))}
          </div>
        </div>

        {/* Forecast SHAP Breakdown */}
        <div className="mlSection">
          <div className="mlSectionTitle">
            Why {forecast.forecast_quarter?.replace("_", " ")}?
          </div>
          <div className="shapWaterfall">
            <div className="shapBase">
              <span className="muted">Avg workforce (base)</span>
              <span className="shapBaseVal">
                {forecast.base_value?.toLocaleString()}
              </span>
            </div>
            {breakdown.map((b) => (
              <div
                className={`shapRow shapRow-${b.direction}`}
                key={b.feature}
              >
                <div className="shapLabel">{b.label}</div>
                <div className="shapArrow">
                  {b.direction === "positive" ? "+" : ""}
                  {b.shap_value?.toLocaleString()}
                </div>
                <div className="shapFeatureVal muted">{b.feature_value}</div>
              </div>
            ))}
            <div className="shapResult">
              <span className="muted">Forecast</span>
              <span className="shapResultVal">
                {forecast.predicted_workers?.toLocaleString()}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Expanding window validation chart */}
      <div className="mlAccuracy">
        <div className="mlSectionTitle">Backtest: How well did it predict past quarters?</div>
        <div className="miniChart">
          <ResponsiveContainer width="100%" height={180}>
            <ComposedChart
              data={validation.map((d) => ({
                q: d.quarter.replace("_", " "),
                actual: d.actual,
                predicted: d.predicted,
              }))}
              margin={{ top: 8, right: 8, left: 0, bottom: 0 }}
            >
              <CartesianGrid strokeDasharray="4 10" opacity={0.25} />
              <XAxis dataKey="q" tickMargin={8} fontSize={11} />
              <YAxis tickMargin={8} fontSize={11} />
              <Tooltip content={<SoftTooltip />} />
              <Bar
                dataKey="actual"
                name="Actual"
                fill="rgba(47,109,85,0.25)"
                radius={[4, 4, 0, 0]}
              />
              <Line
                type="monotone"
                dataKey="predicted"
                name="Predicted (1Q ahead)"
                stroke="rgba(196,156,84,0.9)"
                strokeWidth={2.5}
                dot={{ fill: "rgba(196,156,84,0.9)", r: 3 }}
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>
        <div className="mlPerfRow">
          <div className="mlPerfItem">
            <span className="muted">Validation</span>
            <span>{perf.validation}</span>
          </div>
          <div className="mlPerfItem">
            <span className="muted">MAE</span>
            <span>±{perf.mae?.toLocaleString()} workers</span>
          </div>
          <div className="mlPerfItem">
            <span className="muted">Training</span>
            <span>{data.n_samples} quarter pairs</span>
          </div>
        </div>
      </div>
    </Card>
  );
}

export default function App() {
  const { data: summary } = useApi("/summary");
  const { data: timeseries } = useApi("/timeseries");
  const { data: triangulation } = useApi("/triangulation");
  const { data: platforms } = useApi("/platforms");
  const { data: trends } = useApi("/trends");
  const { data: ml } = useApi("/ml");

  return (
    <div className="page">
      <Header />
      <KpiRow data={summary} />
      <div className="grid2">
        <WorkforceChart data={timeseries} />
        <TriangulationChart data={triangulation} />
      </div>
      <div className="grid3">
        <PlatformBreakdown data={platforms} />
        <TrendsCard data={trends} />
        <DriverSupplyCard data={trends} />
      </div>
      <MLExplainCard data={ml} />
      <MethodologyCard data={summary} />
    </div>
  );
}
