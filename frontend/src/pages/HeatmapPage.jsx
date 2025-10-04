import { useState, useMemo, useEffect } from 'react'
import { usePestDaily, useCanopyDaily } from '../hooks/useApi'
import HeatmapCanvas from '../components/charts/HeatmapCanvas'

export default function HeatmapPage() {
  const fieldId = 'field_001'
  const [selectedLayer, setSelectedLayer] = useState('pests')
  const [selectedCropType, setSelectedCropType] = useState(null)
  
  const { data: pestData, isLoading: pestLoading } = usePestDaily(fieldId, null, selectedCropType)
  const { data: canopyData, isLoading: canopyLoading } = useCanopyDaily(fieldId)
  
  const isLoading = pestLoading || canopyLoading
  const heatmapGrid = pestData?.heatmap_grid || []
  const canopyGrid = canopyData?.grid_data || []
  const availableCropTypes = pestData?.available_crop_types || []
  const selectedCrop = pestData?.selected_crop_type || null
  const pestCountsByCrop = pestData?.pest_counts_by_crop || {}
  const criticalZonesCount = pestData?.critical_zones_count || 0
  const totalPestCount = pestData?.total_count || 0

  // Auto-select first crop type when data loads
  useEffect(() => {
    if (availableCropTypes.length > 0 && !selectedCropType) {
      setSelectedCropType(availableCropTypes[0])
    }
  }, [availableCropTypes, selectedCropType])

  // Get max density for color scaling
  const maxDensity = useMemo(() => {
    let max = 0
    heatmapGrid.forEach(row => {
      row.forEach(val => { if (val > max) max = val })
    })
    return max || 1
  }, [heatmapGrid])

  // Modern farmer-friendly color scale - green (safe) to red (danger)
  const getPestDensityColor = (density) => {
    if (density === 0) return 'rgba(16, 185, 129, 0.15)' // Very light green - safe area
    
    const normalized = density / maxDensity // 0 to 1
    
    if (normalized < 0.2) {
      // Safe zone: light green
      return `rgba(52, 211, 153, ${0.2 + normalized * 1.5})`
    } else if (normalized < 0.4) {
      // Low concern: yellow-green
      return `rgba(163, 230, 53, ${0.4 + normalized * 1.5})`
    } else if (normalized < 0.6) {
      // Moderate: yellow-orange
      return `rgba(251, 191, 36, ${0.5 + normalized * 1})`
    } else if (normalized < 0.8) {
      // High concern: orange-red
      return `rgba(251, 146, 60, ${0.6 + normalized * 0.8})`
    } else {
      // Critical hotspot: red
      return `rgba(239, 68, 68, ${0.7 + normalized * 0.3})`
    }
  }

  const getCanopyColor = (coverage) => {
    // Gradient from red (poor) to green (excellent)
    if (coverage < 40) return `rgba(220, 38, 38, ${0.7 + (40 - coverage) / 100})`
    if (coverage < 50) return `rgba(239, 68, 68, 0.7)`
    if (coverage < 60) return `rgba(251, 146, 60, 0.6)`
    if (coverage < 70) return `rgba(250, 204, 21, 0.5)`
    if (coverage < 80) return `rgba(132, 204, 22, 0.5)`
    return `rgba(34, 197, 94, ${0.4 + (coverage - 80) / 50})`
  }

  const renderHeatmap = () => {
    if (isLoading) {
      return (
        <div className="flex items-center justify-center h-full min-h-[500px]">
          <div className="text-center">
            <div className="animate-spin text-4xl mb-2">⏳</div>
            <p className="text-gray-600">Loading heatmap data...</p>
          </div>
        </div>
      )
    }

    if (!heatmapGrid.length && !canopyGrid.length) {
      return (
        <div className="flex items-center justify-center h-full min-h-[500px]">
          <p className="text-gray-500">No heatmap data available</p>
        </div>
      )
    }

    // Determine which data to display
    let displayData = heatmapGrid
    let colorScheme = 'pest'
    
    if (selectedLayer === 'canopy') {
      displayData = canopyGrid
      colorScheme = 'canopy'
    } else if (selectedLayer === 'overlay') {
      colorScheme = 'overlay'
    }

    // Dynamically size canvas based on grid dimensions so 50x50 maps to a sensible pixel size
    const gridWidth = displayData[0]?.length || 0
    const gridHeight = displayData.length
    // pixels per cell - increased to 15 so 50x50 -> 750 canvas (fills board better with larger boxes)
    const ppc = 15
    const minCanvas = 400
    const maxCanvas = 1400
    const canvasWidth = Math.min(maxCanvas, Math.max(minCanvas, Math.round(gridWidth * ppc)))
    const canvasHeight = Math.min(maxCanvas, Math.max(minCanvas, Math.round(gridHeight * ppc)))

    return (
      <div className="flex justify-center bg-white p-6 rounded-lg">
        <HeatmapCanvas
          data={displayData}
          width={canvasWidth}
          height={canvasHeight}
          colorScheme={colorScheme}
          maxDensity={maxDensity}
          onCellClick={(cell) => {
            console.log('Clicked cell:', cell)
          }}
        />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="bg-gradient-to-br from-white to-slate-50 rounded-2xl p-8 shadow-xl border border-slate-200 max-w-6xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold text-slate-900 mb-2">🗺️ Field Health Monitor</h1>
            <p className="text-slate-600">
              Real-time visualization of pest infestation zones and crop health across your field
            </p>
          </div>
        </div>

        <div className="flex flex-wrap gap-3 mb-6">
          <button 
            onClick={() => setSelectedLayer('pests')}
            className={`px-6 py-3 rounded-xl font-semibold transition-all shadow-md hover:shadow-lg transform hover:scale-105 ${
              selectedLayer === 'pests' 
                ? 'bg-gradient-to-r from-red-500 to-red-600 text-white shadow-red-300' 
                : 'bg-white text-slate-700 hover:bg-slate-50 border border-slate-200'
            }`}
          >
            🐛 Pest Infestation Map
          </button>
          <button 
            onClick={() => setSelectedLayer('canopy')}
            className={`px-6 py-3 rounded-xl font-semibold transition-all shadow-md hover:shadow-lg transform hover:scale-105 ${
              selectedLayer === 'canopy' 
                ? 'bg-gradient-to-r from-green-500 to-green-600 text-white shadow-green-300' 
                : 'bg-white text-slate-700 hover:bg-slate-50 border border-slate-200'
            }`}
          >
            🌱 Crop Coverage
          </button>
          <button 
            onClick={() => setSelectedLayer('overlay')}
            className={`px-6 py-3 rounded-xl font-semibold transition-all shadow-md hover:shadow-lg transform hover:scale-105 ${
              selectedLayer === 'overlay' 
                ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white shadow-blue-300' 
                : 'bg-white text-slate-700 hover:bg-slate-50 border border-slate-200'
            }`}
          >
            🗺️ Combined View
          </button>
          {selectedLayer === 'pests' && availableCropTypes.length > 0 && (
            <div className="flex items-center gap-2">
              <label className="text-sm font-medium text-slate-700">Crop Type:</label>
              <select
                value={selectedCropType || ''}
                onChange={(e) => setSelectedCropType(e.target.value)}
                className="px-4 py-2 rounded-lg border-2 border-slate-300 bg-white text-slate-700 font-medium focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all"
              >
                {availableCropTypes.map(crop => (
                  <option key={crop} value={crop} className="capitalize">
                    {crop.charAt(0).toUpperCase() + crop.slice(1)}
                  </option>
                ))}
              </select>
            </div>
          )}
        </div>

        {!isLoading && pestData && canopyData && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-gradient-to-br from-red-50 to-red-100 rounded-lg p-4">
              <p className="text-sm font-medium text-red-700 mb-1">🐛 Pest Detections</p>
              <p className="text-3xl font-bold text-red-700">{totalPestCount}</p>
            </div>
            <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-4">
              <p className="text-sm font-medium text-green-700 mb-1">🌱 Avg Canopy</p>
              {/* canopy API returns statistics.avg; dashboard KPIs return avg_canopy_cover.
                  Prefer statistics.avg if available, otherwise fall back to avg_canopy_cover or aggregates */}
              <p className="text-3xl font-bold text-green-700">{(canopyData?.statistics?.avg ?? canopyData?.avg_coverage ?? canopyData?.avg_canopy_cover ?? 0).toFixed(1)}%</p>
            </div>
            <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-4">
              <p className="text-sm font-medium text-purple-700 mb-1">🐛 Selected Crop Pests</p>
              <p className="text-3xl font-bold text-purple-700">
                {selectedCropType ? (pestCountsByCrop[selectedCropType] ?? 0) : totalPestCount}
              </p>
              <p className="text-xs text-slate-500 mt-1">
                {selectedCropType ? `${selectedCropType.charAt(0).toUpperCase() + selectedCropType.slice(1)} pests` : 'Total pests across crops'}
              </p>
            </div>
            <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-4">
              <p className="text-sm font-medium text-blue-700 mb-1">📈 Max Density</p>
              <p className="text-3xl font-bold text-blue-700">{maxDensity.toFixed(1)}</p>
              <p className="text-xs text-slate-500 mt-1">Maximum cell density (heatmap)</p>
            </div>
          </div>
        )}

        {renderHeatmap()}

        {/* Legend */}
        <div className="mt-6 bg-white rounded-lg p-6 border-2 border-slate-200">
          {selectedLayer === 'pests' && (
            <div>
              <p className="text-sm font-semibold text-slate-700 mb-2">Pest Density Scale:</p>
              <div className="flex items-center gap-2">
                <span className="text-xs text-slate-600">Low</span>
                <div className="flex-1 h-8 rounded-lg overflow-hidden flex">
                  <div className="flex-1" style={{ background: 'linear-gradient(to right, rgba(52, 211, 153, 0.4), rgba(163, 230, 53, 0.7), rgba(251, 191, 36, 0.8), rgba(251, 146, 60, 0.9), rgba(239, 68, 68, 1))' }}></div>
                </div>
                <span className="text-xs text-slate-600">High</span>
              </div>
            </div>
          )}

          {selectedLayer === 'canopy' && (
            <div>
              <p className="text-sm font-semibold text-slate-700 mb-2">Canopy Coverage:</p>
              <div className="grid grid-cols-6 gap-2 text-xs">
                <div className="text-center">
                  <div className="w-full h-6 rounded" style={{ backgroundColor: 'rgba(220, 38, 38, 0.8)' }}></div>
                  <p className="mt-1 text-slate-600">&lt;40%</p>
                </div>
                <div className="text-center">
                  <div className="w-full h-6 rounded" style={{ backgroundColor: 'rgba(239, 68, 68, 0.7)' }}></div>
                  <p className="mt-1 text-slate-600">40-50%</p>
                </div>
                <div className="text-center">
                  <div className="w-full h-6 rounded" style={{ backgroundColor: 'rgba(251, 146, 60, 0.6)' }}></div>
                  <p className="mt-1 text-slate-600">50-60%</p>
                </div>
                <div className="text-center">
                  <div className="w-full h-6 rounded" style={{ backgroundColor: 'rgba(250, 204, 21, 0.5)' }}></div>
                  <p className="mt-1 text-slate-600">60-70%</p>
                </div>
                <div className="text-center">
                  <div className="w-full h-6 rounded" style={{ backgroundColor: 'rgba(132, 204, 22, 0.5)' }}></div>
                  <p className="mt-1 text-slate-600">70-80%</p>
                </div>
                <div className="text-center">
                  <div className="w-full h-6 rounded" style={{ backgroundColor: 'rgba(34, 197, 94, 0.6)' }}></div>
                  <p className="mt-1 text-slate-600">&gt;80%</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
