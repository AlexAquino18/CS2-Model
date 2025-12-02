import { useEffect, useState } from "react";
import axios from "axios";
import { RefreshCw, TrendingUp, AlertCircle, Clock } from "lucide-react";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import MatchStrip from "@/components/MatchStrip";
import StatsPanel from "@/components/StatsPanel";
import DataSourceBanner from "@/components/DataSourceBanner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Dashboard = () => {
  const [matches, setMatches] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [lastUpdate, setLastUpdate] = useState(null);

  const fetchMatches = async () => {
    try {
      const response = await axios.get(`${API}/matches`);
      setMatches(response.data);
      if (response.data.length > 0) {
        setLastUpdate(new Date(response.data[0].last_updated));
      }
      setLoading(false);
    } catch (error) {
      console.error("Error fetching matches:", error);
      toast.error("Failed to load matches");
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API}/stats`);
      setStats(response.data);
    } catch (error) {
      console.error("Error fetching stats:", error);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      await axios.post(`${API}/refresh`);
      await fetchMatches();
      await fetchStats();
      toast.success("Data refreshed successfully");
    } catch (error) {
      console.error("Error refreshing data:", error);
      toast.error("Failed to refresh data");
    }
    setRefreshing(false);
  };

  useEffect(() => {
    fetchMatches();
    fetchStats();
    
    // Auto-refresh every 5 minutes
    const interval = setInterval(() => {
      fetchMatches();
      fetchStats();
    }, 300000);

    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="w-12 h-12 text-primary animate-spin mx-auto mb-4" />
          <p className="font-mono text-muted-foreground">INITIALIZING PROJECTION SYSTEM...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="font-heading text-3xl md:text-4xl font-black tracking-tighter uppercase text-foreground">
                CS2 PRO TERMINAL
              </h1>
              <p className="font-mono text-xs text-muted-foreground tracking-widest uppercase mt-1">
                PROJECTION MATRIX v1.0
              </p>
            </div>
            <div className="flex items-center gap-4">
              {lastUpdate && (
                <div className="text-right hidden md:block">
                  <p className="font-mono text-xs text-muted-foreground uppercase tracking-wider">LAST UPDATE</p>
                  <p className="font-mono text-sm text-foreground">
                    {lastUpdate.toLocaleTimeString()}
                  </p>
                </div>
              )}
              <Button
                data-testid="refresh-button"
                onClick={handleRefresh}
                disabled={refreshing}
                className="bg-primary text-primary-foreground font-black uppercase tracking-wider hover:bg-primary/90 active:scale-95 transition-all rounded-sm"
              >
                <RefreshCw className={`w-4 h-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
                REFRESH
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Stats Bar */}
      {stats && (
        <div className="border-b border-border bg-card/30">
          <div className="container mx-auto px-6 py-4">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <StatsPanel
                icon={<TrendingUp className="w-5 h-5" />}
                label="TOTAL PROJECTIONS"
                value={stats.total_projections}
              />
              <StatsPanel
                icon={<AlertCircle className="w-5 h-5" />}
                label="VALUE OPPORTUNITIES"
                value={stats.value_opportunities}
                highlight
              />
              <StatsPanel
                icon={<Clock className="w-5 h-5" />}
                label="AVG CONFIDENCE"
                value={`${stats.avg_confidence}%`}
              />
              <StatsPanel
                icon={<TrendingUp className="w-5 h-5" />}
                label="ACTIVE MATCHES"
                value={matches.length}
              />
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        <div className="mb-6">
          <h2 className="font-heading text-2xl font-bold tracking-tight text-foreground mb-2">
            UPCOMING MATCHES
          </h2>
          <p className="font-mono text-sm text-muted-foreground">
            Automated projections vs DFS lines • Highlighting value opportunities
          </p>
        </div>

        <div className="space-y-4">
          {matches.length === 0 ? (
            <div className="text-center py-12 border border-border rounded-sm bg-card">
              <AlertCircle className="w-12 h-12 text-muted-foreground mx-auto mb-4" />
              <p className="font-mono text-muted-foreground">NO MATCHES AVAILABLE</p>
            </div>
          ) : (
            matches.map((matchData, index) => (
              <MatchStrip key={matchData.match.id} matchData={matchData} index={index} />
            ))
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-border bg-card/30 mt-12">
        <div className="container mx-auto px-6 py-6">
          <p className="font-mono text-xs text-center text-muted-foreground tracking-widest uppercase">
            AUTOMATED DATA REFRESH • DFS LINE COMPARISON • STATISTICAL PROJECTIONS
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Dashboard;