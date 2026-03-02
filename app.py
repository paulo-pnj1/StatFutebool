import { useState, useCallback } from "react";

const API_KEY_PLACEHOLDER = "YOUR_API_KEY";

const COMPETITIONS = {
  "Premier League": 2021,
  "La Liga": 2014,
  "Serie A": 2019,
  "Bundesliga": 2002,
  "Ligue 1": 2015,
  "Champions League": 2001,
  "Europa League": 2146,
};

const MARKET_LABELS = {
  btts: "BTTS",
  over25: "Over 2.5",
  over15: "Over 1.5",
  under35: "Under 3.5",
  under25: "Under 2.5",
  secondHalf: "2º Tempo +Gols",
};

const MARKET_ICONS = {
  btts: "⚽",
  over25: "🔥",
  over15: "✅",
  under35: "🛡️",
  under25: "🔒",
  secondHalf: "⏱️",
};

function GaugeBar({ value, label, icon, fairOdd }) {
  const color =
    value >= 65 ? "#22c55e" : value >= 50 ? "#f59e0b" : "#ef4444";
  const bg =
    value >= 65
      ? "rgba(34,197,94,0.12)"
      : value >= 50
      ? "rgba(245,158,11,0.12)"
      : "rgba(239,68,68,0.12)";
  return (
    <div
      style={{
        background: bg,
        border: `1px solid ${color}40`,
        borderRadius: 14,
        padding: "14px 16px",
        display: "flex",
        flexDirection: "column",
        gap: 8,
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <span style={{ fontSize: 13, fontWeight: 700, color: "#e2e8f0" }}>
          {icon} {label}
        </span>
        <span style={{ fontSize: 22, fontWeight: 900, color }}>
          {value}%
        </span>
      </div>
      <div
        style={{
          background: "rgba(255,255,255,0.08)",
          borderRadius: 99,
          height: 8,
          overflow: "hidden",
        }}
      >
        <div
          style={{
            width: `${value}%`,
            height: "100%",
            background: color,
            borderRadius: 99,
            transition: "width 0.8s cubic-bezier(.4,0,.2,1)",
          }}
        />
      </div>
      <div style={{ fontSize: 11, color: "#94a3b8" }}>
        Odd Justa: <b style={{ color: "#e2e8f0" }}>{fairOdd}</b>
      </div>
    </div>
  );
}

function ValueCalc({ prob, fairOdd, label, icon }) {
  const [realOdd, setRealOdd] = useState(fairOdd);
  const ev = realOdd ? ((realOdd * prob) / 100 - 1).toFixed(3) : null;
  const isValue = ev && parseFloat(ev) > 0.05;
  const isSmall = ev && parseFloat(ev) > 0 && parseFloat(ev) <= 0.05;
  return (
    <div
      style={{
        background: "rgba(255,255,255,0.04)",
        border: "1px solid rgba(255,255,255,0.08)",
        borderRadius: 12,
        padding: "12px 14px",
        display: "flex",
        flexDirection: "column",
        gap: 8,
      }}
    >
      <div style={{ fontSize: 13, fontWeight: 700, color: "#cbd5e1" }}>
        {icon} {label}
      </div>
      <input
        type="number"
        min="1.01"
        step="0.01"
        value={realOdd}
        onChange={(e) => setRealOdd(parseFloat(e.target.value))}
        style={{
          background: "rgba(255,255,255,0.06)",
          border: "1px solid rgba(255,255,255,0.15)",
          borderRadius: 8,
          padding: "6px 10px",
          color: "#f1f5f9",
          fontSize: 15,
          width: "100%",
          outline: "none",
        }}
      />
      {ev !== null && (
        <div
          style={{
            fontSize: 12,
            fontWeight: 700,
            color: isValue ? "#22c55e" : isSmall ? "#f59e0b" : "#ef4444",
          }}
        >
          EV: {ev}{" "}
          {isValue ? "✅ VALUE!" : isSmall ? "⚠️ Pequeno" : "❌ Sem value"}
        </div>
      )}
    </div>
  );
}

function TeamCard({ name, profile, side }) {
  const styleColor =
    profile.estilo === "ofensivo"
      ? "#f59e0b"
      : profile.estilo === "defensivo"
      ? "#3b82f6"
      : "#8b5cf6";
  return (
    <div
      style={{
        background: "rgba(255,255,255,0.04)",
        border: "1px solid rgba(255,255,255,0.08)",
        borderRadius: 14,
        padding: 18,
        display: "flex",
        flexDirection: "column",
        gap: 10,
      }}
    >
      <div
        style={{
          fontSize: 14,
          fontWeight: 800,
          color: "#f1f5f9",
          display: "flex",
          alignItems: "center",
          gap: 8,
        }}
      >
        <span>{side === "home" ? "🏠" : "✈️"}</span>
        <span>{name}</span>
        <span
          style={{
            marginLeft: "auto",
            background: `${styleColor}22`,
            color: styleColor,
            fontSize: 10,
            fontWeight: 700,
            padding: "2px 8px",
            borderRadius: 99,
            border: `1px solid ${styleColor}55`,
            textTransform: "uppercase",
          }}
        >
          {profile.estilo}
        </span>
      </div>
      <div style={{ display: "flex", gap: 8 }}>
        {[
          { label: "Ataque", val: profile.ataque, color: "#f59e0b" },
          { label: "Defesa", val: profile.defesa, color: "#3b82f6" },
        ].map(({ label, val, color }) => (
          <div
            key={label}
            style={{
              flex: 1,
              background: "rgba(255,255,255,0.04)",
              borderRadius: 8,
              padding: "6px 10px",
            }}
          >
            <div style={{ fontSize: 10, color: "#94a3b8", marginBottom: 4 }}>
              {label}
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
              <div
                style={{
                  flex: 1,
                  background: "rgba(255,255,255,0.08)",
                  borderRadius: 99,
                  height: 6,
                }}
              >
                <div
                  style={{
                    width: `${(val / 10) * 100}%`,
                    height: "100%",
                    background: color,
                    borderRadius: 99,
                  }}
                />
              </div>
              <span style={{ fontSize: 12, fontWeight: 700, color }}>
                {val}/10
              </span>
            </div>
          </div>
        ))}
      </div>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: 6,
          fontSize: 11,
          color: "#94a3b8",
        }}
      >
        {[
          ["⚽ BTTS", profile.btts + "%"],
          ["🔥 Over 2.5", profile.over25 + "%"],
          ["✅ Over 1.5", profile.over15 + "%"],
          ["🛡️ Under 3.5", profile.under35 + "%"],
        ].map(([k, v]) => (
          <div
            key={k}
            style={{
              display: "flex",
              justifyContent: "space-between",
              background: "rgba(255,255,255,0.03)",
              borderRadius: 6,
              padding: "4px 8px",
            }}
          >
            <span>{k}</span>
            <span style={{ color: "#e2e8f0", fontWeight: 600 }}>{v}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function HistoryRow({ item, i }) {
  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        gap: 12,
        padding: "10px 14px",
        background: i % 2 === 0 ? "rgba(255,255,255,0.03)" : "transparent",
        borderRadius: 8,
        fontSize: 13,
      }}
    >
      <span style={{ color: "#64748b", fontSize: 11, minWidth: 100 }}>
        {item.data}
      </span>
      <span style={{ flex: 1, color: "#e2e8f0", fontWeight: 600 }}>
        {item.home} vs {item.away}
      </span>
      <span
        style={{
          background: "rgba(34,197,94,0.15)",
          color: "#22c55e",
          padding: "2px 8px",
          borderRadius: 6,
          fontSize: 11,
        }}
      >
        BTTS {item.prob_btts}%
      </span>
      <span
        style={{
          background: "rgba(239,120,30,0.15)",
          color: "#f59e0b",
          padding: "2px 8px",
          borderRadius: 6,
          fontSize: 11,
        }}
      >
        O2.5 {item.prob_over25}%
      </span>
    </div>
  );
}

// ---------- CORE ANALYSIS LOGIC ----------
function buildProfile(standingsData, matchesData, teamId) {
  const profile = {
    ataque: 5,
    defesa: 5,
    estilo: "equilibrado",
    btts: 50,
    over25: 50,
    over15: 70,
    under35: 70,
    under25: 50,
    secondHalf: 50,
  };

  if (standingsData?.standings) {
    for (const group of standingsData.standings) {
      for (const entry of group.table) {
        if (entry.team.id === teamId && entry.playedGames > 0) {
          const avgScored = entry.goalsFor / entry.playedGames;
          const avgConceded = entry.goalsAgainst / entry.playedGames;
          profile.ataque = Math.min(10, Math.max(1, Math.round((avgScored / 1.4) * 7 + 1)));
          profile.defesa = Math.min(10, Math.max(1, Math.round((1.4 / Math.max(avgConceded, 0.1)) * 7 + 1)));
        }
      }
    }
  }

  if (matchesData?.matches?.length) {
    const recent = matchesData.matches.slice(0, 10);
    const n = recent.length;
    const totalGoals = (m) =>
      (m.score.fullTime.home || 0) + (m.score.fullTime.away || 0);
    const hg = (m) => m.score.fullTime.home || 0;
    const ag = (m) => m.score.fullTime.away || 0;
    const firstHalf = (m) =>
      (m.score.halfTime?.home || 0) + (m.score.halfTime?.away || 0);

    profile.btts = Math.round((recent.filter((m) => hg(m) > 0 && ag(m) > 0).length / n) * 100);
    profile.over25 = Math.round((recent.filter((m) => totalGoals(m) > 2.5).length / n) * 100);
    profile.over15 = Math.round((recent.filter((m) => totalGoals(m) > 1.5).length / n) * 100);
    profile.under35 = Math.round((recent.filter((m) => totalGoals(m) < 3.5).length / n) * 100);
    profile.under25 = Math.round((recent.filter((m) => totalGoals(m) < 2.5).length / n) * 100);
    profile.secondHalf = Math.round(
      (recent.filter((m) => totalGoals(m) - firstHalf(m) > firstHalf(m)).length / n) * 100
    );
  }

  const { ataque, defesa } = profile;
  profile.estilo =
    ataque >= 7 && defesa <= 6 ? "ofensivo" : defesa >= 7 && ataque <= 6 ? "defensivo" : "equilibrado";

  return profile;
}

function computeAnalysis(homeProfile, awayProfile, h2h, competition) {
  const base = (a, b) => (a + b) / 2;
  let btts = base(homeProfile.btts, awayProfile.btts);
  let over25 = base(homeProfile.over25, awayProfile.over25);
  let over15 = base(homeProfile.over15, awayProfile.over15);
  let under35 = base(homeProfile.under35, awayProfile.under35);
  let under25 = base(homeProfile.under25, awayProfile.under25);
  let secondHalf = base(homeProfile.secondHalf, awayProfile.secondHalf);

  // Style adjustments
  const styles = [homeProfile.estilo, awayProfile.estilo].sort().join("+");
  if (styles === "ofensivo+ofensivo") {
    btts += 8; over25 += 12; over15 += 5; under35 -= 10; under25 -= 8; secondHalf += 5;
  } else if (styles === "defensivo+defensivo") {
    btts -= 10; over25 -= 15; over15 -= 5; under35 += 12; under25 += 10; secondHalf -= 5;
  }

  // Competition adjustments
  if (competition.includes("Premier")) { over25 += 5; over15 += 3; }
  else if (competition.includes("Serie")) { btts -= 3; over25 -= 2; under35 += 4; }
  else if (competition.includes("Bundesliga")) { btts += 5; over25 += 8; over15 += 5; }

  // H2H
  btts += (h2h.btts - 50) / 10;
  over25 += (h2h.over25 - 50) / 10;

  const clamp = (v, lo, hi) => Math.round(Math.min(hi, Math.max(lo, v)) * 10) / 10;

  return {
    btts: clamp(btts, 15, 85),
    over25: clamp(over25, 20, 80),
    over15: clamp(over15, 40, 95),
    under35: clamp(under35, 30, 90),
    under25: clamp(under25, 25, 85),
    secondHalf: clamp(secondHalf, 20, 80),
  };
}

// ---------- MAIN APP ----------
export default function App() {
  const [apiKey, setApiKey] = useState("");
  const [apiKeyInput, setApiKeyInput] = useState("");
  const [competition, setCompetition] = useState("Premier League");
  const [matches, setMatches] = useState([]);
  const [selectedMatch, setSelectedMatch] = useState(null);
  const [selectedMarkets, setSelectedMarkets] = useState(["btts", "over25", "over15", "under35"]);
  const [analysis, setAnalysis] = useState(null);
  const [profiles, setProfiles] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingMatches, setLoadingMatches] = useState(false);
  const [error, setError] = useState("");
  const [tab, setTab] = useState("analysis");

  const headers = { "X-Auth-Token": apiKey };

  const fetchMatches = useCallback(async (compName) => {
    if (!apiKey) return;
    setLoadingMatches(true);
    setError("");
    setMatches([]);
    setSelectedMatch(null);
    setAnalysis(null);
    try {
      const compId = COMPETITIONS[compName];
      const today = new Date().toISOString().split("T")[0];
      const next = new Date(Date.now() + 7 * 86400000).toISOString().split("T")[0];
      const res = await fetch(
        `https://api.football-data.org/v4/competitions/${compId}/matches?dateFrom=${today}&dateTo=${next}`,
        { headers }
      );
      const data = await res.json();
      const upcoming = (data.matches || []).filter((m) =>
        ["SCHEDULED", "TIMED"].includes(m.status)
      );
      setMatches(upcoming);
      if (!upcoming.length) setError("Nenhuma partida encontrada para os próximos 7 dias.");
    } catch {
      setError("Erro ao buscar partidas. Verifique sua API key.");
    }
    setLoadingMatches(false);
  }, [apiKey]);

  const runAnalysis = async () => {
    if (!selectedMatch) return;
    setLoading(true);
    setError("");
    setAnalysis(null);
    setProfiles(null);
    try {
      const compId = COMPETITIONS[competition];
      const { home_id, away_id, home_team, away_team } = selectedMatch;

      const [standH, matchH, standA, matchA, recentHome] = await Promise.all([
        fetch(`https://api.football-data.org/v4/competitions/${compId}/standings`, { headers }).then((r) => r.json()),
        fetch(`https://api.football-data.org/v4/teams/${home_id}/matches?status=FINISHED&limit=10`, { headers }).then((r) => r.json()),
        fetch(`https://api.football-data.org/v4/competitions/${compId}/standings`, { headers }).then((r) => r.json()),
        fetch(`https://api.football-data.org/v4/teams/${away_id}/matches?status=FINISHED&limit=10`, { headers }).then((r) => r.json()),
        fetch(`https://api.football-data.org/v4/teams/${home_id}/matches?status=FINISHED&limit=20`, { headers }).then((r) => r.json()),
      ]);

      const homeProfile = buildProfile(standH, matchH, home_id);
      const awayProfile = buildProfile(standA, matchA, away_id);

      // H2H
      const h2hMatches = (recentHome.matches || []).filter(
        (m) => m.awayTeam?.id === away_id || m.homeTeam?.id === away_id
      ).slice(0, 5);
      const n = Math.max(h2hMatches.length, 1);
      const tg = (m) => (m.score.fullTime.home || 0) + (m.score.fullTime.away || 0);
      const h2h = {
        btts: Math.round((h2hMatches.filter((m) => (m.score.fullTime.home || 0) > 0 && (m.score.fullTime.away || 0) > 0).length / n) * 100),
        over25: Math.round((h2hMatches.filter((m) => tg(m) > 2.5).length / n) * 100),
      };

      const probs = computeAnalysis(homeProfile, awayProfile, h2h, competition);

      const result = {
        probs,
        fairOdds: Object.fromEntries(
          Object.entries(probs).map(([k, v]) => [k, (100 / v).toFixed(2)])
        ),
        homeProfile,
        awayProfile,
        h2h,
        h2hCount: h2hMatches.length,
      };

      setAnalysis(result);
      setProfiles({ home: homeProfile, away: awayProfile });
      setHistory((prev) => [
        {
          home: home_team,
          away: away_team,
          prob_btts: probs.btts,
          prob_over25: probs.over25,
          data: new Date().toLocaleString("pt-BR"),
        },
        ...prev.slice(0, 49),
      ]);
    } catch (e) {
      setError("Erro na análise. Verifique sua API key e tente novamente.");
    }
    setLoading(false);
  };

  const toggleMarket = (m) =>
    setSelectedMarkets((prev) =>
      prev.includes(m) ? prev.filter((x) => x !== m) : [...prev, m]
    );

  const matchOptions = matches.map((m) => {
    const date = new Date(m.utcDate);
    return {
      id: m.id,
      home_id: m.homeTeam.id,
      away_id: m.awayTeam.id,
      home_team: m.homeTeam.name,
      away_team: m.awayTeam.name,
      display: `${m.homeTeam.name} vs ${m.awayTeam.name} — ${date.toLocaleDateString("pt-BR")} ${date.toLocaleTimeString("pt-BR", { hour: "2-digit", minute: "2-digit" })}`,
      date,
    };
  });

  const baseStyle = {
    fontFamily: "'DM Sans', 'Segoe UI', sans-serif",
    background: "#0b0f1a",
    minHeight: "100vh",
    color: "#e2e8f0",
    padding: 24,
  };

  const cardStyle = {
    background: "rgba(255,255,255,0.04)",
    border: "1px solid rgba(255,255,255,0.08)",
    borderRadius: 16,
    padding: 20,
  };

  const btnPrimary = {
    background: "linear-gradient(135deg, #3b82f6, #6366f1)",
    color: "#fff",
    border: "none",
    borderRadius: 10,
    padding: "12px 24px",
    fontSize: 14,
    fontWeight: 700,
    cursor: "pointer",
    width: "100%",
  };

  const inputStyle = {
    background: "rgba(255,255,255,0.06)",
    border: "1px solid rgba(255,255,255,0.12)",
    borderRadius: 10,
    padding: "10px 14px",
    color: "#f1f5f9",
    fontSize: 14,
    width: "100%",
    outline: "none",
    boxSizing: "border-box",
  };

  const selectStyle = { ...inputStyle, cursor: "pointer" };

  // API Key gate
  if (!apiKey) {
    return (
      <div style={{ ...baseStyle, display: "flex", alignItems: "center", justifyContent: "center" }}>
        <div style={{ ...cardStyle, maxWidth: 420, width: "100%", textAlign: "center" }}>
          <div style={{ fontSize: 48, marginBottom: 12 }}>⚽</div>
          <h1 style={{ fontSize: 22, fontWeight: 900, marginBottom: 4, color: "#f1f5f9" }}>
            Analisador de Apostas
          </h1>
          <p style={{ color: "#64748b", fontSize: 13, marginBottom: 24 }}>
            Insira sua chave da{" "}
            <a
              href="https://www.football-data.org/"
              target="_blank"
              rel="noreferrer"
              style={{ color: "#3b82f6" }}
            >
              football-data.org
            </a>{" "}
            para começar (gratuita)
          </p>
          <input
            type="text"
            placeholder="Cole sua API Key aqui..."
            value={apiKeyInput}
            onChange={(e) => setApiKeyInput(e.target.value)}
            style={{ ...inputStyle, marginBottom: 12 }}
          />
          <button
            style={btnPrimary}
            onClick={() => {
              if (apiKeyInput.trim()) setApiKey(apiKeyInput.trim());
            }}
          >
            Entrar →
          </button>
          <p style={{ color: "#475569", fontSize: 11, marginTop: 12 }}>
            A chave é usada apenas nesta sessão e não é salva.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div style={baseStyle}>
      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 24 }}>
        <div>
          <h1 style={{ fontSize: 20, fontWeight: 900, margin: 0, color: "#f1f5f9" }}>
            ⚽ Analisador de Apostas
          </h1>
          <p style={{ fontSize: 12, color: "#64748b", margin: 0 }}>
            Dados reais · Probabilidades · Value Bets
          </p>
        </div>
        <button
          onClick={() => setApiKey("")}
          style={{
            background: "rgba(239,68,68,0.12)",
            border: "1px solid rgba(239,68,68,0.3)",
            color: "#ef4444",
            borderRadius: 8,
            padding: "6px 14px",
            fontSize: 12,
            cursor: "pointer",
          }}
        >
          Sair
        </button>
      </div>

      {/* Tabs */}
      <div style={{ display: "flex", gap: 8, marginBottom: 20 }}>
        {[
          ["analysis", "🔍 Análise"],
          ["profiles", "👤 Perfis"],
          ["history", "📈 Histórico"],
        ].map(([key, label]) => (
          <button
            key={key}
            onClick={() => setTab(key)}
            style={{
              padding: "8px 18px",
              borderRadius: 8,
              border: "1px solid",
              cursor: "pointer",
              fontSize: 13,
              fontWeight: 600,
              background: tab === key ? "rgba(59,130,246,0.2)" : "rgba(255,255,255,0.04)",
              borderColor: tab === key ? "#3b82f6" : "rgba(255,255,255,0.08)",
              color: tab === key ? "#93c5fd" : "#94a3b8",
            }}
          >
            {label}
          </button>
        ))}
      </div>

      {/* TAB: Analysis */}
      {tab === "analysis" && (
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          {/* Setup card */}
          <div style={cardStyle}>
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr 2fr",
                gap: 12,
                marginBottom: 16,
              }}
            >
              <div>
                <label style={{ fontSize: 12, color: "#94a3b8", display: "block", marginBottom: 6 }}>
                  Competição
                </label>
                <select
                  style={selectStyle}
                  value={competition}
                  onChange={(e) => {
                    setCompetition(e.target.value);
                    setMatches([]);
                    setSelectedMatch(null);
                    setAnalysis(null);
                  }}
                >
                  {Object.keys(COMPETITIONS).map((c) => (
                    <option key={c} value={c}>
                      {c}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label style={{ fontSize: 12, color: "#94a3b8", display: "block", marginBottom: 6 }}>
                  Partida{" "}
                  {!matches.length && (
                    <span style={{ color: "#f59e0b" }}>— clique em "Buscar" primeiro</span>
                  )}
                </label>
                <div style={{ display: "flex", gap: 8 }}>
                  <select
                    style={{ ...selectStyle, flex: 1 }}
                    value={selectedMatch?.id || ""}
                    onChange={(e) =>
                      setSelectedMatch(matchOptions.find((m) => String(m.id) === e.target.value) || null)
                    }
                    disabled={!matchOptions.length}
                  >
                    <option value="">Selecione uma partida...</option>
                    {matchOptions.map((m) => (
                      <option key={m.id} value={m.id}>
                        {m.display}
                      </option>
                    ))}
                  </select>
                  <button
                    onClick={() => fetchMatches(competition)}
                    disabled={loadingMatches}
                    style={{
                      ...btnPrimary,
                      width: "auto",
                      padding: "10px 16px",
                      opacity: loadingMatches ? 0.6 : 1,
                      whiteSpace: "nowrap",
                    }}
                  >
                    {loadingMatches ? "⏳" : "Buscar"}
                  </button>
                </div>
              </div>
            </div>

            {/* Markets */}
            <div style={{ marginBottom: 16 }}>
              <label style={{ fontSize: 12, color: "#94a3b8", display: "block", marginBottom: 8 }}>
                Mercados Ativos
              </label>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                {Object.entries(MARKET_LABELS).map(([key, label]) => {
                  const active = selectedMarkets.includes(key);
                  return (
                    <button
                      key={key}
                      onClick={() => toggleMarket(key)}
                      style={{
                        padding: "6px 14px",
                        borderRadius: 8,
                        border: "1px solid",
                        cursor: "pointer",
                        fontSize: 12,
                        fontWeight: 600,
                        background: active ? "rgba(59,130,246,0.18)" : "rgba(255,255,255,0.04)",
                        borderColor: active ? "#3b82f6" : "rgba(255,255,255,0.08)",
                        color: active ? "#93c5fd" : "#64748b",
                      }}
                    >
                      {MARKET_ICONS[key]} {label}
                    </button>
                  );
                })}
              </div>
            </div>

            <button
              onClick={runAnalysis}
              disabled={!selectedMatch || loading}
              style={{ ...btnPrimary, opacity: !selectedMatch || loading ? 0.5 : 1 }}
            >
              {loading ? "⏳ Analisando..." : "🚀 Analisar Partida"}
            </button>
          </div>

          {error && (
            <div
              style={{
                background: "rgba(239,68,68,0.1)",
                border: "1px solid rgba(239,68,68,0.3)",
                borderRadius: 10,
                padding: "12px 16px",
                color: "#fca5a5",
                fontSize: 13,
              }}
            >
              ⚠️ {error}
            </div>
          )}

          {/* Results */}
          {analysis && selectedMatch && (
            <>
              <div style={{ ...cardStyle, borderColor: "rgba(59,130,246,0.3)" }}>
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    marginBottom: 16,
                  }}
                >
                  <div>
                    <div style={{ fontSize: 17, fontWeight: 800, color: "#f1f5f9" }}>
                      {selectedMatch.home_team} <span style={{ color: "#64748b" }}>vs</span>{" "}
                      {selectedMatch.away_team}
                    </div>
                    <div style={{ fontSize: 12, color: "#64748b" }}>
                      {competition} ·{" "}
                      {selectedMatch.date.toLocaleDateString("pt-BR")}{" "}
                      {selectedMatch.date.toLocaleTimeString("pt-BR", {
                        hour: "2-digit",
                        minute: "2-digit",
                      })}
                    </div>
                  </div>
                  <div
                    style={{
                      fontSize: 11,
                      color: "#94a3b8",
                      background: "rgba(255,255,255,0.05)",
                      borderRadius: 8,
                      padding: "4px 10px",
                    }}
                  >
                    H2H: {analysis.h2hCount} jogos
                  </div>
                </div>

                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))",
                    gap: 10,
                  }}
                >
                  {selectedMarkets.map((m) => (
                    <GaugeBar
                      key={m}
                      value={analysis.probs[m]}
                      label={MARKET_LABELS[m]}
                      icon={MARKET_ICONS[m]}
                      fairOdd={analysis.fairOdds[m]}
                    />
                  ))}
                </div>
              </div>

              {/* Recommendations */}
              <div style={cardStyle}>
                <div style={{ fontSize: 14, fontWeight: 700, color: "#e2e8f0", marginBottom: 12 }}>
                  🎯 Recomendações
                </div>
                <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                  {selectedMarkets.map((m) => {
                    const v = analysis.probs[m];
                    const strong = v >= 65;
                    const mod = v >= 50;
                    const color = strong ? "#22c55e" : mod ? "#f59e0b" : "#ef4444";
                    const bg = strong
                      ? "rgba(34,197,94,0.08)"
                      : mod
                      ? "rgba(245,158,11,0.08)"
                      : "rgba(239,68,68,0.08)";
                    const msg = strong
                      ? "FORTE candidato ✅"
                      : mod
                      ? "Candidato moderado ⚠️"
                      : "Probabilidade baixa ❌";
                    return (
                      <div
                        key={m}
                        style={{
                          display: "flex",
                          alignItems: "center",
                          gap: 10,
                          background: bg,
                          borderRadius: 8,
                          padding: "8px 12px",
                        }}
                      >
                        <span style={{ fontSize: 16 }}>{MARKET_ICONS[m]}</span>
                        <span style={{ fontSize: 13, fontWeight: 700, color: "#e2e8f0", flex: 1 }}>
                          {MARKET_LABELS[m]}
                        </span>
                        <span style={{ fontSize: 12, color }}>{msg}</span>
                        <span
                          style={{
                            fontSize: 13,
                            fontWeight: 700,
                            color,
                            minWidth: 44,
                            textAlign: "right",
                          }}
                        >
                          {v}%
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Value Calculator */}
              <div style={cardStyle}>
                <div style={{ fontSize: 14, fontWeight: 700, color: "#e2e8f0", marginBottom: 12 }}>
                  💰 Calculadora de Value Bet
                </div>
                <p style={{ fontSize: 12, color: "#64748b", marginBottom: 12 }}>
                  Insira a odd que você encontrou na casa de apostas:
                </p>
                <div
                  style={{
                    display: "grid",
                    gridTemplateColumns: "repeat(auto-fill, minmax(160px, 1fr))",
                    gap: 10,
                  }}
                >
                  {selectedMarkets.map((m) => (
                    <ValueCalc
                      key={m}
                      prob={analysis.probs[m]}
                      fairOdd={parseFloat(analysis.fairOdds[m])}
                      label={MARKET_LABELS[m]}
                      icon={MARKET_ICONS[m]}
                    />
                  ))}
                </div>
              </div>
            </>
          )}
        </div>
      )}

      {/* TAB: Profiles */}
      {tab === "profiles" && (
        <div>
          {profiles && selectedMatch ? (
            <>
              <div
                style={{
                  fontSize: 13,
                  color: "#64748b",
                  marginBottom: 16,
                  padding: "10px 14px",
                  background: "rgba(255,255,255,0.03)",
                  borderRadius: 10,
                }}
              >
                ℹ️ H2H: BTTS {analysis?.h2h?.btts ?? "?"}% · Over 2.5{" "}
                {analysis?.h2h?.over25 ?? "?"}% ({analysis?.h2hCount ?? 0} confrontos)
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
                <TeamCard name={selectedMatch.home_team} profile={profiles.home} side="home" />
                <TeamCard name={selectedMatch.away_team} profile={profiles.away} side="away" />
              </div>
            </>
          ) : (
            <div
              style={{
                ...cardStyle,
                textAlign: "center",
                padding: 40,
                color: "#64748b",
              }}
            >
              <div style={{ fontSize: 40, marginBottom: 12 }}>👤</div>
              Analise uma partida primeiro para ver os perfis dos times.
            </div>
          )}
        </div>
      )}

      {/* TAB: History */}
      {tab === "history" && (
        <div style={cardStyle}>
          <div style={{ fontSize: 14, fontWeight: 700, color: "#e2e8f0", marginBottom: 16 }}>
            📈 Histórico de Análises{" "}
            <span style={{ color: "#64748b", fontWeight: 400 }}>({history.length})</span>
          </div>
          {history.length ? (
            <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
              {history.map((item, i) => (
                <HistoryRow key={i} item={item} i={i} />
              ))}
            </div>
          ) : (
            <div style={{ textAlign: "center", color: "#64748b", padding: 40, fontSize: 13 }}>
              Nenhuma análise ainda. Vá para a aba Análise e analise uma partida.
            </div>
          )}
        </div>
      )}
    </div>
  );
}
