import { Badge } from "./badge";
import { StatusBadge } from "./status-badge";
import { RiskBadge } from "./risk-badge";

const meta = {
  title: "UI/Badges",
  component: Badge,
};

export default meta;

export const Standard = () => (
  <div className="flex gap-3 items-center">
    <Badge variant="filled" color="primary">Primary</Badge>
    <Badge variant="outline" color="success">Success</Badge>
    <Badge variant="dot" color="warning">Warning</Badge>
    <Badge variant="filled" color="danger">Danger</Badge>
  </div>
);

export const WorkflowStatuses = () => (
  <div className="flex flex-wrap gap-3 items-center">
    <StatusBadge status="running" />
    <StatusBadge status="done" />
    <StatusBadge status="failed" />
    <StatusBadge status="waiting" />
    <StatusBadge status="queued" />
  </div>
);

export const RiskIndicators = () => (
  <div className="flex gap-3 items-center">
    <RiskBadge level="low" />
    <RiskBadge level="medium" />
    <RiskBadge level="high" />
    <RiskBadge level="critical" />
  </div>
);
