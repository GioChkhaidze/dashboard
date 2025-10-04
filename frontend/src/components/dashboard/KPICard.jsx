import { TrendingUp, TrendingDown } from 'lucide-react'

export default function KPICard({ title, value, unit, change, changePercent, icon: Icon, trend }) {
  const isPositive = changePercent > 0
  const trendColor = trend === 'good' 
    ? 'text-green-600' 
    : trend === 'bad' 
      ? 'text-red-600' 
      : 'text-gray-600'

  return (
    <div className="bg-white rounded-xl p-6 card-shadow hover:card-shadow-lg transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
            <Icon className="w-6 h-6 text-green-600" />
          </div>
        </div>
      </div>
      
      <div className="space-y-2">
        <p className="text-sm font-medium text-gray-600">{title}</p>
        <p className="text-4xl font-bold text-gray-900">
          {value}
          {unit && <span className="text-2xl text-gray-500 ml-1">{unit}</span>}
        </p>
        
        {change !== undefined && (
          <div className={`flex items-center space-x-1 text-sm font-medium ${trendColor}`}>
            {isPositive ? (
              <TrendingUp className="w-4 h-4" />
            ) : (
              <TrendingDown className="w-4 h-4" />
            )}
            <span>
              {isPositive ? '+' : ''}{change} ({isPositive ? '+' : ''}{changePercent.toFixed(1)}%)
            </span>
            <span className="text-gray-500 ml-1">vs yesterday</span>
          </div>
        )}
      </div>
    </div>
  )
}
