import { useState } from 'react'
import { useZoneInsights } from '../hooks/useApi'

export default function InsightsPage() {
  const fieldId = 'field_001'
  const { data, isLoading } = useZoneInsights(fieldId)
  
  // Filter state: 'all', 'critical', 'warning', 'healthy', or combinations
  const [activeFilters, setActiveFilters] = useState(new Set(['all']))

  const toggleFilter = (filter) => {
    const newFilters = new Set(activeFilters)
    
    if (filter === 'all') {
      // If 'all' is selected, clear other filters
      setActiveFilters(new Set(['all']))
    } else {
      // Remove 'all' if selecting specific filters
      newFilters.delete('all')
      
      // Toggle the specific filter
      if (newFilters.has(filter)) {
        newFilters.delete(filter)
      } else {
        newFilters.add(filter)
      }
      
      // If no filters selected, default to 'all'
      if (newFilters.size === 0) {
        newFilters.add('all')
      }
      
      setActiveFilters(newFilters)
    }
  }

  const getStatusColor = (status) => {
    switch (status) {
      case 'critical':
        return 'border-red-300 bg-red-50'
      case 'warning':
        return 'border-amber-300 bg-amber-50'
      default:
        return 'border-green-300 bg-green-50'
    }
  }

  const getStatusBadge = (status) => {
    switch (status) {
      case 'critical':
        return <span className="px-2 py-1 bg-red-100 text-red-700 rounded text-xs font-medium">🚨 Critical</span>
      case 'warning':
        return <span className="px-2 py-1 bg-amber-100 text-amber-700 rounded text-xs font-medium">⚠️ Warning</span>
      default:
        return <span className="px-2 py-1 bg-green-100 text-green-700 rounded text-xs font-medium">✅ Healthy</span>
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[500px]">
        <div className="text-center">
          <div className="animate-spin text-4xl mb-2">⏳</div>
          <p className="text-gray-600">Loading zone insights...</p>
        </div>
      </div>
    )
  }

  const zones = data?.grid_zones || []
  const summary = data?.summary || { healthy_zones: 0, warning_zones: 0, critical_zones: 0 }

  // Filter zones based on active filters
  const filteredZones = activeFilters.has('all') 
    ? zones 
    : zones.filter(zone => activeFilters.has(zone.status))

  const getFilterButtonClass = (filter) => {
    const isActive = activeFilters.has(filter)
    const baseClass = "px-4 py-2 rounded-lg font-semibold transition-all duration-200 flex items-center gap-2 shadow-md hover:shadow-lg transform hover:-translate-y-0.5"
    
    if (filter === 'all') {
      return `${baseClass} ${isActive 
        ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white shadow-blue-300 scale-105' 
        : 'bg-white text-gray-700 border-2 border-blue-200 hover:border-blue-400 hover:bg-blue-50'}`
    } else if (filter === 'critical') {
      return `${baseClass} ${isActive 
        ? 'bg-gradient-to-r from-red-500 to-red-600 text-white shadow-red-300 scale-105' 
        : 'bg-white text-red-700 border-2 border-red-300 hover:border-red-500 hover:bg-red-50'}`
    } else if (filter === 'warning') {
      return `${baseClass} ${isActive 
        ? 'bg-gradient-to-r from-amber-500 to-amber-600 text-white shadow-amber-300 scale-105' 
        : 'bg-white text-amber-700 border-2 border-amber-300 hover:border-amber-500 hover:bg-amber-50'}`
    } else if (filter === 'healthy') {
      return `${baseClass} ${isActive 
        ? 'bg-gradient-to-r from-green-500 to-green-600 text-white shadow-green-300 scale-105' 
        : 'bg-white text-green-700 border-2 border-green-300 hover:border-green-500 hover:bg-green-50'}`
    }
  }

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl p-6 card-shadow">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Field Insights</h1>
        <p className="text-gray-600 mb-6">
          Detailed zone-by-zone analysis of your field health.
        </p>

        {/* Summary */}
        {/* <div className="grid grid-cols-3 gap-4 mb-6">
          <div className="bg-green-50 rounded-lg p-4 border-2 border-green-200">
            <p className="text-sm text-gray-700 mb-1">Healthy Zones</p>
            <p className="text-3xl font-bold text-green-600">{summary.healthy_zones}</p>
          </div>
          <div className="bg-amber-50 rounded-lg p-4 border-2 border-amber-200">
            <p className="text-sm text-gray-700 mb-1">Warning Zones</p>
            <p className="text-3xl font-bold text-amber-600">{summary.warning_zones}</p>
          </div>
          <div className="bg-red-50 rounded-lg p-4 border-2 border-red-200">
            <p className="text-sm text-gray-700 mb-1">Critical Zones</p>
            <p className="text-3xl font-bold text-red-600">{summary.critical_zones}</p>
          </div>
        </div> */}

        {/* Filter Buttons */}
        <div className="mb-6 p-5 bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 rounded-2xl border-2 border-indigo-200 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-base font-bold text-indigo-900 flex items-center gap-2">
              🔍 Filter Zones
            </h3>
            <span className="text-sm font-semibold text-indigo-700 bg-white px-3 py-1 rounded-full shadow-sm">
              {filteredZones.length} of {zones.length} zones
            </span>
          </div>
          <div className="flex flex-wrap gap-3">
            <button
              onClick={() => toggleFilter('all')}
              className={getFilterButtonClass('all')}
            >
              <span>📊 All Zones</span>
              <span className={`px-2 py-0.5 rounded-md text-sm font-bold ${
                activeFilters.has('all') 
                  ? 'bg-white bg-opacity-25 text-white' 
                  : 'bg-blue-100 text-blue-700'
              }`}>
                {zones.length}
              </span>
            </button>
                        
            <button
              onClick={() => toggleFilter('healthy')}
              className={getFilterButtonClass('healthy')}
            >
              <span>✅ Healthy</span>
              <span className={`px-2 py-0.5 rounded-md text-sm font-bold ${
                activeFilters.has('healthy') 
                  ? 'bg-white bg-opacity-25 text-white' 
                  : 'bg-green-100 text-green-700'
              }`}>
                {summary.healthy_zones}
              </span>
            </button>

            <button
              onClick={() => toggleFilter('warning')}
              className={getFilterButtonClass('warning')}
            >
              <span>⚠️ Warning</span>
              <span className={`px-2 py-0.5 rounded-md text-sm font-bold ${
                activeFilters.has('warning') 
                  ? 'bg-white bg-opacity-25 text-white' 
                  : 'bg-amber-100 text-amber-700'
              }`}>
                {summary.warning_zones}
              </span>
            </button>

            <button
              onClick={() => toggleFilter('critical')}
              className={getFilterButtonClass('critical')}
            >
              <span>🚨 Critical</span>
              <span className={`px-2 py-0.5 rounded-md text-sm font-bold ${
                activeFilters.has('critical') 
                  ? 'bg-white bg-opacity-25 text-white' 
                  : 'bg-red-100 text-red-700'
              }`}>
                {summary.critical_zones}
              </span>
            </button>
          </div>
          {!activeFilters.has('all') && (
            <p className="text-xs text-indigo-700 mt-4 italic flex items-center gap-1 bg-white bg-opacity-60 px-3 py-2 rounded-lg">
              💡 <span className="font-medium">Tip:</span> Click multiple filters to combine them, or click "All Zones" to show everything
            </p>
          )}
        </div>

        {/* Zone Grid */}
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Zone Details
          {!activeFilters.has('all') && (
            <span className="ml-2 text-sm font-normal text-gray-600">
              (Filtered)
            </span>
          )}
        </h2>
        
        {filteredZones.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 text-center">
            <div className="text-6xl mb-4">🔍</div>
            <p className="text-xl font-semibold text-gray-700 mb-2">No zones match your filter</p>
            <p className="text-gray-500 mb-4">Try selecting different filter options above</p>
            <button
              onClick={() => setActiveFilters(new Set(['all']))}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Show All Zones
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 max-h-[600px] overflow-y-auto">
            {filteredZones.map((zone) => (
              <div
                key={zone.zone_id}
                className={`border-2 rounded-lg p-4 ${getStatusColor(zone.status)} transition-all duration-200 hover:shadow-lg`}
              >
                <div className="flex justify-between items-start mb-2">
                  <span className="text-sm font-semibold text-gray-900">{zone.zone_id}</span>
                  {getStatusBadge(zone.status)}
                </div>
                
                <div className="space-y-2">
                  <div>
                    <p className="text-xs text-gray-600">Canopy Coverage</p>
                    <p className="text-lg font-bold text-gray-900">{zone.avg_canopy}%</p>
                  </div>
                  
                  <div>
                    <p className="text-xs text-gray-600">Pests Detected</p>
                    <p className="text-lg font-bold text-gray-900">
                      {zone.pest_count !== undefined ? zone.pest_count : Math.round(zone.pest_density || 0)}
                      {((zone.pest_count !== undefined ? zone.pest_count : Math.round(zone.pest_density || 0)) > 0) && (
                        <span className="text-sm text-gray-600 ml-1">pests</span>
                      )}
                    </p>
                  </div>

                  <div>
                    <p className="text-xs text-gray-600">Risk Level</p>
                    <p className="text-sm font-medium text-gray-700 capitalize">{zone.risk_level}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
        
        {/* Showing filtered zones count */}
      </div>

      {/* Recommendations */}
      <div className="bg-white rounded-xl p-6 card-shadow">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Recommendations</h2>
        <div className="space-y-3">
          {summary.critical_zones > 0 && (
            <div className="flex items-start space-x-3 p-4 bg-red-50 rounded-lg border border-red-200">
              <span className="text-2xl">🚨</span>
              <div>
                <p className="font-semibold text-red-900">Immediate Action Required</p>
                <p className="text-sm text-red-700">
                  {summary.critical_zones} zones need urgent attention. Consider targeted pesticide
                  application and irrigation checks.
                </p>
              </div>
            </div>
          )}
          
          {summary.warning_zones > 0 && (
            <div className="flex items-start space-x-3 p-4 bg-amber-50 rounded-lg border border-amber-200">
              <span className="text-2xl">⚠️</span>
              <div>
                <p className="font-semibold text-amber-900">Monitor Closely</p>
                <p className="text-sm text-amber-700">
                  {summary.warning_zones} zones showing warning signs. Schedule inspection and
                  preventive measures.
                </p>
              </div>
            </div>
          )}

          {summary.healthy_zones === zones.length && (
            <div className="flex items-start space-x-3 p-4 bg-green-50 rounded-lg border border-green-200">
              <span className="text-2xl">✅</span>
              <div>
                <p className="font-semibold text-green-900">Field is Healthy</p>
                <p className="text-sm text-green-700">
                  All zones are performing well. Continue regular monitoring and maintenance.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
