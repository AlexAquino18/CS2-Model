import { useState } from 'react';
import { Upload, Save, AlertCircle, CheckCircle2 } from 'lucide-react';

const AdminPanel = () => {
  const [underdogText, setUnderdogText] = useState('');
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    setLoading(true);
    setStatus(null);

    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/admin/update-underdog`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ lines_text: underdogText }),
      });

      const data = await response.json();

      if (response.ok) {
        setStatus({
          type: 'success',
          message: `✅ Successfully updated ${data.count} Underdog lines!`,
        });
      } else {
        setStatus({
          type: 'error',
          message: `❌ Error: ${data.error || 'Failed to update lines'}`,
        });
      }
    } catch (error) {
      setStatus({
        type: 'error',
        message: `❌ Error: ${error.message}`,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl sm:text-4xl font-bold text-foreground flex items-center gap-3">
            <Upload className="w-8 h-8 text-primary" />
            Admin Panel - Update Underdog Lines
          </h1>
          <p className="mt-2 text-muted-foreground">
            Paste your Underdog lines here to update the system
          </p>
        </div>

        {/* Instructions */}
        <div className="bg-card border border-border rounded-lg p-6 mb-6">
          <h2 className="text-xl font-semibold text-foreground mb-4">How to Update Lines:</h2>
          
          <div className="space-y-3 text-sm text-muted-foreground">
            <div className="flex items-start gap-2">
              <span className="font-bold text-primary">1.</span>
              <p>Copy lines from your notes app or Underdog Fantasy website</p>
            </div>
            
            <div className="flex items-start gap-2">
              <span className="font-bold text-primary">2.</span>
              <p>Paste into the text box below in this format:</p>
            </div>
            
            <div className="ml-6 bg-background rounded p-3 font-mono text-xs border border-border">
              <div>PlayerName, kills, 28.5, TeamName</div>
              <div>PlayerName, headshots, 15.5, TeamName</div>
              <div>AnotherPlayer, kills, 30.5, OtherTeam</div>
            </div>
            
            <div className="flex items-start gap-2">
              <span className="font-bold text-primary">3.</span>
              <p>Click "Update Lines" - system will parse and store them</p>
            </div>

            <div className="flex items-start gap-2">
              <span className="font-bold text-primary">4.</span>
              <p>Refresh the dashboard to see updated projections with new Underdog lines</p>
            </div>
          </div>

          <div className="mt-4 p-3 bg-accent/10 border border-accent rounded">
            <p className="text-sm text-foreground">
              <strong>Supported Formats:</strong> CSV, line-separated, or freeform text. 
              The system will intelligently parse player names, stats, and values.
            </p>
          </div>
        </div>

        {/* Status Message */}
        {status && (
          <div
            className={`mb-6 p-4 rounded-lg border-2 flex items-center gap-3 ${
              status.type === 'success'
                ? 'bg-green-50 border-green-400 text-green-800'
                : 'bg-red-50 border-red-400 text-red-800'
            }`}
          >
            {status.type === 'success' ? (
              <CheckCircle2 className="w-5 h-5" />
            ) : (
              <AlertCircle className="w-5 h-5" />
            )}
            <p>{status.message}</p>
          </div>
        )}

        {/* Text Input */}
        <div className="bg-card border border-border rounded-lg p-6">
          <label className="block text-sm font-medium text-foreground mb-2">
            Paste Underdog Lines Here:
          </label>
          
          <textarea
            value={underdogText}
            onChange={(e) => setUnderdogText(e.target.value)}
            placeholder="DSSj, kills, 28.5, ARCRED
DSSj, headshots, 15.5, ARCRED
Djon8, kills, 32.5, SPARTA
Djon8, headshots, 18.5, SPARTA
..."
            className="w-full h-96 px-4 py-3 bg-background border border-border rounded-lg text-foreground font-mono text-sm focus:outline-none focus:ring-2 focus:ring-primary"
          />

          <div className="mt-4 flex items-center justify-between">
            <p className="text-sm text-muted-foreground">
              {underdogText.split('\n').filter(line => line.trim()).length} lines entered
            </p>

            <button
              onClick={handleSubmit}
              disabled={loading || !underdogText.trim()}
              className="px-6 py-3 bg-primary text-primary-foreground rounded-lg font-semibold hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 transition-all"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary-foreground"></div>
                  Updating...
                </>
              ) : (
                <>
                  <Save className="w-4 h-4" />
                  Update Lines
                </>
              )}
            </button>
          </div>
        </div>

        {/* Back Button */}
        <div className="mt-6">
          <button
            onClick={() => window.location.href = '/'}
            className="text-primary hover:text-primary/80 transition-colors"
          >
            ← Back to Dashboard
          </button>
        </div>
      </div>
    </div>
  );
};

export default AdminPanel;
