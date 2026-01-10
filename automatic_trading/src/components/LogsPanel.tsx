import { useState } from 'react'
import { Terminal, Info, CheckCircle, AlertTriangle, XCircle } from 'lucide-react'
import { LogEntry } from '../services/api'

const LogsPanel = () => {
  const [logs] = useState<LogEntry[]>([])
  const [loading] = useState(true)

  // Don't auto-fetch logs - only load manually
  // Remove automatic fetching to prevent unnecessary API calls

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
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-lg bg-accent-primary/10 flex items-center justify-center">
          <Terminal className="w-5 h-5 text-accent-primary" />
        </div>
        <div>
          <h1 className="text-2xl font-bold">System Logs</h1>
          <p className="text-sm text-gray-500 mt-1">Real-time execution logs and system events</p>
        </div>
      </div>

      <div className="glass rounded-2xl border border-dark-border p-6">
        <div className="bg-dark-bg rounded-xl p-4 font-mono text-sm space-y-2 max-h-[600px] overflow-y-auto">
          {loading ? (
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
