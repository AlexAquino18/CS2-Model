import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";
import { ArrowLeft, RefreshCw, TrendingUp, TrendingDown } from "lucide-react";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const MatchDetail = () => {
  const { matchId } = useParams();
  const navigate = useNavigate();
  const [matchData, setMatchData] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchMatchDetail = async () => {
    try {
      const response = await axios.get(`${API}/matches/${matchId}`);
      setMatchData(response.data);
      setLoading(false);
    } catch (error) {
      console.error("Error fetching match detail:", error);
      toast.error("Failed to load match details");
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMatchDetail();
  }, [matchId]);

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <RefreshCw className="w-12 h-12 text-primary animate-spin" />
      </div>
    );
  }

  if (!matchData) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <p className="font-mono text-muted-foreground">MATCH NOT FOUND</p>
          <Button onClick={() => navigate('/')} className="mt-4">
            RETURN TO DASHBOARD
          </Button>
        </div>
      </div>
    );
  }

  const { match, projections } = matchData;

  // Group projections by team and stat type
  const team1Projections = projections.filter(p => p.team === match.team1);
  const team2Projections = projections.filter(p => p.team === match.team2);

  const renderProjectionTable = (teamProjections, teamName) => {
    const killsData = teamProjections.filter(p => p.stat_type === "kills");
    const headshotsData = teamProjections.filter(p => p.stat_type === "headshots");

    return (
      <div className="border border-border rounded-sm bg-card overflow-hidden">
        <div className="bg-primary/10 border-b border-border px-4 py-3">
          <h3 className="font-heading text-lg font-bold uppercase tracking-tight text-foreground">
            {teamName}
          </h3>
        </div>
        
        {/* Kills Table */}
        <div className="p-4">
          <p className="font-mono text-xs text-muted-foreground uppercase tracking-widest mb-3">KILLS PROJECTIONS</p>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left font-mono text-xs text-muted-foreground uppercase py-2 px-2">PLAYER</th>
                  <th className="text-center font-mono text-xs text-muted-foreground uppercase py-2 px-2">PROJECTION</th>
                  <th className="text-center font-mono text-xs text-muted-foreground uppercase py-2 px-2">PRIZEPICKS</th>
                  <th className="text-center font-mono text-xs text-muted-foreground uppercase py-2 px-2">UNDERDOG</th>
                  <th className="text-center font-mono text-xs text-muted-foreground uppercase py-2 px-2">DIFF</th>
                  <th className="text-center font-mono text-xs text-muted-foreground uppercase py-2 px-2">CONFIDENCE</th>
                </tr>
              </thead>
              <tbody>
                {killsData.map((proj, idx) => {
                  const ppLine = proj.dfs_lines.find(l => l.platform === "prizepicks");
                  const udLine = proj.dfs_lines.find(l => l.platform === "underdog");
                  return (
                    <tr key={idx} className={`border-b border-border/50 hover:bg-muted/30 transition-colors ${proj.value_opportunity ? 'bg-accent/5' : ''}`}>
                      <td className="py-3 px-2 font-mono font-medium text-sm text-foreground">{proj.player_name}</td>
                      <td className="py-3 px-2 text-center font-mono font-bold text-primary">{proj.projected_value}</td>
                      <td className="py-3 px-2 text-center font-mono text-sm text-muted-foreground">{ppLine?.line || '-'}</td>
                      <td className="py-3 px-2 text-center font-mono text-sm text-muted-foreground">{udLine?.line || '-'}</td>
                      <td className={`py-3 px-2 text-center font-mono font-bold text-sm ${proj.difference > 0 ? 'text-accent' : 'text-destructive'}`}>
                        {proj.difference > 0 ? '+' : ''}{proj.difference}
                      </td>
                      <td className="py-3 px-2 text-center font-mono text-sm text-muted-foreground">{proj.confidence}%</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Headshots Table */}
        <div className="p-4 border-t border-border">
          <p className="font-mono text-xs text-muted-foreground uppercase tracking-widest mb-3">HEADSHOTS PROJECTIONS</p>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left font-mono text-xs text-muted-foreground uppercase py-2 px-2">PLAYER</th>
                  <th className="text-center font-mono text-xs text-muted-foreground uppercase py-2 px-2">PROJECTION</th>
                  <th className="text-center font-mono text-xs text-muted-foreground uppercase py-2 px-2">PRIZEPICKS</th>
                  <th className="text-center font-mono text-xs text-muted-foreground uppercase py-2 px-2">UNDERDOG</th>
                  <th className="text-center font-mono text-xs text-muted-foreground uppercase py-2 px-2">DIFF</th>
                  <th className="text-center font-mono text-xs text-muted-foreground uppercase py-2 px-2">CONFIDENCE</th>
                </tr>
              </thead>
              <tbody>
                {headshotsData.map((proj, idx) => {
                  const ppLine = proj.dfs_lines.find(l => l.platform === "prizepicks");
                  const udLine = proj.dfs_lines.find(l => l.platform === "underdog");
                  return (
                    <tr key={idx} className={`border-b border-border/50 hover:bg-muted/30 transition-colors ${proj.value_opportunity ? 'bg-accent/5' : ''}`}>
                      <td className="py-3 px-2 font-mono font-medium text-sm text-foreground">{proj.player_name}</td>
                      <td className="py-3 px-2 text-center font-mono font-bold text-secondary">{proj.projected_value}</td>
                      <td className="py-3 px-2 text-center font-mono text-sm text-muted-foreground">{ppLine?.line || '-'}</td>
                      <td className="py-3 px-2 text-center font-mono text-sm text-muted-foreground">{udLine?.line || '-'}</td>
                      <td className={`py-3 px-2 text-center font-mono font-bold text-sm ${proj.difference > 0 ? 'text-accent' : 'text-destructive'}`}>
                        {proj.difference > 0 ? '+' : ''}{proj.difference}
                      </td>
                      <td className="py-3 px-2 text-center font-mono text-sm text-muted-foreground">{proj.confidence}%</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center gap-4">
            <Button
              data-testid="back-button"
              onClick={() => navigate('/')}
              variant="ghost"
              className="text-muted-foreground hover:text-primary"
            >
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <div>
              <h1 className="font-heading text-2xl md:text-3xl font-black tracking-tighter uppercase text-foreground">
                MATCH ANALYSIS
              </h1>
              <p className="font-mono text-xs text-muted-foreground tracking-widest uppercase mt-1">
                {match.tournament}
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Match Info */}
      <div className="border-b border-border bg-card/30">
        <div className="container mx-auto px-6 py-6">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center gap-6">
              <div className="text-center">
                <p className="font-heading text-3xl font-bold text-primary">{match.team1}</p>
              </div>
              <div className="text-center">
                <p className="font-mono text-2xl text-muted-foreground">VS</p>
              </div>
              <div className="text-center">
                <p className="font-heading text-3xl font-bold text-secondary">{match.team2}</p>
              </div>
            </div>
            <div className="text-right">
              <p className="font-mono text-xs text-muted-foreground uppercase tracking-wider">MAPS</p>
              <p className="font-mono text-sm text-foreground">{match.map1} • {match.map2}</p>
              <p className="font-mono text-xs text-muted-foreground mt-2">
                {new Date(match.start_time).toLocaleString()}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Projections */}
      <main className="container mx-auto px-6 py-8">
        <div className="space-y-6">
          {renderProjectionTable(team1Projections, match.team1)}
          {renderProjectionTable(team2Projections, match.team2)}
        </div>

        <div className="mt-8 border border-border rounded-sm bg-card p-4">
          <p className="font-mono text-xs text-muted-foreground uppercase tracking-widest mb-2">LEGEND</p>
          <div className="flex flex-wrap gap-6 text-sm">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-accent rounded-sm"></div>
              <span className="font-mono text-muted-foreground">Value Opportunity (Highlighted Rows)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-primary rounded-sm"></div>
              <span className="font-mono text-muted-foreground">Kills Projection</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-secondary rounded-sm"></div>
              <span className="font-mono text-muted-foreground">Headshots Projection</span>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default MatchDetail;