"use client";

import { create } from "zustand";
import type { Simulation, Telemetry } from "@/lib/types";

type MissionState = {
  running: boolean;
  intensity: number;
  telemetry?: Telemetry;
  simulation?: Simulation;
  setTelemetry: (telemetry: Telemetry) => void;
  startSimulation: () => void;
  finishSimulation: (simulation: Simulation) => void;
  setIntensity: (intensity: number) => void;
};

export const useMissionStore = create<MissionState>((set) => ({
  running: false,
  intensity: 0,
  setTelemetry: (telemetry) => set({ telemetry }),
  startSimulation: () => set({ running: true, intensity: 1 }),
  finishSimulation: (simulation) => set({ simulation, running: false, intensity: 0.78 }),
  setIntensity: (intensity) => set({ intensity })
}));
