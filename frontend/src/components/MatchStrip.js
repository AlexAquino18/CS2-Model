import { useNavigate } from "react-router-dom";
import { ChevronRight, TrendingUp, Calendar, MapPin } from "lucide-react";
import { Button } from "@/components/ui/button";

const MatchStrip = ({ matchData, index }) => {
  const navigate = useNavigate();
  const { match, projections } = matchData;

  // Calculate value opportunities for this match
  const valueOpportunities = projections.filter(p => p.value_opportunity).length;
  const totalProjections = projections.length;

  const formatTime = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = date - now;
    const diffHrs = Math.floor(diffMs / (1000 * 60 * 60));
    
    if (diffHrs < 1) {
      return "Starting Soon";
    } else if (diffHrs < 24) {
      return `In ${diffHrs}h`;
    } else {
      const diffDays = Math.floor(diffHrs / 24);
      return `In ${diffDays}d`;
    }
  };

  return (
    <div
      data-testid={`match-strip-${index}`}
      className="group relative border border-border rounded-sm bg-card overflow-hidden hover:border-primary/50 transition-all hover:shadow-lg cursor-pointer"
      onClick={() => navigate(`/match/${match.id}`)}
    >
      {/* Noise texture overlay */}
      <div className="absolute inset-0 noise-texture pointer-events-none"></div>
      
      {/* Value opportunity indicator */}
      {valueOpportunities > 0 && (
        <div className="absolute top-0 right-0 bg-accent text-accent-foreground px-3 py-1 font-mono text-xs font-bold uppercase tracking-wider">
          {valueOpportunities} VALUE PLAYS
        </div>
      )}

      <div className="relative grid grid-cols-1 md:grid-cols-12 gap-4 items-center p-4">
        {/* Time and Tournament Info */}
        <div className="md:col-span-2 flex flex-col gap-1">
          <div className="flex items-center gap-2 text-muted-foreground">
            <Calendar className="w-4 h-4" />
            <span className="font-mono text-xs uppercase tracking-wider">{formatTime(match.start_time)}</span>
          </div>
          <p className="font-mono text-xs text-muted-foreground truncate">{match.tournament}</p>
        </div>

        {/* Teams */}
        <div className="md:col-span-4 flex items-center justify-between md:justify-start gap-4">
          <div className="flex-1 text-left md:text-right">
            <p className="font-heading text-xl md:text-2xl font-bold text-primary uppercase tracking-tight">
              {match.team1}
            </p>
          </div>
          <div className="flex items-center justify-center px-3">
            <span className="font-mono text-sm text-muted-foreground">VS</span>
          </div>
          <div className="flex-1 text-right md:text-left">
            <p className="font-heading text-xl md:text-2xl font-bold text-secondary uppercase tracking-tight">
              {match.team2}
            </p>
          </div>
        </div>

        {/* Maps */}
        <div className="md:col-span-2 flex items-center gap-2">
          <MapPin className="w-4 h-4 text-muted-foreground" />
          <div className="font-mono text-sm text-foreground">
            <span>{match.map1}</span>
            <span className="text-muted-foreground mx-1">•</span>
            <span>{match.map2}</span>
          </div>
        </div>

        {/* Stats */}
        <div className="md:col-span-3 flex items-center justify-between md:justify-end gap-4">
          <div className="flex flex-col items-center">
            <p className="font-mono text-xs text-muted-foreground uppercase tracking-wider">PROJECTIONS</p>
            <p className="font-mono text-lg font-bold text-foreground">{totalProjections}</p>
          </div>
          <div className="flex flex-col items-center">
            <p className="font-mono text-xs text-muted-foreground uppercase tracking-wider">VALUE PLAYS</p>
            <p className="font-mono text-lg font-bold text-accent">{valueOpportunities}</p>
          </div>
        </div>

        {/* Action Button */}
        <div className="md:col-span-1 flex justify-end">
          <Button
            data-testid={`view-details-${index}`}
            variant="ghost"
            className="text-muted-foreground hover:text-primary group-hover:translate-x-1 transition-transform"
            onClick={(e) => {
              e.stopPropagation();
              navigate(`/match/${match.id}`);
            }}
          >
            <ChevronRight className="w-6 h-6" />
          </Button>
        </div>
      </div>

      {/* Bottom accent line for value opportunities */}
      {valueOpportunities > 0 && (
        <div className="h-1 bg-gradient-to-r from-transparent via-accent to-transparent opacity-50"></div>
      )}
    </div>
  );
};

export default MatchStrip;