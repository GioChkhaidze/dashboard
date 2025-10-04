import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

export default function CanopyTrendChart({ data }) {
  if (!data || !data.daily_canopy_avg) {
    return <div className="text-center text-gray-500 py-8">No data available</div>
  }

  const chartData = data.daily_canopy_avg.map((avg, index) => ({
    day: `Day ${index + 1}`,
    canopy: avg,
  }))

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={chartData}>
        <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
        <XAxis 
          dataKey="day" 
          stroke="#6b7280"
          style={{ fontSize: '12px' }}
        />
        <YAxis 
          stroke="#6b7280"
          style={{ fontSize: '12px' }}
          domain={[0, 100]}
        />
        <Tooltip 
          contentStyle={{
            backgroundColor: 'white',
            border: '1px solid #e5e7eb',
            borderRadius: '8px',
            boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
          }}
          formatter={(value) => [`${value.toFixed(1)}%`, 'Canopy Coverage']}
        />
        <Line 
          type="monotone" 
          dataKey="canopy" 
          stroke="#22c55e" 
          strokeWidth={2}
          dot={{ fill: '#22c55e', r: 4 }}
          activeDot={{ r: 6 }}
        />
      </LineChart>
    </ResponsiveContainer>
  )
}
