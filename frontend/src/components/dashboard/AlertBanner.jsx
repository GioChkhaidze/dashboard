import { useState, useEffect } from 'react'
import { AlertTriangle, ChevronDown, ChevronUp, X } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

export default function AlertBanner({ alerts = [] }) {
  const [isExpanded, setIsExpanded] = useState(false)
  const [dismissedCritical, setDismissedCritical] = useState(false)
  const [dismissedWarnings, setDismissedWarnings] = useState(false)
  const [dismissedAlertIds, setDismissedAlertIds] = useState(new Set())
  const navigate = useNavigate()
  
  // Reset dismissed state when new alerts arrive
  useEffect(() => {
    const alertIds = alerts.map(a => a.alert_id).join(',')
    const storedDismissed = sessionStorage.getItem('dismissedAlerts')
    if (storedDismissed) {
      setDismissedAlertIds(new Set(JSON.parse(storedDismissed)))
    }
  }, [alerts])

  // Filter out individually dismissed alerts
  const activeAlerts = alerts.filter(a => !dismissedAlertIds.has(a.alert_id))
  
  if (!activeAlerts || activeAlerts.length === 0) {
    return null
  }

  const criticalAlerts = activeAlerts.filter(a => a.severity === 'critical')
  const warningAlerts = activeAlerts.filter(a => a.severity === 'warning')
  
  // Handle dismissing entire critical alert group
  const handleDismissCritical = () => {
    setDismissedCritical(true)
    // Store dismissed state in session storage so it persists during the session
    const newDismissed = new Set(dismissedAlertIds)
    criticalAlerts.forEach(a => newDismissed.add(a.alert_id))
    setDismissedAlertIds(newDismissed)
    sessionStorage.setItem('dismissedAlerts', JSON.stringify([...newDismissed]))
  }
  
  // Handle dismissing entire warning group
  const handleDismissWarnings = () => {
    setDismissedWarnings(true)
    const newDismissed = new Set(dismissedAlertIds)
    warningAlerts.forEach(a => newDismissed.add(a.alert_id))
    setDismissedAlertIds(newDismissed)
    sessionStorage.setItem('dismissedAlerts', JSON.stringify([...newDismissed]))
  }
  
  // Group alerts by zone to reduce clutter
  const groupedAlerts = criticalAlerts.reduce((acc, alert) => {
    const zoneId = alert.zone_id
    if (!acc[zoneId]) {
      acc[zoneId] = []
    }
    acc[zoneId].push(alert)
    return acc
  }, {})
  
  const uniqueZones = Object.keys(groupedAlerts).length
  const displayCount = 3 // Show top 3 zones when collapsed

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical':
        return 'bg-gradient-to-r from-red-50 to-red-100 border-red-200 text-red-900'
      case 'warning':
        return 'bg-gradient-to-r from-amber-50 to-amber-100 border-amber-200 text-amber-900'
      default:
        return 'bg-gradient-to-r from-blue-50 to-blue-100 border-blue-200 text-blue-900'
    }
  }

  return (
    <div className="space-y-3 mb-6">
      {criticalAlerts.length > 0 && !dismissedCritical && (
        <div className={`rounded-lg border p-4 ${getSeverityColor('critical')} transition-all duration-300 animate-in fade-in slide-in-from-top-2`}>
          <div className="flex items-start justify-between">
            <div className="flex items-start space-x-3 flex-1">
              <div className="mt-0.5">
                <AlertTriangle className="w-5 h-5 text-red-600 animate-pulse" />
              </div>
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <h3 className="font-semibold text-red-900">
                    {criticalAlerts.length} Critical Alert{criticalAlerts.length > 1 ? 's' : ''} in {uniqueZones} Zone{uniqueZones > 1 ? 's' : ''}
                  </h3>
                  <button
                    onClick={() => navigate('/insights')}
                    className="text-sm text-red-700 hover:text-red-900 font-medium underline"
                  >
                    View All →
                  </button>
                </div>
                
                {/* Summary view when collapsed */}
                {!isExpanded && (
                  <div className="mt-2">
                    <p className="text-sm text-red-800">
                      High pest activity detected. {Object.entries(groupedAlerts).slice(0, displayCount).map(([zone]) => zone).join(', ')}
                      {uniqueZones > displayCount && ` and ${uniqueZones - displayCount} more zones`} require attention.
                    </p>
                  </div>
                )}
                
                {/* Detailed view when expanded */}
                {isExpanded && (
                  <div className="mt-2 space-y-2 max-h-96 overflow-y-auto">
                    {criticalAlerts.slice(0, 10).map((alert, idx) => (
                      <div key={idx} className="text-sm border-t border-red-200 pt-2">
                        <p className="font-medium">{alert.message}</p>
                        <p className="text-red-700 mt-1">💡 {alert.recommendation}</p>
                      </div>
                    ))}
                    {criticalAlerts.length > 10 && (
                      <p className="text-sm text-red-700 italic">
                        + {criticalAlerts.length - 10} more alerts...
                      </p>
                    )}
                  </div>
                )}
                
                {/* Toggle button */}
                {criticalAlerts.length > 0 && (
                  <button
                    onClick={() => setIsExpanded(!isExpanded)}
                    className="mt-2 text-sm text-red-700 hover:text-red-900 font-medium flex items-center gap-1"
                  >
                    {isExpanded ? (
                      <>Show Less <ChevronUp className="w-4 h-4" /></>
                    ) : (
                      <>Show Details <ChevronDown className="w-4 h-4" /></>
                    )}
                  </button>
                )}
              </div>
            </div>
            {/* Close button for critical alerts */}
            <button
              onClick={handleDismissCritical}
              className="ml-4 text-red-400 hover:text-red-600 transition-colors flex-shrink-0"
              title="Dismiss critical alerts"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>
      )}

      {warningAlerts.length > 0 && !dismissedWarnings && (
        <div className={`rounded-lg border p-4 ${getSeverityColor('warning')} transition-all duration-300 animate-in fade-in slide-in-from-top-2`}>
          <div className="flex items-start justify-between">
            <div className="flex items-start space-x-3 flex-1">
              <div className="mt-0.5">
                <AlertTriangle className="w-5 h-5 text-amber-600" />
              </div>
              <div className="flex-1">
                <h3 className="font-semibold text-amber-900">
                  {warningAlerts.length} Warning{warningAlerts.length > 1 ? 's' : ''}
                </h3>
                <div className="mt-2 space-y-2">
                  {warningAlerts.slice(0, 2).map((alert, idx) => (
                    <p key={idx} className="text-sm">{alert.message}</p>
                  ))}
                </div>
              </div>
            </div>
            {/* Close button for warnings */}
            <button
              onClick={handleDismissWarnings}
              className="ml-4 text-amber-400 hover:text-amber-600 transition-colors flex-shrink-0"
              title="Dismiss warnings"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
