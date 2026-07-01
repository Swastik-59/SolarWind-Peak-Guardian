import { MissionExperience } from "@/components/mission/mission-experience";
import { LenisProvider } from "@/components/lenis-provider";

export default function Home() {
  return (
    <LenisProvider>
      <MissionExperience />
    </LenisProvider>
  );
}
