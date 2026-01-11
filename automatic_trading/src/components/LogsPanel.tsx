import { useState, useEffect } from 'react'
import { Terminal, Info, CheckCircle, AlertTriangle, XCircle, RefreshCw } from 'lucide-react'
import { LogEntry, apiService } from '../services/api'

const LogsPanel = () => {
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [loading, setLoading] = useState(false)
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)

  // Fetch logs function
  const fetchLogs = async () => {
    try {
      setLoading(true)
      const logs = await apiService.fetchLogs()
      setLogs(logs || [])
      setLastUpdated(new Date())
    } catch (error) {
      console.error('Error fetching logs:', error)
    } finally {
      setLoading(false)
    }
  }

  // Fetch logs on mount
  useEffect(() => {
    fetchLogs()
  }, [])

  const getLogIcon = (severity: string) => {
    switch (severity) {
      case 'success':
        return <CheckCircle className="w-4 h-4 text-accent-success" />
      case 'warning':
        return <AlertTriangle className="w-4 h-4 text-accent-warning" />
      case 'error':
        return <XCircle className="w-4 h-4 text-accent-danger" />
      default:
        return <Info className="w-4 h-4 text-accent-primary" />
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'success':
        return 'text-accent-success'
      case 'warning':
        return 'text-accent-warning'
      case 'error':
        return 'text-accent-danger'
      default:
        return 'text-gray-400'
    }
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-accent-primary/10 flex items-center justify-center">
            <Terminal className="w-5 h-5 text-accent-primary" />
          </div>
          <div>
            <h1 className="text-2xl font-bold">System Logs</h1>
            <p className="text-sm text-gray-500 mt-1">
              Real-time execution logs and system events
              {lastUpdated && (
                <span className="ml-2">
                  • Last updated: {lastUpdated.toLocaleTimeString()}
                </span>
              )}
            </p>
          </div>
        </div>
        
        <button
          onClick={fetchLogs}
          disabled={loading}
          className="px-4 py-2 bg-accent-primary hover:bg-accent-primary/80 disabled:bg-accent-primary/50 text-white rounded-lg transition-colors flex items-center gap-2"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          {loading ? 'Refreshing...' : 'Refresh Logs'}
        </button>
      </div>

      <div className="glass rounded-2xl border border-dark-border p-6">
        <div className="bg-dark-bg rounded-xl p-4 font-mono text-sm space-y-2 max-h-[600px] overflow-y-auto">
          {loading && logs.length === 0 ? (
            <div className="text-center text-gray-500 py-8">Loading logs...</div>
          ) : logs.length === 0 ? (
            <div className="text-center text-gray-500 py-8">No logs available</div>
          ) : (
            logs.map((log) => (
            <div key={log.id} className="flex items-start gap-3 py-2 hover:bg-dark-elevated px-2 rounded transition-colors">
              <span className="text-gray-600 text-xs mt-0.5">{log.timestamp}</span>
              <div className="flex items-center gap-2 flex-shrink-0">
                {getLogIcon(log.severity)}
              </div>
              <span className={getSeverityColor(log.severity)}>{log.message}</span>
            </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}

export default LogsPanel
