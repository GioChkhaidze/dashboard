import { useState } from 'react'
import { useDroneStatus } from '../hooks/useApi'
import FlightPathMap from '../components/drone/FlightPathMap'
import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

export default function DroneDetailsPage() {
  const { data, isLoading, refetch } = useDroneStatus()
  const [selectedTab, setSelectedTab] = useState('overview')
  const [togglingFlight, setTogglingFlight] = useState(false)

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin text-4xl mb-4">🚁</div>
          <p className="text-gray-600">Loading drone information...</p>
        </div>
      </div>
    )
  }

  const drone = data?.drone || {}
  const flightHistory = data?.flight_history || []
  const lastFlight = flightHistory[0] || {}

  // Toggle auto flight scheduling
  const handleToggleAutoFlight = async () => {
    setTogglingFlight(true)
    try {
      const response = await axios.post(
        `${API_BASE}/drone/toggle-auto-flight?drone_id=drone_001`,
        { enabled: !drone.auto_flight_enabled },
        { headers: { 'Content-Type': 'application/json' } }
      )
      
      // Show success message
      alert(response.data.message)
      
      // Refetch drone status
      await refetch()
    } catch (error) {
      console.error('Error toggling auto flight:', error)
      alert('Failed to toggle automatic flights. Please try again.')
    } finally {
      setTogglingFlight(false)
    }
  }

  // Battery status color
  const getBatteryColor = (level) => {
    if (level >= 70) return 'text-green-600 bg-green-50 border-green-200'
    if (level >= 40) return 'text-yellow-600 bg-yellow-50 border-yellow-200'
    return 'text-red-600 bg-red-50 border-red-200'
  }

  // Health status badge
  const getHealthBadge = (status) => {
    const badges = {
      excellent: { color: 'bg-green-100 text-green-800', icon: '✅', text: 'Excellent' },
      good: { color: 'bg-blue-100 text-blue-800', icon: '👍', text: 'Good' },
      fair: { color: 'bg-yellow-100 text-yellow-800', icon: '⚠️', text: 'Fair' },
      poor: { color: 'bg-red-100 text-red-800', icon: '⚠️', text: 'Needs Attention' }
    }
    return badges[status] || badges.good
  }

  const healthBadge = getHealthBadge(drone.health_status)
  const batteryColorClass = getBatteryColor(drone.battery_level)

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg shadow-lg p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">🚁 Drone Status & Details</h1>
            <p className="text-blue-100">Real-time monitoring of your DJI AGRAS T50</p>
          </div>
          <div className="flex items-center space-x-3">
            <button
              onClick={handleToggleAutoFlight}
              disabled={togglingFlight}
              className={`px-6 py-3 rounded-lg font-semibold transition-all shadow-lg transform hover:scale-105 ${
                drone.auto_flight_enabled
                  ? 'bg-red-500 hover:bg-red-600 text-white'
                  : 'bg-green-500 hover:bg-green-600 text-white'
              } ${togglingFlight ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              {togglingFlight ? (
                '⏳ Processing...'
              ) : drone.auto_flight_enabled ? (
                '🚫 Disable Auto Flights'
              ) : (
                '✅ Enable Auto Flights'
              )}
            </button>
          </div>
        </div>
        {drone.auto_flight_enabled && drone.next_scheduled_flight && (
          <div className="mt-3 bg-white bg-opacity-20 rounded px-4 py-2 text-sm">
            📅 Next scheduled flight: {new Date(drone.next_scheduled_flight).toLocaleString()}
          </div>
        )}
        {!drone.auto_flight_enabled && (
          <div className="mt-3 bg-yellow-500 bg-opacity-30 rounded px-4 py-2 text-sm">
            ⚠️ Automatic flights are currently disabled. Press the button above to resume scheduled missions.
          </div>
        )}
      </div>

      {/* Quick Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {/* Battery Level */}
        <div className={`bg-white rounded-lg shadow-md p-6 border-2 ${batteryColorClass}`}>
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium opacity-75">Battery Level</span>
            <span className="text-2xl">🔋</span>
          </div>
          <div className="text-3xl font-bold mb-2">{drone.battery_level}%</div>
          <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
            <div
              className={`h-2 rounded-full transition-all ${
                drone.battery_level >= 70 ? 'bg-green-500' :
                drone.battery_level >= 40 ? 'bg-yellow-500' : 'bg-red-500'
              }`}
              style={{ width: `${drone.battery_level}%` }}
            />
          </div>
          <p className="text-xs opacity-75">
            {drone.battery_level >= 70 ? 'Ready for flight' :
             drone.battery_level >= 40 ? 'Moderate charge' : 'Charge required'}
          </p>
        </div>

        {/* Flight Time */}
        <div className="bg-white rounded-lg shadow-md p-6 border-2 border-blue-200">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-600">Total Flight Time</span>
            <span className="text-2xl">⏱️</span>
          </div>
          <div className="text-3xl font-bold text-blue-600 mb-2">
            {drone.total_flight_hours || 0}h
          </div>
          <p className="text-xs text-gray-500">Accumulated hours</p>
        </div>

        {/* Distance Covered */}
        <div className="bg-white rounded-lg shadow-md p-6 border-2 border-purple-200">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-600">Last Flight Distance</span>
            <span className="text-2xl">📏</span>
          </div>
          <div className="text-3xl font-bold text-purple-600 mb-2">
            {lastFlight.distance_covered || 0} km
          </div>
          <p className="text-xs text-gray-500">
            {lastFlight.date ? new Date(lastFlight.date).toLocaleDateString() : 'N/A'}
          </p>
        </div>

        {/* Flights Completed */}
        <div className="bg-white rounded-lg shadow-md p-6 border-2 border-emerald-200">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-600">Total Flights</span>
            <span className="text-2xl">✈️</span>
          </div>
          <div className="text-3xl font-bold text-emerald-600 mb-2">
            {drone.total_flights || 0}
          </div>
          <p className="text-xs text-gray-500">Successful missions</p>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="bg-white rounded-lg shadow-md">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6" aria-label="Tabs">
            {[
              { id: 'overview', label: 'Overview', icon: '📊' },
              { id: 'camera', label: 'Camera & Sensors', icon: '📷' },
              { id: 'history', label: 'Flight History', icon: '📜' },
              { id: 'specs', label: 'Specifications', icon: '⚙️' }
            ].map(tab => (
              <button
                key={tab.id}
                onClick={() => setSelectedTab(tab.id)}
                className={`
                  py-4 px-1 border-b-2 font-medium text-sm transition-colors
                  ${selectedTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }
                `}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {/* Overview Tab */}
          {selectedTab === 'overview' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Drone Image */}
                <div className="bg-gray-50 rounded-lg p-6 border border-gray-200">
                  <h3 className="text-lg font-semibold mb-4 text-gray-800">Drone Visual</h3>
                  <div className="aspect-video bg-gradient-to-br from-gray-100 to-gray-200 rounded-lg flex items-center justify-center mb-4 overflow-hidden">
                    <img 
                      src={drone.image_url?.startsWith('http') ? drone.image_url : `http://localhost:8000${drone.image_url || '/static/drone.png'}`} 
                      alt={drone.model || 'DJI AGRAS T50'} 
                      className="w-full h-full object-contain p-4"
                      onError={(e) => {
                        e.target.onerror = null
                        e.target.src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200"><text x="50%" y="50%" text-anchor="middle" dy=".3em" font-size="48">🚁</text></svg>'
                      }}
                    />
                  </div>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Model:</span>
                      <span className="font-medium">{drone.model || 'DJI AGRAS T50'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Serial Number:</span>
                      <span className="font-medium">{drone.serial_number || 'N/A'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Firmware:</span>
                      <span className="font-medium">{drone.firmware_version || 'v3.2.1'}</span>
                    </div>
                  </div>
                </div>

                {/* Current Status */}
                <div className="space-y-4">
                  <div className="bg-gray-50 rounded-lg p-6 border border-gray-200">
                    <h3 className="text-lg font-semibold mb-4 text-gray-800">Current Status</h3>
                    <div className="space-y-3">
                      <div className="flex items-center justify-between p-3 bg-white rounded border">
                        <span className="text-gray-700">Operational Status</span>
                        <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                          drone.operational_status === 'active' ? 'bg-green-100 text-green-800' :
                          drone.operational_status === 'standby' ? 'bg-blue-100 text-blue-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {drone.operational_status === 'active' ? '🟢 Active' :
                           drone.operational_status === 'standby' ? '🔵 Standby' : '⚫ Offline'}
                        </span>
                      </div>
                      
                      <div className="flex items-center justify-between p-3 bg-white rounded border">
                        <span className="text-gray-700">Last Maintenance</span>
                        <span className="font-medium">
                          {drone.last_maintenance ? new Date(drone.last_maintenance).toLocaleDateString() : 'N/A'}
                        </span>
                      </div>

                      <div className="flex items-center justify-between p-3 bg-white rounded border">
                        <span className="text-gray-700">Next Service Due</span>
                        <span className="font-medium text-orange-600">
                          {drone.next_service_due ? new Date(drone.next_service_due).toLocaleDateString() : 'Not scheduled'}
                        </span>
                      </div>

                      <div className="flex items-center justify-between p-3 bg-white rounded border">
                        <span className="text-gray-700">GPS Status</span>
                        <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                          drone.gps_status === 'excellent' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                        }`}>
                          {drone.gps_status === 'excellent' ? '🛰️ Excellent' : '🛰️ Good'}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Health Check Details */}
              <div className="bg-gray-50 rounded-lg p-6 border border-gray-200">
                <h3 className="text-lg font-semibold mb-4 text-gray-800">🏥 Health Check</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {[
                    { label: 'Motor Health', value: drone.motor_health || 95, unit: '%', icon: '⚙️' },
                    { label: 'Propeller Condition', value: drone.propeller_health || 92, unit: '%', icon: '🔄' },
                    { label: 'Signal Strength', value: drone.signal_strength || 88, unit: '%', icon: '📶' }
                  ].map((item, idx) => (
                    <div key={idx} className="bg-white rounded-lg p-4 border">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm text-gray-600">{item.label}</span>
                        <span className="text-xl">{item.icon}</span>
                      </div>
                      <div className="text-2xl font-bold text-gray-800 mb-2">
                        {item.value}{item.unit}
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${
                            item.value >= 90 ? 'bg-green-500' :
                            item.value >= 70 ? 'bg-yellow-500' : 'bg-red-500'
                          }`}
                          style={{ width: `${item.value}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Flight Path Visualization */}
              <FlightPathMap fieldWidth={50} fieldHeight={50} />
            </div>
          )}

          {/* Camera & Sensors Tab */}
          {selectedTab === 'camera' && (
            <div className="space-y-6">
              <div className="bg-gray-50 rounded-lg p-6 border border-gray-200">
                <h3 className="text-lg font-semibold mb-4 text-gray-800">📷 Camera Specifications - DJI Zenmuse P1</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <div className="flex items-center justify-between p-4 bg-white rounded border">
                      <span className="text-gray-700">Camera Model</span>
                      <span className="font-medium">{drone.camera?.model || 'DJI Zenmuse P1'}</span>
                    </div>
                    <div className="flex items-center justify-between p-4 bg-white rounded border">
                      <span className="text-gray-700">Resolution</span>
                      <span className="font-medium">{drone.camera?.resolution || '45MP Full-Frame'}</span>
                    </div>
                    <div className="flex items-center justify-between p-4 bg-white rounded border">
                      <span className="text-gray-700">Sensor Type</span>
                      <span className="font-medium">{drone.camera?.sensor_type || 'CMOS Full-Frame'}</span>
                    </div>
                    <div className="flex items-center justify-between p-4 bg-white rounded border">
                      <span className="text-gray-700">Field of View</span>
                      <span className="font-medium">{drone.camera?.fov || '63.5° (35mm)'}</span>
                    </div>
                  </div>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between p-4 bg-white rounded border">
                      <span className="text-gray-700">Lens Quality</span>
                      <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                        drone.camera?.lens_quality === 'excellent' ? 'bg-green-100 text-green-800' : 'bg-blue-100 text-blue-800'
                      }`}>
                        {drone.camera?.lens_quality === 'excellent' ? '⭐ Excellent' : '👍 Good'}
                      </span>
                    </div>
                    <div className="flex items-center justify-between p-4 bg-white rounded border">
                      <span className="text-gray-700">Image Quality</span>
                      <span className="font-medium">{drone.camera?.image_quality || 98}%</span>
                    </div>
                    <div className="flex items-center justify-between p-4 bg-white rounded border">
                      <span className="text-gray-700">Stabilization</span>
                      <span className="font-medium">{drone.camera?.stabilization || '3-axis gimbal'}</span>
                    </div>
                    <div className="flex items-center justify-between p-4 bg-white rounded border">
                      <span className="text-gray-700">Last Calibration</span>
                      <span className="font-medium">
                        {drone.camera?.last_calibration ? new Date(drone.camera.last_calibration).toLocaleDateString() : 'N/A'}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="bg-gray-50 rounded-lg p-6 border border-gray-200">
                <h3 className="text-lg font-semibold mb-4 text-gray-800">🛰️ AI & Sensor Systems</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {[
                    { name: 'Pest Detection AI', status: 'active', accuracy: 96, icon: '🐛' },
                    { name: 'Canopy Analysis', status: 'active', accuracy: 94, icon: '🌿' },
                    { name: 'Multispectral Sensor', status: 'active', accuracy: 92, icon: '🌈' },
                    { name: 'Thermal Imaging', status: 'standby', accuracy: 88, icon: '🌡️' }
                  ].map((sensor, idx) => (
                    <div key={idx} className="bg-white rounded-lg p-4 border">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center space-x-2">
                          <span className="text-2xl">{sensor.icon}</span>
                          <span className="font-medium text-gray-800">{sensor.name}</span>
                        </div>
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          sensor.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-600'
                        }`}>
                          {sensor.status === 'active' ? '🟢 Active' : '⏸️ Standby'}
                        </span>
                      </div>
                      <div className="flex items-center justify-between mt-3">
                        <span className="text-sm text-gray-600">Accuracy</span>
                        <span className="font-semibold text-blue-600">{sensor.accuracy}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                        <div
                          className="bg-blue-500 h-2 rounded-full"
                          style={{ width: `${sensor.accuracy}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Flight History Tab */}
          {selectedTab === 'history' && (
            <div className="space-y-4">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-800">📜 Recent Flights</h3>
                <span className="text-sm text-gray-600">Last 10 missions</span>
              </div>
              <div className="overflow-x-auto">
                <table className="min-w-full bg-white border border-gray-200 rounded-lg">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Date</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Duration</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Distance</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Battery Used</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Images Captured</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {flightHistory.length > 0 ? flightHistory.map((flight, idx) => (
                      <tr key={idx} className="hover:bg-gray-50">
                        <td className="px-6 py-4 text-sm text-gray-900">
                          {new Date(flight.date).toLocaleDateString('en-US', { 
                            month: 'short', 
                            day: 'numeric', 
                            year: 'numeric' 
                          })}
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-900">{flight.duration} min</td>
                        <td className="px-6 py-4 text-sm text-gray-900">{flight.distance_covered} km</td>
                        <td className="px-6 py-4 text-sm text-gray-900">{flight.battery_used}%</td>
                        <td className="px-6 py-4 text-sm text-gray-900">{flight.images_captured}</td>
                        <td className="px-6 py-4">
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                            flight.status === 'success' ? 'bg-green-100 text-green-800' :
                            flight.status === 'partial' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-red-100 text-red-800'
                          }`}>
                            {flight.status === 'success' ? '✅ Success' :
                             flight.status === 'partial' ? '⚠️ Partial' : '❌ Failed'}
                          </span>
                        </td>
                      </tr>
                    )) : (
                      <tr>
                        <td colSpan="6" className="px-6 py-8 text-center text-gray-500">
                          No flight history available
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Specifications Tab */}
          {selectedTab === 'specs' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-gray-50 rounded-lg p-6 border border-gray-200">
                  <h3 className="text-lg font-semibold mb-4 text-gray-800">⚙️ Technical Specifications - DJI AGRAS T50</h3>
                  <div className="space-y-3">
                    {[
                      { label: 'Weight', value: drone.specs?.weight || '47.5 kg (with full tank)' },
                      { label: 'Max Speed', value: drone.specs?.max_speed || '10 m/s' },
                      { label: 'Max Altitude (AGL)', value: drone.specs?.max_altitude || '30 m AGL' },
                      { label: 'Max Flight Time', value: drone.specs?.max_flight_time || '18 min (full load)' },
                      { label: 'Wind Resistance', value: drone.specs?.wind_resistance || '8 m/s' },
                      { label: 'Operating Temperature', value: drone.specs?.temp_range || '-10°C to 45°C' },
                      { label: 'Spray Width', value: drone.specs?.spray_width || '11 m' },
                      { label: 'Tank Capacity', value: drone.specs?.tank_capacity || '40 L' }
                    ].map((spec, idx) => (
                      <div key={idx} className="flex justify-between p-3 bg-white rounded border">
                        <span className="text-gray-700">{spec.label}</span>
                        <span className="font-medium text-gray-900">{spec.value}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="bg-gray-50 rounded-lg p-6 border border-gray-200">
                  <h3 className="text-lg font-semibold mb-4 text-gray-800">🔋 Battery Specifications - DB1560</h3>
                  <div className="space-y-3">
                    {[
                      { label: 'Battery Type', value: drone.battery?.type || 'DB1560 Intelligent Battery' },
                      { label: 'Capacity', value: drone.battery?.capacity || '29,000 mAh' },
                      { label: 'Voltage', value: drone.battery?.voltage || '52.22 V' },
                      { label: 'Charge Time (80%)', value: drone.battery?.charge_time || '10 min' },
                      { label: 'Battery Cycles', value: drone.battery?.cycles || '247 / 1500' },
                      { label: 'Battery Health', value: drone.battery?.health || '92%' }
                    ].map((spec, idx) => (
                      <div key={idx} className="flex justify-between p-3 bg-white rounded border">
                        <span className="text-gray-700">{spec.label}</span>
                        <span className="font-medium text-gray-900">{spec.value}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              <div className="bg-blue-50 rounded-lg p-6 border border-blue-200">
                <h3 className="text-lg font-semibold mb-2 text-blue-900">📋 Maintenance Schedule</h3>
                <ul className="space-y-2 text-sm text-blue-800">
                  <li className="flex items-start">
                    <span className="mr-2">✓</span>
                    <span>Pre-flight inspection before every mission</span>
                  </li>
                  <li className="flex items-start">
                    <span className="mr-2">✓</span>
                    <span>Propeller check and cleaning every 10 flights</span>
                  </li>
                  <li className="flex items-start">
                    <span className="mr-2">✓</span>
                    <span>Camera lens calibration every 30 days</span>
                  </li>
                  <li className="flex items-start">
                    <span className="mr-2">✓</span>
                    <span>Spray nozzle inspection and cleaning after each use</span>
                  </li>
                  <li className="flex items-start">
                    <span className="mr-2">⚠️</span>
                    <span className="font-medium">Full service check due in {drone.service_due_days || 15} days</span>
                  </li>
                </ul>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
