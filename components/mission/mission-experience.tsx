"use client";

import { motion, useScroll, useTransform } from "framer-motion";
import { Activity, BatteryCharging, BrainCircuit, Download, Factory, Gauge, Leaf, RadioTower, Settings, SunMedium, Waves, Wind, Zap } from "lucide-react";
import { useEffect, useMemo, useState } from "react";
import { Area, AreaChart, Bar, BarChart, CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useForm } from "react-hook-form";
import { api, getMissionData, type MissionData } from "@/lib/api";
import { challenges, disadvantages, justification, phases, sources, useCases } from "@/lib/content";
import type { Simulation } from "@/lib/types";
import { useMissionStore } from "@/store/mission-store";

const fallback: MissionData = {
  forecast: { horizon_hours: 2, peak_window: "17:00-22:00", confidence: 0.91, ai_explanation: "EMS reserves CAES for bulk delivery while Li-Ion protects frequency.", points: [
    { time: "16:00", demand_mw: 210, solar_mw: 116, wind_mw: 58, battery_mw: 18, caes_mw: 0, frequency_hz: 50.03 },
    { time: "17:00", demand_mw: 254, solar_mw: 72, wind_mw: 76, battery_mw: 36, caes_mw: 0, frequency_hz: 50.01 },
    { time: "18:00", demand_mw: 308, solar_mw: 22, wind_mw: 93, battery_mw: 74, caes_mw: 24, frequency_hz: 49.98 },
    { time: "19:00", demand_mw: 338, solar_mw: 0, wind_mw: 104, battery_mw: 86, caes_mw: 82, frequency_hz: 50.0 },
    { time: "20:00", demand_mw: 326, solar_mw: 0, wind_mw: 96, battery_mw: 72, caes_mw: 104, frequency_hz: 50.02 },
    { time: "21:00", demand_mw: 286, solar_mw: 0, wind_mw: 88, battery_mw: 54, caes_mw: 82, frequency_hz: 50.04 },
    { time: "22:00", demand_mw: 224, solar_mw: 0, wind_mw: 71, battery_mw: 28, caes_mw: 48, frequency_hz: 50.05 }
  ] },
  weather: { condition: "Coastal wind ramp", temperature_c: 31.4, wind_speed_mps: 8.7, solar_irradiance_wm2: 184, cloud_cover_percentage: 18, forecast_note: "Sunset reduces irradiance while thermal winds strengthen." },
  analytics: { efficiency_gain_percentage: 16.2, grid_stability_score: 97.4, storage_cycles_saved: 128, renewable_peak_coverage_percentage: 91.2, brownout_risk_reduction_percentage: 86.5, telemetry: [] },
  battery: { state_of_charge_percentage: 76, output_mw: 64, response_time_ms: 200, health_percentage: 93.8, cycle_strategy: "Shallow fast-response regulation." },
  storage: { li_ion: { state_of_charge_percentage: 76, output_mw: 64, response_time_ms: 200, health_percentage: 93.8, cycle_strategy: "Shallow fast-response regulation." }, caes_pressure_bar: 68, caes_state_of_charge_percentage: 84, caes_output_mw: 92, duration_hours_remaining: 7.8, round_trip_efficiency_percentage: 94 },
  renewables: { solar_mw: 42, wind_mw: 92, solar_capacity_factor: 0.25, wind_capacity_factor: 0.47, smart_grid_efficiency_percentage: 94, source_mix: { solar: 42, wind: 92, li_ion: 68, caes: 96 } },
  carbon: { co2_avoided_tonnes_year: 150000, co2_avoided_tonnes_today: 411, diesel_mwh_displaced: 642, sdg_alignment: ["SDG 7", "SDG 13"] },
  cost: { hres_lcoe_usd_mwh: 74, diesel_peaker_usd_mwh: 182, annual_savings_usd_million: 21.6, capex_usd_mw_million: 2.1, payback_years: 9.4, ancillary_revenue_usd_million: 3.8 },
  grid: { frequency_hz: 50.01, renewable_percentage: 91.2, demand_mw: 318, served_mw: 319, stability_state: "stable", voltage_kv: 220.4, ai_action: "Dispatch CAES for bulk ramp." }
};

export function MissionExperience() {
  const [data, setData] = useState<MissionData>(fallback);
  const [activeUseCase, setActiveUseCase] = useState(0);
  const { telemetry, setTelemetry, running, startSimulation, finishSimulation, simulation } = useMissionStore();
  const live = telemetry ?? { tick: 0, grid: data.grid, storage: data.storage, renewables: data.renewables, carbon: data.carbon, cost: data.cost };
  const { scrollYProgress } = useScroll();
  const sky = useTransform(scrollYProgress, [0, 0.28], ["rgba(216,155,53,.18)", "rgba(121,167,200,.08)"]);

  useEffect(() => {
    getMissionData().then(setData).catch(() => setData(fallback));
    const ws = new WebSocket(api.telemetryUrl());
    ws.onmessage = (event) => setTelemetry(JSON.parse(event.data));
    ws.onerror = () => ws.close();
    return () => ws.close();
  }, [setTelemetry]);

  const runSimulation = async () => {
    startSimulation();
    const result = await api.simulate(340).catch<Simulation>(() => ({
      scenario: "evening_peak",
      phases: phases.map(([window, name, description]) => ({ window, name, description, solar_mw: 0, wind_mw: 90, battery_mw: 70, caes_mw: 96, grid_frequency_hz: 50.01 })),
      ems_decisions: [{ timestamp: "19:04", decision: "CAES synchronized to grid", reason: "Demand exceeded Li-Ion endurance threshold." }],
      outcomes: { co2_avoided_tonnes: 411, diesel_cost_avoided_usd: 58240, hres_cost_usd: 23680, renewable_peak_coverage_percentage: 91.2 }
    }));
    setTimeout(() => finishSimulation(result), 900);
  };

  return (
    <main className="overflow-hidden bg-graphite text-bone">
      <MissionRail />
      <motion.section id="landing" style={{ backgroundColor: sky }} className="mission-grid relative min-h-screen px-6 py-8 lg:px-16">
        <Header />
        <div className="grid min-h-[82vh] items-center gap-12 lg:grid-cols-[1.05fr_.95fr]">
          <div>
            <p className="font-mono text-xs uppercase tracking-[.28em] text-amber">Hybrid Hack 2026 / Team Kaisen</p>
            <h1 className="mt-6 max-w-5xl font-display text-[16vw] leading-[.78] text-balance md:text-[10vw] lg:text-[8vw]">SolarWind Peak Guardian</h1>
            <p className="mt-8 max-w-2xl text-lg leading-8 text-bone/72">AI-powered hybrid renewable system for fossil-free evening peak management, designed for operators protecting national-scale grids through the 17:00-22:00 demand surge.</p>
            <div className="mt-10 grid max-w-2xl grid-cols-3 border-y hairline py-5 font-mono text-xs uppercase text-bone/64">
              <Metric label="Peak coverage" value={`${live.grid.renewable_percentage.toFixed(1)}%`} />
              <Metric label="Frequency" value={`${live.grid.frequency_hz.toFixed(2)}Hz`} />
              <Metric label="CO2/year" value="150k t" />
            </div>
          </div>
          <EarthSystem running={running} />
        </div>
      </motion.section>

      <Section id="problem" kicker="Act 1 / The Problem" title="The duck curve is not a chart. It is the moment the grid loses time.">
        <div className="grid gap-8 lg:grid-cols-[1.2fr_.8fr]">
          <Panel className="min-h-[420px]">
            <ResponsiveContainer width="100%" height={360}>
              <AreaChart data={data.forecast.points}>
                <defs>
                  <linearGradient id="demand" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#b96b57" stopOpacity={0.6} /><stop offset="100%" stopColor="#b96b57" stopOpacity={0.02} /></linearGradient>
                </defs>
                <CartesianGrid stroke="rgba(243,239,229,.09)" vertical={false} />
                <XAxis dataKey="time" stroke="#8c918c" />
                <YAxis stroke="#8c918c" />
                <Tooltip contentStyle={{ background: "#141615", border: "1px solid rgba(243,239,229,.14)", color: "#f3efe5" }} />
                <Area type="monotone" dataKey="demand_mw" stroke="#b96b57" fill="url(#demand)" name="Demand MW" />
                <Line type="monotone" dataKey="solar_mw" stroke="#d89b35" strokeWidth={3} name="Solar MW" />
              </AreaChart>
            </ResponsiveContainer>
          </Panel>
          <div className="space-y-3">
            {challenges.map(([name, copy], index) => <TextRow key={name} index={index + 1} name={name} copy={copy} />)}
          </div>
        </div>
      </Section>

      <Section id="control" kicker="Act 2 / Mission Control" title="AI EMS allocates sunlight, wind, Li-Ion speed, and CAES endurance as one organism.">
        <div className="grid gap-8 xl:grid-cols-[1fr_420px]">
          <DigitalTwin live={live} running={running} />
          <div className="space-y-4">
            <Panel><StatusGrid live={live} /></Panel>
            <Panel><Copilot data={data} /></Panel>
          </div>
        </div>
      </Section>

      <Section id="sources" kicker="Renewable Sources + Storage" title="Four complementary assets, each selected for a different job in the evening peak.">
        <div className="grid gap-6 md:grid-cols-2">
          {sources.map(([name, copy], index) => <SourceComposition key={name} index={index} name={name} copy={copy} live={live} />)}
        </div>
      </Section>

      <Section id="architecture" kicker="Animated System Architecture" title="The operating cycle follows the exact four-phase presentation flow.">
        <div className="grid gap-6 lg:grid-cols-4">
          {phases.map(([window, name, copy], index) => <Phase key={name} index={index} window={window} name={name} copy={copy} active={running || index < 3} />)}
        </div>
      </Section>

      <Section id="simulator" kicker="Peak Demand Simulator" title="Press one control and the evening peak sequence comes alive.">
        <div className="grid items-start gap-8 lg:grid-cols-[420px_1fr]">
          <SimulatorControl onRun={runSimulation} running={running} simulation={simulation} />
          <Panel>
            <ResponsiveContainer width="100%" height={360}>
              <LineChart data={data.forecast.points}>
                <CartesianGrid stroke="rgba(243,239,229,.09)" vertical={false} />
                <XAxis dataKey="time" stroke="#8c918c" />
                <YAxis stroke="#8c918c" />
                <Tooltip contentStyle={{ background: "#141615", border: "1px solid rgba(243,239,229,.14)", color: "#f3efe5" }} />
                <Line type="monotone" dataKey="wind_mw" stroke="#79a7c8" strokeWidth={3} />
                <Line type="monotone" dataKey="battery_mw" stroke="#6f9f72" strokeWidth={3} />
                <Line type="monotone" dataKey="caes_mw" stroke="#d89b35" strokeWidth={3} />
              </LineChart>
            </ResponsiveContainer>
          </Panel>
        </div>
      </Section>

      <Section id="results" kicker="Act 3 / Results" title="Zero-carbon peak power with economic logic, operational stability, and honest constraints.">
        <div className="grid gap-6 lg:grid-cols-3">
          <BigNumber label="CO2 reduction per 100 MW" value={`${data.carbon.co2_avoided_tonnes_year.toLocaleString()} t/yr`} />
          <BigNumber label="LCOE vs diesel peaker" value={`$${data.cost.hres_lcoe_usd_mwh}-${data.cost.diesel_peaker_usd_mwh}/MWh`} />
          <BigNumber label="AI efficiency gain" value={`${data.analytics.efficiency_gain_percentage}%`} />
        </div>
        <div className="mt-8 grid gap-8 lg:grid-cols-[.8fr_1.2fr]">
          <Panel>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={[{ name: "HRES", value: data.cost.hres_lcoe_usd_mwh }, { name: "Diesel", value: data.cost.diesel_peaker_usd_mwh }]}>
                <XAxis dataKey="name" stroke="#8c918c" /><YAxis stroke="#8c918c" />
                <Bar dataKey="value" fill="#d89b35" radius={[2, 2, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </Panel>
          <div className="grid gap-3">
            {justification.map(([name, copy], i) => <TextRow key={name} index={i + 1} name={name} copy={copy} />)}
          </div>
        </div>
      </Section>

      <Section id="usecases" kicker="Use-Case Explorer" title="The same system scales from industrial corridors to islands, data centers, and farms.">
        <div className="grid gap-8 lg:grid-cols-[320px_1fr]">
          <div className="space-y-2">{useCases.map(([name], i) => <button key={name} onClick={() => setActiveUseCase(i)} className={`w-full border-l px-4 py-4 text-left font-mono text-sm uppercase ${activeUseCase === i ? "border-amber text-amber" : "border-bone/15 text-bone/56"}`}>{name}</button>)}</div>
          <Panel className="min-h-[260px]">
            <Factory className="mb-8 text-amber" size={36} />
            <h3 className="font-display text-5xl">{useCases[activeUseCase][0]}</h3>
            <p className="mt-6 max-w-2xl text-xl leading-9 text-bone/70">{useCases[activeUseCase][1]}</p>
          </Panel>
        </div>
      </Section>

      <Section id="reports" kicker="Reports + Settings" title="Generate a judge-ready operating report and tune the mission assumptions.">
        <div className="grid gap-8 lg:grid-cols-2">
          <Report simulation={simulation} />
          <SettingsPanel />
        </div>
        <div className="mt-8 grid gap-3">
          {disadvantages.map(([name, copy], i) => <TextRow key={name} index={i + 1} name={name} copy={copy} />)}
        </div>
      </Section>
    </main>
  );
}

function Header() {
  return <header className="flex items-center justify-between border-b hairline pb-5 font-mono text-xs uppercase tracking-[.18em] text-bone/56"><span>National renewable grid mission control</span><span>AI EMS / Live</span></header>;
}

function MissionRail() {
  return <nav aria-label="Mission sections" className="fixed right-4 top-1/2 z-50 hidden -translate-y-1/2 flex-col gap-3 lg:flex">{["landing","problem","control","sources","architecture","simulator","results","usecases","reports"].map((id) => <a key={id} href={`#${id}`} className="h-8 w-px bg-bone/22 transition hover:bg-amber" />)}</nav>;
}

function Section({ id, kicker, title, children }: { id: string; kicker: string; title: string; children: React.ReactNode }) {
  return <section id={id} className="border-t hairline px-6 py-24 lg:px-16 lg:py-32"><p className="font-mono text-xs uppercase tracking-[.28em] text-amber">{kicker}</p><h2 className="mb-12 mt-5 max-w-5xl font-display text-5xl leading-[.95] text-balance md:text-7xl">{title}</h2>{children}</section>;
}

function Panel({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return <div className={`border hairline bg-ink/72 p-5 ${className}`}>{children}</div>;
}

function Metric({ label, value }: { label: string; value: string }) {
  return <div><div className="text-bone">{value}</div><div className="mt-2 text-bone/42">{label}</div></div>;
}

function TextRow({ index, name, copy }: { index: number; name: string; copy: string }) {
  return <div className="grid grid-cols-[42px_1fr] border-t hairline py-4"><span className="font-mono text-sm text-amber">{String(index).padStart(2, "0")}</span><div><h3 className="font-mono text-sm uppercase tracking-[.16em]">{name}</h3><p className="mt-2 leading-7 text-bone/64">{copy}</p></div></div>;
}

function EarthSystem({ running }: { running: boolean }) {
  return <div className="relative mx-auto aspect-square w-full max-w-[620px]"><div className="absolute inset-10 rounded-full border border-bone/15 bg-[radial-gradient(circle_at_35%_35%,rgba(216,155,53,.28),rgba(121,167,200,.1)_35%,rgba(0,0,0,.12)_60%,transparent_70%)]" /><svg viewBox="0 0 600 600" className="absolute inset-0 h-full w-full"><circle cx="300" cy="300" r="214" fill="none" stroke="rgba(243,239,229,.16)" /><circle className="energy-line" cx="300" cy="300" r="260" fill="none" stroke={running ? "#d89b35" : "#79a7c8"} strokeWidth="2" /><path className="energy-line" d="M90 390 C180 280 280 470 510 220" fill="none" stroke="#d89b35" strokeWidth="3" /><circle className="pulse-dot" cx="508" cy="220" r="5" fill="#d89b35" /></svg></div>;
}

function DigitalTwin({ live, running }: { live: ReturnType<typeof useMemo> & any; running: boolean }) {
  const nodes = [{ x: 90, y: 100, label: "Solar", icon: SunMedium }, { x: 90, y: 300, label: "Wind", icon: Wind }, { x: 330, y: 205, label: "AI EMS", icon: BrainCircuit }, { x: 570, y: 95, label: "Li-Ion", icon: BatteryCharging }, { x: 570, y: 300, label: "CAES", icon: Gauge }, { x: 780, y: 205, label: "Grid", icon: RadioTower }];
  return <Panel className="relative min-h-[560px] overflow-hidden"><svg viewBox="0 0 900 440" className="h-full min-h-[440px] w-full"><defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8" fill="#d89b35" /></marker></defs>{[[90,100,330,205],[90,300,330,205],[330,205,570,95],[330,205,570,300],[570,95,780,205],[570,300,780,205]].map(([x1,y1,x2,y2], i) => <path key={i} className="energy-line" d={`M${x1} ${y1} C${(x1+x2)/2} ${y1}, ${(x1+x2)/2} ${y2}, ${x2} ${y2}`} fill="none" stroke={i % 2 ? "#79a7c8" : "#d89b35"} strokeWidth={running ? 4 : 2} markerEnd="url(#arrow)" />)}{nodes.map(({ x, y, label, icon: Icon }) => <g key={label}><circle cx={x} cy={y} r={54} fill="#0b0c0c" stroke="rgba(243,239,229,.22)" /><foreignObject x={x-38} y={y-38} width="76" height="76"><div className="flex h-full flex-col items-center justify-center gap-1 text-center"><Icon className={label === "Wind" ? "spin-slow text-telemetry" : "text-amber"} size={24}/><span className="font-mono text-[10px] uppercase">{label}</span></div></foreignObject></g>)}</svg><div className="grid gap-4 border-t hairline pt-4 font-mono text-xs uppercase text-bone/58 md:grid-cols-4"><Metric label="Demand" value={`${live.grid.demand_mw.toFixed(0)} MW`} /><Metric label="Wind" value={`${live.renewables.wind_mw.toFixed(0)} MW`} /><Metric label="Battery" value={`${live.storage.li_ion.state_of_charge_percentage.toFixed(0)}%`} /><Metric label="CAES" value={`${live.storage.caes_pressure_bar.toFixed(0)} bar`} /></div></Panel>;
}

function StatusGrid({ live }: { live: any }) {
  return <div className="grid grid-cols-2 gap-4"><Metric label="Weather wind" value={`${live.renewables.wind_mw.toFixed(0)}MW`} /><Metric label="Storage hours" value={`${live.storage.duration_hours_remaining.toFixed(1)}h`} /><Metric label="Frequency" value={`${live.grid.frequency_hz.toFixed(2)}Hz`} /><Metric label="Renewable" value={`${live.grid.renewable_percentage.toFixed(1)}%`} /></div>;
}

function Copilot({ data }: { data: MissionData }) {
  return <div><div className="mb-4 flex items-center gap-3 font-mono text-xs uppercase text-amber"><BrainCircuit size={16}/> Grid Intelligence</div><p className="leading-7 text-bone/70">{data.forecast.ai_explanation}</p><p className="mt-4 border-t hairline pt-4 text-sm leading-6 text-bone/52">Why did battery output increase? Solar fell below the demand-ramp threshold, so Li-Ion absorbed the 200ms frequency correction while CAES stayed reserved for long-duration discharge.</p></div>;
}

function SourceComposition({ index, name, copy, live }: { index: number; name: string; copy: string; live: any }) {
  const icons = [SunMedium, Wind, BatteryCharging, Waves];
  const Icon = icons[index];
  const value = [live.renewables.solar_mw, live.renewables.wind_mw, live.storage.li_ion.output_mw, live.storage.caes_output_mw][index];
  return <Panel><div className="flex items-start justify-between"><Icon className={index === 1 ? "spin-slow text-telemetry" : "text-amber"} size={40}/><span className="font-mono text-4xl">{value.toFixed(0)}</span></div><h3 className="mt-12 font-display text-4xl">{name}</h3><p className="mt-4 leading-7 text-bone/64">{copy}</p></Panel>;
}

function Phase({ index, window, name, copy, active }: { index: number; window: string; name: string; copy: string; active: boolean }) {
  return <motion.div animate={{ opacity: active ? 1 : .45 }} className="border-t hairline pt-5"><div className="font-mono text-xs text-amber">{window}</div><h3 className="mt-5 font-display text-3xl">{name}</h3><p className="mt-5 leading-7 text-bone/62">{copy}</p><div className="mt-8 h-1 bg-bone/10"><motion.div animate={{ width: active ? "100%" : "28%" }} className="h-full bg-amber" /></div></motion.div>;
}

function SimulatorControl({ onRun, running, simulation }: { onRun: () => void; running: boolean; simulation?: Simulation }) {
  return <Panel><button onClick={onRun} disabled={running} className="group flex w-full items-center justify-center gap-3 bg-bone px-5 py-5 font-mono text-sm uppercase tracking-[.18em] text-graphite transition hover:bg-amber disabled:opacity-60"><Zap size={18}/>{running ? "Running peak sequence" : "Run Evening Peak Simulation"}</button><div className="mt-8 space-y-4">{(simulation?.ems_decisions ?? []).map((item) => <div key={item.timestamp} className="border-l border-amber pl-4"><div className="font-mono text-xs text-amber">{item.timestamp}</div><div className="mt-1">{item.decision}</div><p className="mt-1 text-sm leading-6 text-bone/56">{item.reason}</p></div>)}</div></Panel>;
}

function BigNumber({ label, value }: { label: string; value: string }) {
  return <div className="border-t hairline pt-5"><div className="font-display text-5xl md:text-6xl">{value}</div><div className="mt-4 font-mono text-xs uppercase tracking-[.18em] text-bone/46">{label}</div></div>;
}

function Report({ simulation }: { simulation?: Simulation }) {
  return <Panel><Download className="text-amber" /><h3 className="mt-8 font-display text-4xl">Simulation report</h3><p className="mt-4 leading-7 text-bone/64">Generates an operator summary with phase timeline, EMS decisions, carbon savings, cost delta, and future roadmap for microgrids and V2G vehicle storage.</p><button className="mt-8 border hairline px-5 py-3 font-mono text-xs uppercase tracking-[.16em] text-amber">Prepare PDF Summary</button><div className="mt-6 text-sm text-bone/48">Last run: {simulation ? simulation.scenario : "No simulation run yet"}</div></Panel>;
}

function SettingsPanel() {
  const { register } = useForm({ defaultValues: { peak: 340, caes: true, bonds: true } });
  return <Panel><Settings className="text-amber" /><h3 className="mt-8 font-display text-4xl">Settings</h3><label className="mt-6 block font-mono text-xs uppercase text-bone/56">Peak demand MW<input type="number" {...register("peak")} className="mt-2 w-full border hairline bg-transparent px-3 py-3 text-bone" /></label><label className="mt-5 flex items-center gap-3 text-bone/70"><input type="checkbox" {...register("caes")} /> Allow vessel CAES fallback</label><label className="mt-3 flex items-center gap-3 text-bone/70"><input type="checkbox" {...register("bonds")} /> Include green bonds and PPA mitigation</label><p className="mt-6 text-sm leading-6 text-bone/48">Settings model the presentation mitigations: financing offsets CAPEX, alternate storage handles CAES geology limits, and modular standards reduce integration complexity.</p></Panel>;
}
