import { useTodayKPIs, useWeeklyKPIs, useActiveAlerts } from '../hooks/useApi'
import AlertBanner from '../components/dashboard/AlertBanner'
import KPICard from '../components/dashboard/KPICard'
import PestTrendChart from '../components/charts/PestTrendChart'
import CanopyTrendChart from '../components/charts/CanopyTrendChart'
import { Bug, Leaf, TrendingUp, Activity } from 'lucide-react'

export default function DashboardPage() {
  const fieldId = 'field_001' // This would come from context/state
  
  const { data: todayData, isLoading: loadingToday } = useTodayKPIs(fieldId)
  const { data: weeklyData, isLoading: loadingWeekly } = useWeeklyKPIs(fieldId)
  const { data: alertsData } = useActiveAlerts(fieldId)

  if (loadingToday || loadingWeekly) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  const pestTrend = todayData?.change_vs_yesterday?.pest_change_pct > 0 ? 'bad' : 'good'
  const canopyTrend = todayData?.change_vs_yesterday?.canopy_change_pct > 0 ? 'good' : 'bad'

  return (
    <div className="space-y-6">
      {/* Alerts */}
      <AlertBanner alerts={alertsData?.active_alerts || []} />

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <KPICard
          title="Today's Pest Count"
          value={todayData?.pest_count || 0}
          change={todayData?.change_vs_yesterday?.pest_change}
          changePercent={todayData?.change_vs_yesterday?.pest_change_pct || 0}
          icon={Bug}
          trend={pestTrend}
        />
        
        <KPICard
          title="Canopy Coverage"
          value={todayData?.avg_canopy_cover?.toFixed(1) || 0}
          unit="%"
          change={todayData?.change_vs_yesterday?.canopy_change}
          changePercent={todayData?.change_vs_yesterday?.canopy_change_pct || 0}
          icon={Leaf}
          trend={canopyTrend}
        />
        
        <KPICard
          title="Weekly Pest Trend"
          value={weeklyData?.weekly_summary?.pest_trend === 'increasing' ? '↗' : '↘'}
          icon={TrendingUp}
          trend={weeklyData?.weekly_summary?.pest_trend === 'increasing' ? 'bad' : 'good'}
        />
        
        <KPICard
          title="Field Health"
          value={todayData?.status === 'critical' ? 'Action Needed' : 'Healthy'}
          icon={Activity}
          trend={todayData?.status === 'critical' ? 'bad' : 'good'}
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl p-6 card-shadow">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Weekly Pest Detections
          </h2>
          <PestTrendChart data={weeklyData} />
        </div>

        <div className="bg-white rounded-xl p-6 card-shadow">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Weekly Canopy Health
          </h2>
          <CanopyTrendChart data={weeklyData} />
        </div>
      </div>

      {/* Quick Stats */}
      <div className="bg-white rounded-xl p-6 card-shadow">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Quick Statistics
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center p-4 bg-green-50 rounded-lg">
            <p className="text-2xl font-bold text-green-600">
              {weeklyData?.weekly_summary?.total_pests || 0}
            </p>
            <p className="text-sm text-gray-600 mt-1">Total Pests This Week</p>
          </div>
          <div className="text-center p-4 bg-blue-50 rounded-lg">
            <p className="text-2xl font-bold text-blue-600">
              {weeklyData?.weekly_summary?.avg_canopy?.toFixed(1) || 0}%
            </p>
            <p className="text-sm text-gray-600 mt-1">Avg Weekly Canopy</p>
          </div>
          <div className="text-center p-4 bg-amber-50 rounded-lg">
            <p className="text-2xl font-bold text-amber-600">
              {todayData?.active_alerts || 0}
            </p>
            <p className="text-sm text-gray-600 mt-1">Active Alerts</p>
          </div>
          <div className="text-center p-4 bg-purple-50 rounded-lg">
            <p className="text-2xl font-bold text-purple-600">7</p>
            <p className="text-sm text-gray-600 mt-1">Days Monitored</p>
          </div>
        </div>
      </div>
    </div>
  )
}
