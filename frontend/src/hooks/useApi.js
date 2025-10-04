import { useQuery } from '@tanstack/react-query'
import { dashboardAPI, pestAPI, canopyAPI, insightsAPI, alertsAPI, analyticsAPI, droneAPI } from '../services/api'

// Dashboard hooks
export const useTodayKPIs = (fieldId) => {
  return useQuery({
    queryKey: ['kpis', 'today', fieldId],
    queryFn: () => dashboardAPI.getTodayKPIs(fieldId).then(res => res.data),
    enabled: !!fieldId,
  })
}

export const useWeeklyKPIs = (fieldId) => {
  return useQuery({
    queryKey: ['kpis', 'weekly', fieldId],
    queryFn: () => dashboardAPI.getWeeklyKPIs(fieldId).then(res => res.data),
    enabled: !!fieldId,
  })
}

// Pest hooks
export const usePestDaily = (fieldId, date, cropType) => {
  return useQuery({
    queryKey: ['pests', 'daily', fieldId, date, cropType],
    queryFn: () => pestAPI.getDailyData(fieldId, date, cropType).then(res => res.data),
    enabled: !!fieldId,
  })
}

export const usePestTrend = (fieldId, days = 7) => {
  return useQuery({
    queryKey: ['pests', 'trend', fieldId, days],
    queryFn: () => pestAPI.getTrend(fieldId, days).then(res => res.data),
    enabled: !!fieldId,
  })
}

// Canopy hooks
export const useCanopyDaily = (fieldId, date) => {
  return useQuery({
    queryKey: ['canopy', 'daily', fieldId, date],
    queryFn: () => canopyAPI.getDailyData(fieldId, date).then(res => res.data),
    enabled: !!fieldId,
  })
}

export const useCanopyTrend = (fieldId, days = 7) => {
  return useQuery({
    queryKey: ['canopy', 'trend', fieldId, days],
    queryFn: () => canopyAPI.getTrend(fieldId, days).then(res => res.data),
    enabled: !!fieldId,
  })
}

// Insights hooks
export const useZoneInsights = (fieldId, date) => {
  return useQuery({
    queryKey: ['insights', 'zones', fieldId, date],
    queryFn: () => insightsAPI.getZones(fieldId, date).then(res => res.data),
    enabled: !!fieldId,
  })
}

// Alerts hooks
export const useActiveAlerts = (fieldId) => {
  return useQuery({
    queryKey: ['alerts', 'active', fieldId],
    queryFn: () => alertsAPI.getActive(fieldId).then(res => res.data),
    enabled: !!fieldId,
    refetchInterval: 60000, // Refetch every minute
  })
}

// Analytics hooks
export const useMonthlyAnalytics = (fieldId, month) => {
  return useQuery({
    queryKey: ['analytics', 'monthly', fieldId, month],
    queryFn: () => analyticsAPI.getMonthly(fieldId, month).then(res => res.data),
    enabled: !!fieldId,
  })
}

// Drone hooks
export const useDroneStatus = (droneId = 'drone_001') => {
  return useQuery({
    queryKey: ['drone', 'status', droneId],
    queryFn: () => droneAPI.getStatus(droneId).then(res => res.data),
    refetchInterval: 30000, // Refetch every 30 seconds for real-time updates
  })
}

export const useFlightHistory = (droneId = 'drone_001', limit = 30, fieldId) => {
  return useQuery({
    queryKey: ['drone', 'flights', droneId, limit, fieldId],
    queryFn: () => droneAPI.getFlightHistory(droneId, limit, fieldId).then(res => res.data),
  })
}
