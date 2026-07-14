type StatusBadgeProps = {
  label: string;
  tone?: "neutral" | "progress" | "verified" | "warning";
};

export function StatusBadge({ label, tone = "neutral" }: StatusBadgeProps) {
  return <span className={`statusBadge statusBadge--${tone}`}>{label}</span>;
}
