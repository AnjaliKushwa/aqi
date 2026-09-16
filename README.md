import { useMemo, useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card } from "@/components/ui/card";
import { estimateAqi, getCategory, subAqi } from "@/lib/aqi.js";
import { Wind, Activity, Sparkles, Gauge, RotateCcw, BarChart3, Search, MapPin, Building2 } from "lucide-react";
import {
  BarChart, Bar, LabelList, XAxis, YAxis,
  CartesianGrid, Tooltip, ResponsiveContainer, Cell,
} from "recharts";

function computeContributions(p) {
  return [
    { name: "PM2.5", value: subAqi("pm25", Number(p.pm25) || 0) },
    { name: "PM10", value: subAqi("pm10", Number(p.pm10) || 0) },
    { name: "NO₂", value: subAqi("no2", Number(p.no2) || 0) },
    { name: "SO₂", value: subAqi("so2", Number(p.so2) || 0) },
    { name: "CO", value: subAqi("co", Number(p.co) || 0) },
    { name: "O₃", value: subAqi("o3", Number(p.o3) || 0) },
  ];
}

function ContributionChart({ data }) {
  const max = Math.max(...data.map((d) => d.value), 1);
  return (
    <Card className="mt-8 border-border/60 bg-card/80 p-6 backdrop-blur sm:p-8" style={{ boxShadow: "var(--shadow-card)" }}>
      <div className="mb-4 flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl text-primary-foreground" style={{ background: "var(--gradient-hero)" }}>
          <BarChart3 className="h-5 w-5" />
        </div>
        <div>
          <h2 className="text-lg font-semibold text-foreground">Pollutant Contribution</h2>
          <p className="text-xs text-muted-foreground">Each bar shows that pollutant's individual sub-AQI. The highest one drives the final AQI.</p>
        </div>
      </div>
      <div style={{ display: "flex", alignItems: "flex-end", justifyContent: "space-around", height: "220px", gap: "8px", padding: "0 8px" }}>
        {data.map((d, i) => {
          const c = getCategory(d.value);
          const heightPct = max > 0 ? (d.value / max) * 100 : 0;
          const isMax = d.value === max && max > 0;
          return (
            <div key={i} style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", gap: "4px", height: "100%", justifyContent: "flex-end" }}>
              <span style={{ fontSize: "12px", fontWeight: "600", color: c.hex }}>{d.value}</span>
              <div style={{ width: "100%", height: `${heightPct}%`, backgroundColor: c.hex, borderRadius: "6px 6px 0 0", outline: isMax ? "2px solid #333" : "none", outlineOffset: "1px", minHeight: d.value > 0 ? "4px" : "0px", transition: "height 0.4s ease" }} />
              <span style={{ fontSize: "11px", color: "hsl(var(--muted-foreground))", textAlign: "center", lineHeight: "1.2" }}>{d.name}</span>
            </div>
          );
        })}
      </div>
      <div style={{ marginTop: "12px", display: "flex", justifyContent: "space-between", fontSize: "10px", color: "hsl(var(--muted-foreground))", padding: "0 8px" }}>
        <span>Sub-AQI per pollutant — highest drives final AQI</span>
        <span>Max: {max}</span>
      </div>
    </Card>
  );
}

function CityAqiSearch() {
  const [cityQuery, setCityQuery] = useState("");
  const [cityResult, setCityResult] = useState(null);
  const [searched, setSearched] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [quickCities, setQuickCities] = useState([]);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/cities")
      .then(res => res.json())
      .then(data => {
        if (data.cities) setQuickCities(data.cities.slice(0, 10));
      })
      .catch(() => {
        setQuickCities(["Delhi", "Mumbai", "Bengaluru", "Kolkata", "Chennai"]);
      });
  }, []);

  const fetchCity = async (city) => {
    if (!city.trim()) return;
    setLoading(true);
    setError("");
    setCityResult(null);
    try {
      // get pollutant values from CSV
      const res = await fetch(`http://127.0.0.1:8000/city-data/${city}`);
      const data = await res.json();

      if (data.error) {
        setError(`City "${city}" not found in dataset.`);
      } else {
        // get LIVE AQI from WAQI API
        let liveAqi = null;
        try {
          const liveRes = await fetch(`http://127.0.0.1:8000/live-aqi/${city}`);
          const liveData = await liveRes.json();
          if (liveData.aqi && !liveData.error) {
            liveAqi = liveData.aqi;
          }
        } catch {
          // live fetch failed, use calculated
        }

        const calculatedAqi = estimateAqi({
          pm25: data.pm25 || 0, pm10: data.pm10 || 0,
          no2: data.no2 || 0, so2: data.so2 || 0,
          co: data.co || 0, o3: data.o3 || 0,
        });

        setCityResult({
          city,
          aqi: liveAqi ?? calculatedAqi,
          isLive: liveAqi !== null,
          pm25: data.pm25, pm10: data.pm10,
          no2: data.no2, so2: data.so2,
          co: data.co, o3: data.o3,
          pollutants: [
            { name: "PM2.5", value: subAqi("pm25", data.pm25 || 0) },
            { name: "PM10", value: subAqi("pm10", data.pm10 || 0) },
            { name: "NO₂", value: subAqi("no2", data.no2 || 0) },
            { name: "SO₂", value: subAqi("so2", data.so2 || 0) },
            { name: "CO", value: subAqi("co", data.co || 0) },
            { name: "O₃", value: subAqi("o3", data.o3 || 0) },
          ],
        });
      }
    } catch {
      setError("Backend not running. Please start your FastAPI server.");
    }
    setLoading(false);
    setSearched(true);
  };

  const handleCitySearch = (e) => {
    e.preventDefault();
    fetchCity(cityQuery);
  };

  return (
    <div className="mt-8 rounded-xl border border-border/60 bg-card/80 p-6 backdrop-blur sm:p-8" style={{ boxShadow: "var(--shadow-card)" }}>
      <div className="mb-6 flex items-center gap-3">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl text-primary-foreground" style={{ background: "var(--gradient-hero)" }}>
          <MapPin className="h-5 w-5" />
        </div>
        <div>
          <h2 className="text-lg font-semibold text-foreground">Search City AQI</h2>
          <p className="text-xs text-muted-foreground">Search any Indian city from the dataset</p>
        </div>
      </div>

      <form onSubmit={handleCitySearch} className="flex flex-col gap-3 sm:flex-row">
        <Input
          type="search"
          value={cityQuery}
          onChange={(e) => setCityQuery(e.target.value)}
          placeholder="Type any city e.g. Delhi, Patna, Lucknow..."
          className="h-11 bg-background/60"
        />
        <Button type="submit" className="h-11 px-6 text-primary-foreground" style={{ background: "var(--gradient-hero)", boxShadow: "var(--shadow-glow)" }}>
          <Search className="mr-2 h-4 w-4" />
          {loading ? "Searching…" : "Search"}
        </Button>
      </form>

      {quickCities.length > 0 && (
        <div className="mt-4 flex flex-wrap gap-2">
          {quickCities.map((city) => (
            <button key={city} type="button"
              onClick={() => { setCityQuery(city); fetchCity(city); }}
              className="rounded-full border border-border bg-background/70 px-3 py-1.5 text-xs font-semibold text-foreground transition hover:border-primary hover:text-primary">
              {city}
            </button>
          ))}
        </div>
      )}

      {loading && (
        <div className="mt-6 text-center text-sm text-muted-foreground animate-pulse">Fetching city data…</div>
      )}

      {searched && error && (
        <div className="mt-5 rounded-xl border border-border bg-background/50 p-4 text-sm text-muted-foreground">{error}</div>
      )}

      {cityResult && (
        <>
          <div className="mt-6 grid gap-4 lg:grid-cols-5">
            <div className="rounded-xl p-5 lg:col-span-2" style={{ backgroundColor: getCategory(cityResult.aqi).hex, color: getCategory(cityResult.aqi).textOn }}>
              <div className="flex items-center gap-2 text-sm font-bold opacity-90">
                <Building2 className="h-4 w-4" />{cityResult.city}
              </div>
              {cityResult.isLive && (
                <div className="mt-2 inline-flex items-center gap-1 rounded-full bg-green-500/20 px-2 py-0.5 text-xs font-semibold text-green-300">
                  <span className="h-1.5 w-1.5 rounded-full bg-green-400 animate-pulse inline-block" />
                  Live
                </div>
              )}

              {!cityResult.isLive && (
                <div className="mt-2 inline-flex items-center gap-1 rounded-full bg-white/10 px-2 py-0.5 text-xs text-white/60">
                  Historical data
                </div>
              )}
              <div className="mt-4 text-6xl font-black leading-none">{cityResult.aqi}</div>
              <div className="mt-2 inline-block rounded-full bg-black/15 px-3 py-1 text-xs font-bold backdrop-blur">
                {getCategory(cityResult.aqi).label}
              </div>
              <p className="mt-4 text-sm opacity-90">{getCategory(cityResult.aqi).description}</p>
            </div>

            <div className="grid gap-3 lg:col-span-3 sm:grid-cols-2">
              {[
                { label: "PM2.5", key: "pm25", value: cityResult.pm25, unit: "µg/m³" },
                { label: "PM10", key: "pm10", value: cityResult.pm10, unit: "µg/m³" },
                { label: "NO₂", key: "no2", value: cityResult.no2, unit: "ppb" },
                { label: "SO₂", key: "so2", value: cityResult.so2, unit: "ppb" },
                { label: "CO", key: "co", value: cityResult.co, unit: "ppm" },
                { label: "O₃", key: "o3", value: cityResult.o3, unit: "ppb" },
              ].map((p) => {
                const sub = subAqi(p.key, p.value || 0);
                const c = getCategory(sub);
                return (
                  <div key={p.label} className="rounded-xl border border-border bg-background/50 p-4">
                    <div className="flex items-start justify-between gap-3">
                      <div>
                        <div className="font-semibold text-foreground">{p.label}</div>
                        <div className="mt-1 text-xs text-muted-foreground">{p.unit}</div>
                      </div>
                      <div className="min-w-14 rounded-lg px-2 py-1 text-center text-sm font-black" style={{ backgroundColor: c.hex, color: c.textOn }}>
                        {p.value?.toFixed(1) ?? "–"}
                      </div>
                    </div>
                    <div className="mt-2 text-xs text-muted-foreground">Sub-AQI: <strong>{sub}</strong></div>
                    <div className="mt-2 h-2 overflow-hidden rounded-full bg-muted">
                      <div className="h-full rounded-full transition-all duration-700" style={{ width: `${Math.min(100, (sub / 500) * 100)}%`, backgroundColor: c.hex }} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="mt-6 overflow-hidden rounded-xl border border-border bg-card/90 p-4 sm:p-5" style={{ boxShadow: "var(--shadow-card)" }}>
            <div className="mb-4 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5 text-primary" />
                <h3 className="text-sm font-semibold text-foreground">Sub-AQI Breakdown</h3>
              </div>
              <div className="rounded-full bg-secondary px-3 py-1 text-xs font-semibold text-secondary-foreground">
                Final AQI: {cityResult.aqi}
              </div>
            </div>
            <div className="h-72 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={cityResult.pollutants} margin={{ top: 22, right: 10, left: 0, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="hsl(var(--border))" opacity={0.4} />
                  <XAxis dataKey="name" stroke="hsl(var(--muted-foreground))" fontSize={12} />
                  <YAxis stroke="hsl(var(--muted-foreground))" fontSize={12} />
                  <Tooltip contentStyle={{ background: "hsl(var(--card))", border: "1px solid hsl(var(--border))", borderRadius: 8, fontSize: 12 }} formatter={(v) => [v, "Sub-AQI"]} />
                  <Bar dataKey="value" radius={[8, 8, 0, 0]} isAnimationActive={false} background={{ fill: "transparent" }}>
                    {cityResult.pollutants.map((d, i) => {
                      const c = getCategory(d.value);
                      const isMax = d.value === cityResult.aqi;
                      return <Cell key={i} fill={c.hex} stroke={isMax ? "#333" : "none"} strokeWidth={isMax ? 2 : 0} />;
                    })}
                    <LabelList dataKey="value" position="top" style={{ fill: "hsl(var(--foreground))", fontSize: 11, fontWeight: 700 }} />
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

function ResultPanel({ aqi, predicting }) {
  if (aqi === null) {
    return (
      <Card className="flex h-full min-h-[420px] flex-col items-center justify-center border-dashed border-border/60 bg-card/50 p-8 text-center backdrop-blur">
        <div className="mb-4 flex h-16 w-16 items-center justify-center rounded-2xl text-primary-foreground" style={{ background: "var(--gradient-hero)" }}>
          <Gauge className="h-8 w-8" />
        </div>
        <h3 className="text-lg font-semibold text-foreground">Awaiting Prediction</h3>
        <p className="mt-2 max-w-xs text-sm text-muted-foreground">
          Fill in the pollutant values and click <span className="font-medium">Predict AQI</span> to see your air quality reading here.
        </p>
      </Card>
    );
  }
  const c = getCategory(aqi);
  const pct = Math.min(100, (aqi / 500) * 100);
  return (
    <Card className="relative h-full min-h-[420px] overflow-hidden border-0 p-8 text-center transition-all" style={{ backgroundColor: c.hex, color: c.textOn, boxShadow: "var(--shadow-glow)" }}>
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,rgba(255,255,255,0.25),transparent_60%)]" />
      <div className="relative">
        <div className="text-6xl">{c.emoji}</div>
        <div className="mt-3 text-xs font-semibold uppercase tracking-[0.2em] opacity-80">AQI</div>
        <div className={`mt-1 text-7xl font-black leading-none ${predicting ? "animate-pulse" : ""}`}>{aqi}</div>
        <div className="mt-3 inline-block rounded-full bg-black/15 px-4 py-1 text-sm font-bold backdrop-blur">{c.label}</div>
        <div className="mt-6">
          <div className="h-2 w-full overflow-hidden rounded-full bg-black/15">
            <div className="h-full rounded-full bg-white/80 transition-all duration-700" style={{ width: `${pct}%` }} />
          </div>
          <div className="mt-1 flex justify-between text-[10px] font-medium opacity-75">
            <span>0</span><span>250</span><span>500</span>
          </div>
        </div>
        <p className="mt-6 text-sm opacity-95">{c.description}</p>
        <div className="mt-4 rounded-xl bg-black/15 p-3 text-xs leading-relaxed backdrop-blur">
          <strong className="font-bold">Advice:</strong> {c.advice}
        </div>
      </div>
    </Card>
  );
}

const FIELDS = [
  { key: "pm25", label: "PM2.5", unit: "µg/m³", hint: "Fine particulates", placeholder: "e.g. 12" },
  { key: "pm10", label: "PM10", unit: "µg/m³", hint: "Coarse particulates", placeholder: "e.g. 40" },
  { key: "no2", label: "NO₂", unit: "ppb", hint: "Nitrogen dioxide", placeholder: "e.g. 25" },
  { key: "so2", label: "SO₂", unit: "ppb", hint: "Sulfur dioxide", placeholder: "e.g. 10" },
  { key: "co", label: "CO", unit: "ppm", hint: "Carbon monoxide", placeholder: "e.g. 1.2" },
  { key: "o3", label: "O₃", unit: "ppb", hint: "Ground-level ozone", placeholder: "e.g. 30" },
];

export default function AqiPredictor() {
  const [values, setValues] = useState({ pm25: "", pm10: "", no2: "", so2: "", co: "", o3: "" });
  const [aqi, setAqi] = useState(null);
  const [predicting, setPredicting] = useState(false);

  const category = useMemo(() => (aqi !== null ? getCategory(aqi) : null), [aqi]);
  const handleChange = (k, v) => setValues((s) => ({ ...s, [k]: v }));

  const handlePredict = (e) => {
    e.preventDefault();
    setPredicting(true);
    const parsed = {
      pm25: Number(values.pm25) || 0,
      pm10: Number(values.pm10) || 0,
      no2: Number(values.no2) || 0,
      so2: Number(values.so2) || 0,
      co: Number(values.co) || 0,
      o3: Number(values.o3) || 0,
    };
    setAqi(estimateAqi(parsed));
    setPredicting(false);
  };

  const handleReset = () => {
    setValues({ pm25: "", pm10: "", no2: "", so2: "", co: "", o3: "" });
    setAqi(null);
  };

  return (
    <div className="relative min-h-screen overflow-hidden bg-background">
      <div className="pointer-events-none absolute inset-0" style={{ background: "var(--gradient-sky)" }} aria-hidden />
      <div className="pointer-events-none absolute -top-40 -right-40 h-96 w-96 rounded-full opacity-30 blur-3xl" style={{ background: "var(--gradient-hero)" }} aria-hidden />
      <div className="pointer-events-none absolute -bottom-40 -left-40 h-96 w-96 rounded-full opacity-20 blur-3xl" style={{ background: "var(--gradient-hero)" }} aria-hidden />

      <main className="relative mx-auto max-w-6xl px-4 py-12 sm:px-6 lg:py-20">
        <header className="mb-12 text-center">
          <div className="inline-flex items-center gap-2 rounded-full border border-border bg-card/60 px-4 py-1.5 text-xs font-medium text-muted-foreground backdrop-blur">
            <Sparkles className="h-3.5 w-3.5 text-primary" />
            AI-powered Air Quality Prediction
          </div>
          <h1 className="mt-5 bg-clip-text text-4xl font-bold tracking-tight text-transparent sm:text-6xl" style={{ backgroundImage: "var(--gradient-hero)" }}>
            Breathe Smarter.
          </h1>
          <p className="mx-auto mt-4 max-w-2xl text-base text-muted-foreground sm:text-lg">
            Enter pollutant concentrations and instantly discover the predicted Air Quality Index, health category and recommendations for your environment.
          </p>
          {category && <p className="sr-only">Current category: {category.label}</p>}
        </header>

        <div className="grid gap-8 lg:grid-cols-5">
          <Card className="lg:col-span-3 border-border/60 bg-card/80 p-6 backdrop-blur sm:p-8" style={{ boxShadow: "var(--shadow-card)" }}>
            <div className="mb-6 flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-xl text-primary-foreground" style={{ background: "var(--gradient-hero)" }}>
                <Wind className="h-5 w-5" />
              </div>
              <div>
                <h2 className="text-lg font-semibold text-foreground">Pollutant Inputs</h2>
                <p className="text-xs text-muted-foreground">Enter measured values from your sensor or station</p>
              </div>
            </div>
            <form onSubmit={handlePredict} className="space-y-5">
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                {FIELDS.map((f) => (
                  <div key={f.key} className="space-y-1.5">
                    <Label htmlFor={f.key} className="flex items-center justify-between text-sm">
                      <span className="font-medium text-foreground">{f.label}</span>
                      <span className="text-xs text-muted-foreground">{f.unit}</span>
                    </Label>
                    <Input id={f.key} type="number" step="any" min="0" inputMode="decimal" placeholder={f.placeholder} value={values[f.key]} onChange={(e) => handleChange(f.key, e.target.value)} className="h-11 bg-background/60" />
                    <p className="text-xs text-muted-foreground">{f.hint}</p>
                  </div>
                ))}
              </div>
              <div className="flex flex-col-reverse gap-3 pt-2 sm:flex-row sm:justify-end">
                <Button type="button" variant="outline" onClick={handleReset} className="h-11">
                  <RotateCcw className="mr-2 h-4 w-4" />Reset
                </Button>
                <Button type="submit" disabled={predicting} className="h-11 px-6 text-primary-foreground transition-[transform,box-shadow] hover:scale-[1.02]" style={{ background: "var(--gradient-hero)", boxShadow: "var(--shadow-glow)" }}>
                  <Activity className="mr-2 h-4 w-4" />
                  {predicting ? "Analyzing…" : "Predict AQI"}
                </Button>
              </div>
            </form>
          </Card>
          <div className="lg:col-span-2">
            <ResultPanel aqi={aqi} predicting={predicting} />
          </div>
        </div>

        {aqi !== null && (
          <ContributionChart data={computeContributions(values)} />
        )}

        <CityAqiSearch />

        <section className="mt-14">
          <h3 className="mb-4 text-center text-sm font-medium uppercase tracking-wider text-muted-foreground">AQI Scale Reference</h3>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
            {[25, 75, 125, 175, 250, 350].map((v) => {
              const c = getCategory(v);
              return (
                <div key={v} className="rounded-xl p-4 text-center shadow-sm transition-transform hover:-translate-y-1" style={{ backgroundColor: c.hex, color: c.textOn }}>
                  <div className="text-2xl">{c.emoji}</div>
                  <div className="mt-1 text-xs font-semibold opacity-90">{c.range}</div>
                  <div className="text-sm font-bold">{c.label}</div>
                </div>
              );
            })}
          </div>
        </section>


      </main>
    </div>
  );
}
