const StatsPanel = ({ icon, label, value, highlight = false }) => {
  return (
    <div className="bg-card/50 border border-border rounded-sm p-4 hover:border-primary/30 transition-colors">
      <div className="flex items-start gap-3">
        <div className={`p-2 rounded-sm ${highlight ? 'bg-accent/20 text-accent' : 'bg-muted text-muted-foreground'}`}>
          {icon}
        </div>
        <div className="flex-1">
          <p className="font-mono text-xs text-muted-foreground uppercase tracking-widest mb-1">
            {label}
          </p>
          <p className={`font-mono text-2xl font-bold ${highlight ? 'text-accent' : 'text-foreground'}`}>
            {value}
          </p>
        </div>
      </div>
    </div>
  );
};

export default StatsPanel;