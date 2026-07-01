export const challenges = [
  ["Duck Curve", "Solar generation drops after 18:00 while operators must ramp alternatives in 1-2 hours."],
  ["Wind Intermittency", "Evening wind can complement solar, but remains variable without AI dispatch."],
  ["Storage Depletion", "Single-source batteries degrade 15-30% over five years and can empty during 5+ hour peaks."],
  ["Frequency Stability", "Renewable fluctuations must remain within the +/-0.5 Hz safety envelope."],
  ["Fossil Peaker Cost", "Diesel and gas peakers run only 5-10% of the time yet cost $150-200/MWh."]
];

export const sources = [
  ["Solar PV", "30-40% daytime demand, bifacial tracking, charges storage before sunset."],
  ["Wind Energy", "Onshore/offshore wind fills the evening solar gap with 20-35% peak contribution."],
  ["Li-Ion Battery", "200ms response for fast power delivery and frequency regulation."],
  ["CAES", "6-10 hour long-duration bulk energy release at lower storage cost per kWh."]
];

export const phases = [
  ["08:00-17:00", "Solar Charging", "60% grid feed, 40% Li-Ion charging and CAES compression."],
  ["17:00-19:00", "Wind + Storage Transition", "EMS blends evening wind with controlled Li-Ion discharge."],
  ["19:00-22:00", "Full Peak Coverage", "Wind, Li-Ion, and CAES are allocated for cost, efficiency, and stability."],
  ["22:00-08:00", "Recovery + Recharge", "Wind and morning solar restore readiness without manual intervention."]
];

export const useCases = [
  ["Urban Industrial Zones", "50-200 MW peaks, $15-25M annual fossil fuel savings, 80%+ evening renewable penetration."],
  ["Island + Remote Grids", "Self-sufficient 24/7 power with 95% renewable share and no diesel fuel imports."],
  ["Data Centers", "UPS-level 200ms clean response for uptime, ESG, and net-zero commitments."],
  ["Rural Agriculture", "Night irrigation, water pumping, and cold storage powered by surplus CAES energy."]
];

export const justification = [
  ["Evening Peak", "Daily, universal, high-impact, and directly solved by time-shifted renewable energy."],
  ["Solar", "Predictable daytime harvesting forms the foundation of the evening response."],
  ["Wind", "Temporal and geographic complementarity improves peak-hour reliability."],
  ["Hybrid Storage", "Li-Ion covers speed; CAES covers endurance and cost."],
  ["Alternative Comparison", "Biomass adds fuel complexity; geothermal is site-constrained; tri-source HRES scales."]
];

export const disadvantages = [
  ["High Initial CAPEX", "$1.5-2.5M/MW possible with CAES infrastructure; mitigated by bonds, subsidies, and PPAs."],
  ["CAES Site Dependency", "Salt caverns or depleted gas fields may be unavailable; use vessels or flow batteries where needed."],
  ["Integration Complexity", "Power electronics, SCADA, inverters, and EMS expertise are handled through modular standards."]
];
