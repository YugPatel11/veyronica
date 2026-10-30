import { StatCard } from "./stat-card";
import { Activity, ShieldCheck, Clock, Zap } from "lucide-react";

const meta = {
  title: "UI/StatCard",
  component: StatCard,
};

export default meta;

export const MetricsGrid = () => (
  <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
    <StatCard
      label="Active Runs"
      value="42"
      icon={Activity}
      delta="+12.5%"
      trend="up"
    />
    <StatCard
      label="Pass Rate"
      value="99.4%"
      icon={ShieldCheck}
      delta="+0.8%"
      trend="up"
    />
    <StatCard
      label="Avg Duration"
      value="1.2s"
      icon={Clock}
      delta="-14%"
      trend="up"
    />
    <StatCard
      label="Token Burn"
      value="$14.20"
      icon={Zap}
      delta="+4.1%"
      trend="down"
    />
  </div>
);
