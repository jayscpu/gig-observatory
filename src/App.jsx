import React from "react";
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
} from "recharts";
import {
  Users,
  TrendingUp,
  Layers,
  BarChart3,
  Info,
  ChevronDown,
  Scale,
} from "lucide-react";
import "./app.css";

const kpi = {
  workers: { value: "90k", range: "Range: 75k → 105k" },
  growth: { value: "+18%", sub: "0.8% • Last update: 2026-03-05" },
  coverage: {
    platformsTracked: 4,
    platforms: ["Jahez", "HungerStation", "Mrsool", "Chefz"],
    lastUpdate: "2026-03-05",
  },
  gap: { value: "+55k", label: "Estimated — Official" },
};

// Time series (Estimated Gig Workforce)
const workforceSeries = [
  { q: "Q2 2025", base: 56, low: 50, high: 62 },
  { q: "Q3 2025", base: 58, low: 52, high: 65 },
  { q: "Q4 2025", base: 60, low: 54, high: 68 },
  { q: "Q1 2026", base: 63, low: 57, high: 72 },
  { q: "Q2 2026", base: 67, low: 61, high: 77 },
  { q: "Q3 2026", base: 70, low: 64, high: 80 },
  { q: "Q4 2026", base: 74, low: 68, high: 84 },
  { q: "Q1 2027", base: 78, low: 71, high: 87 },
  { q: "Q2 2027", base: 85, low: 77, high: 90 },
];

// Triangulated (bars)
const triangulated = [
  { name: "Financial\nProxy", value: 95 },
  { name: "App Ecosystem\nEstimate", value: 80 },
  { name: "Recruitment\nSignal", value: 85 },
  { name: "Final\nEstimate", value: 90 },
];

// App Store Activity (mini line)
const appStore = [
  { m: "Mar 2025", v: 3.0 },
  { m: "May 2025", v: 3.4 },
  { m: "Aug 2025", v: 4.1 },
  { m: "Jan 2026", v: 5.0 },
  { m: "Feb 2026", v: 6.4 },
];

// Search interest (horizontal bars)
const searchInterest = [
  { platform: "Jahez", score: 67 },
  { platform: "HungerStation", score: 54 },
  { platform: "Mrsool", score: 38 },
  { platform: "Chefz", score: 22 },
];

// Platform comparison (workers)
const platformComparison = [
  { platform: "Jahez", min: 22, max: 95 },
  { platform: "HungerStation", min: 23, max: 35 },
  { platform: "Mrsool", min: 15, max: 25 },
  { platform: "Chefz", min: 10, max: 16 },
];

function SoftTooltip({ active, payload, label }) {
  if (!active || !payload || !payload.length) return null;
  return (
    <div className="tooltip">
      <div className="tooltipTitle">{label}</div>
      {payload.map((p) => (
        <div key={p.dataKey} className="tooltipRow">
          <span className="dot" />
          <span className="tooltipKey">{p.name ?? p.dataKey}</span>
          <span className="tooltipVal">{p.value}</span>
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

function Header() {
  return (
    <div className="header">
      <div className="brand">
        <div className="brandMark">
          <Users size={18} />
        </div>
        <div className="brandText">
          <div className="brandTitle">Gig Economy</div>
          <div className="brandSub">Data Observatory</div>
        </div>
      </div>

      <div className="headerControls">
        <button className="ghostBtn" type="button">
          <span className="ghostLeft">
            <Info size={16} />
          </span>
          <span>02 hours</span>
          <ChevronDown size={16} />
        </button>
        <button className="ghostBtn" type="button">
          <span>7 days</span>
          <span className="arabic">لبياناتنا</span>
          <ChevronDown size={16} />
        </button>
      </div>
    </div>
  );
}

function KpiRow() {
  return (
    <div className="kpiGrid">
      <Card
        title="Estimated Gig Workers"
        icon={<Users size={18} />}
        right={<span className="muted"> </span>}
      >
        <div className="kpiMain">
          <div className="kpiValue">{kpi.workers.value}</div>
          <div className="kpiSub">
            <Pill muted>{kpi.workers.range}</Pill>
          </div>
        </div>
      </Card>

      <Card title="Growth Rate" icon={<TrendingUp size={18} />}>
        <div className="kpiMain">
          <div className="kpiValue kpiPositive">{kpi.growth.value}</div>
          <div className="kpiSub">
            <Pill muted>{kpi.growth.sub}</Pill>
          </div>
        </div>
      </Card>

      <Card title="Coverage" icon={<Layers size={18} />}>
        <div className="coverage">
          <div className="coverageRow">
            <div className="coverageKey">Platforms Tracked:</div>
            <div className="coverageVal">{kpi.coverage.platformsTracked}</div>
          </div>

          <div className="coverageList">
            {kpi.coverage.platforms.map((p) => (
              <span className="chip" key={p}>
                {p}
              </span>
            ))}
          </div>

          <div className="coverageMeta">
            <span className="muted">Last update:</span>{" "}
            <span>{kpi.coverage.lastUpdate}</span>
          </div>
        </div>
      </Card>

      <Card title="Estimated Gap" icon={<BarChart3 size={18} />}>
        <div className="gap">
          <div className="gapTop">
            <div className="kpiValue kpiPositive">{kpi.gap.value}</div>
            <div className="gapBadges">
              <span className="badgeGold">{kpi.gap.value}</span>
              <span className="badgeGold">{kpi.gap.value}</span>
              <span className="badgeGold">{kpi.gap.value}</span>
            </div>
          </div>
          <div className="muted">{kpi.gap.label}</div>
        </div>
      </Card>
    </div>
  );
}

function WorkforceChart() {
  return (
    <Card
      title={
        <span>
          Estimated Gig Workforce <span className="muted">(Unique Workers)</span>
        </span>
      }
      right={
        <span className="legendHint">
          <span className="legendDot" /> Estimate
        </span>
      }
      className="bigCard"
    >
      <div className="chartWrap">
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={workforceSeries} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="hiFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="10%" stopOpacity={0.22} />
                <stop offset="95%" stopOpacity={0.02} />
              </linearGradient>
              <linearGradient id="midFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="10%" stopOpacity={0.18} />
                <stop offset="95%" stopOpacity={0.02} />
              </linearGradient>
            </defs>

            <CartesianGrid strokeDasharray="4 10" opacity={0.35} />
            <XAxis dataKey="q" tickMargin={10} />
            <YAxis tickMargin={10} domain={[45, 95]} />
            <Tooltip content={<SoftTooltip />} />

            {/* High band */}
            <Area
              type="monotone"
              dataKey="high"
              name="High Estimate"
              strokeOpacity={0}
              fill="url(#hiFill)"
            />
            {/* Low band */}
            <Area
              type="monotone"
              dataKey="low"
              name="Low Estimate"
              strokeOpacity={0}
              fillOpacity={0}
              fill="transparent"
            />

            {/* Base estimate line */}
            <Line
              type="monotone"
              dataKey="base"
              name="Base Estimate"
              strokeWidth={3}
              dot={false}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="chartLegendRow">
        <div className="legendItem">
          <span className="legendSwatch swatchLine" /> Base Estimate
        </div>
        <div className="legendItem">
          <span className="legendSwatch swatchBand" /> High Estimate
        </div>
        <div className="legendItem">
          <span className="legendSwatch swatchDash" /> Low Estimate
        </div>
      </div>
    </Card>
  );
}

function TriangulatedChart() {
  return (
    <Card
      title="Triangulated Workforce Estimate"
      right={
        <span className="muted">
          <Scale size={16} style={{ verticalAlign: "middle" }} />{" "}
        </span>
      }
      className="bigCard"
    >
      <div className="chartWrap">
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={triangulated} margin={{ top: 10, right: 10, left: 10, bottom: 10 }}>
            <CartesianGrid strokeDasharray="4 10" opacity={0.35} />
            <XAxis dataKey="name" tickMargin={12} />
            <YAxis domain={[70, 100]} />
            <Tooltip content={<SoftTooltip />} />
            <Bar dataKey="value" radius={[14, 14, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="formula">
        <span className="muted">FinalEstimate</span> = (Estimate1 + Estimate2 +
        Estimate3) / 3
      </div>
    </Card>
  );
}

function AppStoreCard() {
  return (
    <Card
      title={
        <span>
          App Store Activity <span className="muted">(Jahez)</span>
        </span>
      }
      right={<span className="kpiTinyUp">+17.6% ↑</span>}
    >
      <div className="miniMeta muted">Reviews per month</div>
      <div className="miniChart">
        <ResponsiveContainer width="100%" height={140}>
          <LineChart data={appStore} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="4 10" opacity={0.25} />
            <XAxis dataKey="m" hide />
            <YAxis hide domain={[2.5, 7]} />
            <Tooltip content={<SoftTooltip />} />
            <Line type="monotone" dataKey="v" strokeWidth={3} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="storeBadges">
        <span className="chip soft">Google Play</span>
        <span className="chip soft">App Store</span>
        <span className="chip soft">Chefz</span>
      </div>
    </Card>
  );
}

function SearchInterestCard() {
  return (
    <Card
      title={
        <span>
          Search Interest <span className="muted">(Google Trends)</span>
        </span>
      }
      right={<span className="kpiTinyUp">+24% ↑</span>}
    >
      <div className="hbarList">
        {searchInterest.map((r) => (
          <div className="hbarRow" key={r.platform}>
            <div className="hbarLabel">{r.platform}</div>
            <div className="hbarTrack">
              <div className="hbarFill" style={{ width: `${r.score}%` }} />
            </div>
            <div className="hbarVal muted">{r.score}</div>
          </div>
        ))}
      </div>
      <div className="muted miniFoot">Mar 2025 → Feb 2026</div>
    </Card>
  );
}

function PlatformComparisonCard() {
  return (
    <Card
      title={
        <span>
          Platform Comparison <span className="muted">(Workers)</span>
        </span>
      }
      right={<span className="kpiTinyUp">+20.9% ↑</span>}
    >
      <div className="rangeList">
        {platformComparison.map((p) => {
          const span = Math.max(1, p.max - p.min);
          const left = (p.min / 100) * 100;
          const width = (span / 100) * 100;
          return (
            <div className="rangeRow" key={p.platform}>
              <div className="rangeLabel">{p.platform}</div>
              <div className="rangeTrack">
                <div
                  className="rangeFill"
                  style={{ marginLeft: `${left}%`, width: `${width}%` }}
                />
              </div>
              <div className="rangeVal muted">
                {p.min}–{p.max}k
              </div>
            </div>
          );
        })}
      </div>
      <div className="muted miniFoot">Mar 2025 → Feb 2026</div>
    </Card>
  );
}

export default function App() {
  return (
    <div className="page">
      <Header />
      <KpiRow />

      <div className="grid2">
        <WorkforceChart />
        <TriangulatedChart />
      </div>

      <div className="grid3">
        <AppStoreCard />
        <SearchInterestCard />
        <PlatformComparisonCard />
      </div>
    </div>
  );
}