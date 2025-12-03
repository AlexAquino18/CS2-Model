import { useEffect, useState } from 'react';
import { ArrowUpIcon, ArrowDownIcon, MinusIcon, TrendingUpIcon } from 'lucide-react';

const LineMovements = () => {
  const [movements, setMovements] = useState([]);
  const [significantMovements, setSignificantMovements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all'); // 'all', 'significant', 'up', 'down'
  const [stats, setStats] = useState(null);

  useEffect(() => {
    fetchLineMovements();
    // Refresh every 30 seconds
    const interval = setInterval(fetchLineMovements, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchLineMovements = async () => {
    try {
      const [movementsRes, significantRes] = await Promise.all([
        fetch(`${process.env.REACT_APP_BACKEND_URL}/api/line-movements`),
        fetch(`${process.env.REACT_APP_BACKEND_URL}/api/line-movements/significant`)
      ]);

      const movementsData = await movementsRes.json();
      const significantData = await significantRes.json();

      setMovements(movementsData.movements || []);
      setSignificantMovements(significantData.significant_movements || []);
      setStats(movementsData.tracker_stats);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching line movements:', error);
      setLoading(false);
    }
  };

  const getFilteredMovements = () => {
    let filtered = movements;

    switch (filter) {
      case 'significant':
        return significantMovements;
      case 'up':
        return movements.filter(m => m.movement_direction === 'up');
      case 'down':
        return movements.filter(m => m.movement_direction === 'down');
      default:
        return movements;
    }
  };

  const getMovementIcon = (direction) => {
    switch (direction) {
      case 'up':
        return <ArrowUpIcon className="w-5 h-5 text-green-500" />;
      case 'down':
        return <ArrowDownIcon className="w-5 h-5 text-red-500" />;
      case 'new':
        return <span className="text-blue-500 text-xs font-semibold">NEW</span>;
      default:
        return <MinusIcon className="w-5 h-5 text-gray-400" />;
    }
  };

  const getMovementColor = (direction, isSignificant) => {
    if (isSignificant) {
      return direction === 'up' ? 'bg-green-100 border-green-400' : 'bg-red-100 border-red-400';
    }
    return 'bg-background border-border';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background p-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
            <p className="mt-4 text-muted-foreground">Loading line movements...</p>
          </div>
        </div>
      </div>
    );
  }

  const filteredMovements = getFilteredMovements();

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="bg-card border-b border-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl sm:text-4xl font-bold text-foreground flex items-center gap-3">
                <TrendingUpIcon className="w-8 h-8 text-primary" />
                PrizePicks Line Movements
              </h1>
              <p className="mt-2 text-muted-foreground">
                Track how betting lines are moving in real-time
              </p>
            </div>
            <button
              onClick={fetchLineMovements}
              className="px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 transition-colors"
            >
              Refresh
            </button>
          </div>

          {/* Stats Summary */}
          {stats && (
            <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-background rounded-lg p-4 border border-border">
                <p className="text-sm text-muted-foreground">Tracked Players</p>
                <p className="text-2xl font-bold text-foreground">{stats.tracked_players}</p>
              </div>
              <div className="bg-background rounded-lg p-4 border border-border">
                <p className="text-sm text-muted-foreground">Total Lines</p>
                <p className="text-2xl font-bold text-foreground">{stats.tracked_stat_lines}</p>
              </div>
              <div className="bg-background rounded-lg p-4 border border-border">
                <p className="text-sm text-muted-foreground">Movements Detected</p>
                <p className="text-2xl font-bold text-foreground">{stats.movements_detected}</p>
              </div>
              <div className="bg-background rounded-lg p-4 border border-border">
                <p className="text-sm text-muted-foreground">Significant Moves</p>
                <p className="text-2xl font-bold text-accent">{stats.significant_movements}</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Filter Buttons */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              filter === 'all'
                ? 'bg-primary text-primary-foreground'
                : 'bg-card text-foreground border border-border hover:bg-accent'
            }`}
          >
            All Movements ({movements.length})
          </button>
          <button
            onClick={() => setFilter('significant')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              filter === 'significant'
                ? 'bg-primary text-primary-foreground'
                : 'bg-card text-foreground border border-border hover:bg-accent'
            }`}
          >
            🔥 Significant ({significantMovements.length})
          </button>
          <button
            onClick={() => setFilter('up')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              filter === 'up'
                ? 'bg-primary text-primary-foreground'
                : 'bg-card text-foreground border border-border hover:bg-accent'
            }`}
          >
            ↑ Moving Up ({movements.filter(m => m.movement_direction === 'up').length})
          </button>
          <button
            onClick={() => setFilter('down')}
            className={`px-4 py-2 rounded-lg transition-colors ${
              filter === 'down'
                ? 'bg-primary text-primary-foreground'
                : 'bg-card text-foreground border border-border hover:bg-accent'
            }`}
          >
            ↓ Moving Down ({movements.filter(m => m.movement_direction === 'down').length})
          </button>
        </div>

        {/* Movements List */}
        <div className="mt-6 space-y-3">
          {filteredMovements.length === 0 ? (
            <div className="text-center py-12 bg-card rounded-lg border border-border">
              <p className="text-muted-foreground">No movements detected yet. Lines will be tracked on refresh.</p>
            </div>
          ) : (
            filteredMovements.map((movement, index) => (
              <div
                key={index}
                className={`p-4 rounded-lg border-2 transition-all ${getMovementColor(
                  movement.movement_direction,
                  movement.is_significant
                )}`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4 flex-1">
                    {/* Movement Icon */}
                    <div className="flex-shrink-0">
                      {getMovementIcon(movement.movement_direction)}
                    </div>

                    {/* Player Info */}
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <h3 className="text-lg font-semibold text-foreground">
                          {movement.player_name}
                        </h3>
                        {movement.is_significant && (
                          <span className="px-2 py-1 bg-accent text-accent-foreground text-xs font-bold rounded">
                            BIG MOVE
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground capitalize">
                        {movement.stat_type} • {movement.platform}
                      </p>
                    </div>

                    {/* Line Movement Details */}
                    <div className="flex items-center gap-6">
                      {/* Previous Line */}
                      <div className="text-center">
                        <p className="text-xs text-muted-foreground">Previous</p>
                        <p className="text-lg font-mono text-foreground">
                          {movement.previous_line !== null ? movement.previous_line.toFixed(1) : '-'}
                        </p>
                      </div>

                      {/* Arrow */}
                      <div>
                        {movement.movement_direction === 'up' ? (
                          <ArrowUpIcon className="w-6 h-6 text-green-500" />
                        ) : movement.movement_direction === 'down' ? (
                          <ArrowDownIcon className="w-6 h-6 text-red-500" />
                        ) : (
                          <MinusIcon className="w-6 h-6 text-gray-400" />
                        )}
                      </div>

                      {/* Current Line */}
                      <div className="text-center">
                        <p className="text-xs text-muted-foreground">Current</p>
                        <p className="text-xl font-bold font-mono text-foreground">
                          {movement.current_line.toFixed(1)}
                        </p>
                      </div>

                      {/* Movement Amount */}
                      <div className="text-center min-w-[80px]">
                        <p className="text-xs text-muted-foreground">Change</p>
                        <p
                          className={`text-xl font-bold font-mono ${
                            movement.movement > 0
                              ? 'text-green-500'
                              : movement.movement < 0
                              ? 'text-red-500'
                              : 'text-gray-400'
                          }`}
                        >
                          {movement.movement > 0 ? '+' : ''}
                          {movement.movement.toFixed(1)}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Additional Info */}
                <div className="mt-3 flex items-center gap-4 text-xs text-muted-foreground">
                  <span>History: {movement.history_count} data points</span>
                  <span>•</span>
                  <span>
                    Last updated: {new Date(movement.last_updated).toLocaleTimeString()}
                  </span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default LineMovements;
