import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts'
import { useMonthlyAnalytics, usePestTrend, useCanopyTrend } from '../hooks/useApi'

export default function AnalyticsPage() {
  const fieldId = 'field_001'
  const currentMonth = new Date().toISOString().slice(0, 7) // YYYY-MM format
  
  const { data: monthlyData, isLoading: monthlyLoading } = useMonthlyAnalytics(fieldId, currentMonth)
  const { data: pestTrend, isLoading: pestLoading } = usePestTrend(fieldId, 30)
  const { data: canopyTrend, isLoading: canopyLoading } = useCanopyTrend(fieldId, 30)

  const isLoading = monthlyLoading || pestLoading || canopyLoading

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[500px]">
        <div className="text-center">
          <div className="animate-spin text-4xl mb-2">⏳</div>
          <p className="text-gray-600">Loading analytics...</p>
        </div>
      </div>
    )
  }

  // Prepare chart data
  const pestChartData = pestTrend?.daily_counts?.map(item => ({
    date: new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    pests: item.count
  })) || []

  const canopyChartData = canopyTrend?.daily_averages?.map(item => ({
    date: new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    canopy: item.avg_canopy
  })) || []

  // Calculate summary stats
  const totalPests = monthlyData?.total_pests || 0
  const avgCanopy = monthlyData?.avg_canopy || 0
  const pestTrendDirection = pestTrend?.trend || 'stable'
  const canopyTrendDirection = canopyTrend?.trend || 'stable'

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl p-6 card-shadow">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Analytics & Trends</h1>
        <p className="text-gray-600 mb-6">
          Long-term trends and comparative analytics for your field.
        </p>

        {/* Monthly Summary */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-gradient-to-br from-red-50 to-red-100 rounded-lg p-6">
            <p className="text-sm text-gray-700 mb-1">Total Pests This Month</p>
            <p className="text-4xl font-bold text-red-600">{totalPests}</p>
            <p className={`text-sm mt-2 font-medium ${
              pestTrendDirection === 'increasing' ? 'text-red-700' : 'text-green-700'
            }`}>
              {pestTrendDirection === 'increasing' ? '↑' : '↓'} {pestTrend?.change_pct || 0}% vs last period
            </p>
          </div>
          
          <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-6">
            <p className="text-sm text-gray-700 mb-1">Avg Canopy Coverage</p>
            <p className="text-4xl font-bold text-green-600">{avgCanopy.toFixed(1)}%</p>
            <p className={`text-sm mt-2 font-medium ${
              canopyTrendDirection === 'improving' ? 'text-green-700' : 'text-red-700'
            }`}>
              {canopyTrendDirection === 'improving' ? '↑' : '↓'} {canopyTrend?.change_pct || 0}% vs last period
            </p>
          </div>
          
          <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-6">
            <p className="text-sm text-gray-700 mb-1">Data Points This Month</p>
            <p className="text-4xl font-bold text-blue-600">{monthlyData?.data_points || 0}</p>
            <p className="text-sm text-blue-700 mt-2">Days monitored</p>
          </div>
        </div>
      </div>

      {/* Pest Trend Chart */}
      <div className="bg-white rounded-xl p-6 card-shadow">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          30-Day Pest Trend
        </h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={pestChartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis 
              dataKey="date" 
              stroke="#6b7280" 
              style={{ fontSize: '12px' }}
              angle={-45}
              textAnchor="end"
              height={80}
            />
            <YAxis stroke="#6b7280" style={{ fontSize: '12px' }} />
            <Tooltip
              contentStyle={{
                backgroundColor: '#fff',
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
                padding: '8px'
              }}
            />
            <Line 
              type="monotone" 
              dataKey="pests" 
              stroke="#ef4444" 
              strokeWidth={2}
              dot={{ fill: '#ef4444', r: 4 }}
              name="Pest Count"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Canopy Trend Chart */}
      <div className="bg-white rounded-xl p-6 card-shadow">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          30-Day Canopy Coverage Trend
        </h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={canopyChartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis 
              dataKey="date" 
              stroke="#6b7280" 
              style={{ fontSize: '12px' }}
              angle={-45}
              textAnchor="end"
              height={80}
            />
            <YAxis stroke="#6b7280" style={{ fontSize: '12px' }} />
            <Tooltip
              contentStyle={{
                backgroundColor: '#fff',
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
                padding: '8px'
              }}
            />
            <Line 
              type="monotone" 
              dataKey="canopy" 
              stroke="#22c55e" 
              strokeWidth={2}
              dot={{ fill: '#22c55e', r: 4 }}
              name="Canopy %"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Insights */}
      <div className="bg-white rounded-xl p-6 card-shadow">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Trend Insights</h2>
        <div className="space-y-3">
          <div className={`flex items-start space-x-3 p-4 rounded-lg border ${
            pestTrendDirection === 'increasing' 
              ? 'bg-red-50 border-red-200' 
              : 'bg-green-50 border-green-200'
          }`}>
            <span className="text-2xl">{pestTrendDirection === 'increasing' ? '📈' : '📉'}</span>
            <div>
              <p className={`font-semibold ${
                pestTrendDirection === 'increasing' ? 'text-red-900' : 'text-green-900'
              }`}>
                Pest Activity: {pestTrendDirection}
              </p>
              <p className={`text-sm ${
                pestTrendDirection === 'increasing' ? 'text-red-700' : 'text-green-700'
              }`}>
                {pestTrendDirection === 'increasing' 
                  ? 'Pest counts are rising. Consider preventive measures.' 
                  : 'Pest counts are declining. Current treatment is effective.'}
              </p>
            </div>
          </div>

          <div className={`flex items-start space-x-3 p-4 rounded-lg border ${
            canopyTrendDirection === 'improving' 
              ? 'bg-green-50 border-green-200' 
              : 'bg-amber-50 border-amber-200'
          }`}>
            <span className="text-2xl">{canopyTrendDirection === 'improving' ? '🌱' : '🍂'}</span>
            <div>
              <p className={`font-semibold ${
                canopyTrendDirection === 'improving' ? 'text-green-900' : 'text-amber-900'
              }`}>
                Canopy Health: {canopyTrendDirection}
              </p>
              <p className={`text-sm ${
                canopyTrendDirection === 'improving' ? 'text-green-700' : 'text-amber-700'
              }`}>
                {canopyTrendDirection === 'improving' 
                  ? 'Canopy coverage is increasing. Field health is improving.' 
                  : 'Canopy coverage needs attention. Check irrigation and soil conditions.'}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
