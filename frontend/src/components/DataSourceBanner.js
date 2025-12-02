import { useEffect, useState } from "react";
import axios from "axios";
import { AlertCircle, CheckCircle, XCircle, Info } from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const DataSourceBanner = () => {
  const [status, setStatus] = useState(null);
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await axios.get(`${API}/scraping-status`);
        setStatus(response.data);
      } catch (error) {
        console.error("Error fetching scraping status:", error);
      }
    };

    fetchStatus();
  }, []);

  if (!status) return null;

  const isUsingMockData = status.data_mode === "mock";
  const sources = status.status;

  return (
    <div className={`border-b ${isUsingMockData ? 'border-accent/30 bg-accent/5' : 'border-border bg-card/30'}`}>
      <div className="container mx-auto px-6 py-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            {isUsingMockData ? (
              <AlertCircle className="w-5 h-5 text-accent" />
            ) : (
              <Info className="w-5 h-5 text-primary" />
            )}
            <div>
              <p className="font-mono text-sm font-medium text-foreground">
                {isUsingMockData ? "DEMO MODE - Using Sample Data" : "LIVE DATA MODE"}
              </p>
              <p className="font-mono text-xs text-muted-foreground">
                {isUsingMockData 
                  ? "Real PrizePicks & HLTV data blocked by anti-scraping protection" 
                  : "Fetching data from live sources"}
              </p>
            </div>
          </div>
          <button
            data-testid="toggle-status-details"
            onClick={() => setExpanded(!expanded)}
            className="font-mono text-xs text-muted-foreground hover:text-primary transition-colors uppercase tracking-wider"
          >
            {expanded ? "HIDE DETAILS" : "SHOW DETAILS"}
          </button>
        </div>

        {expanded && (
          <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
            <SourceStatus
              name="HLTV (Matches)"
              success={sources.hltv?.success}
              error={sources.hltv?.error}
              lastAttempt={sources.hltv?.last_attempt}
            />
            <SourceStatus
              name="PrizePicks (Props)"
              success={sources.prizepicks?.success}
              error={sources.prizepicks?.error}
              lastAttempt={sources.prizepicks?.last_attempt}
            />
            <SourceStatus
              name="Underdog (Props)"
              success={sources.underdog?.success}
              error={sources.underdog?.error}
              lastAttempt={sources.underdog?.last_attempt}
            />
          </div>
        )}

        {expanded && isUsingMockData && (
          <div className="mt-4 p-4 border border-accent/30 rounded-sm bg-card">
            <p className="font-mono text-xs text-accent font-bold uppercase mb-2">How to get real data:</p>
            <ol className="font-mono text-xs text-muted-foreground space-y-1 list-decimal list-inside">
              <li>Visit PrizePicks.com and navigate to CS2 props</li>
              <li>Manually copy player names, stat types, and lines</li>
              <li>API scraping blocked due to Cloudflare/anti-bot protection</li>
              <li>Alternative: Use PrizePicks official API (requires authentication)</li>
            </ol>
          </div>
        )}
      </div>
    </div>
  );
};

const SourceStatus = ({ name, success, error, lastAttempt }) => {
  return (
    <div className="bg-card/50 border border-border rounded-sm p-3">
      <div className="flex items-center gap-2 mb-2">
        {success ? (
          <CheckCircle className="w-4 h-4 text-accent" />
        ) : (
          <XCircle className="w-4 h-4 text-destructive" />
        )}
        <p className="font-mono text-xs font-bold uppercase tracking-wider text-foreground">
          {name}
        </p>
      </div>
      <p className={`font-mono text-xs ${success ? 'text-accent' : 'text-destructive'}`}>
        {success ? "Connected" : "Unavailable"}
      </p>
      {error && (
        <p className="font-mono text-xs text-muted-foreground mt-1 truncate" title={error}>
          {error}
        </p>
      )}
      {lastAttempt && (
        <p className="font-mono text-xs text-muted-foreground mt-1">
          Last: {new Date(lastAttempt).toLocaleTimeString()}
        </p>
      )}
    </div>
  );
};

export default DataSourceBanner;
