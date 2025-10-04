import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Dashboard API
export const dashboardAPI = {
  getTodayKPIs: (fieldId) => apiClient.get(`/dashboard/kpis/today?field_id=${fieldId}`),
  getWeeklyKPIs: (fieldId) => apiClient.get(`/dashboard/kpis/weekly?field_id=${fieldId}`),
}

// Pest API
export const pestAPI = {
  getDailyData: (fieldId, date, cropType) => {
    const params = new URLSearchParams({ field_id: fieldId })
    if (date) params.append('date', date)
    if (cropType) params.append('crop_type', cropType)
    return apiClient.get(`/pests/daily?${params}`)
  },
  getTrend: (fieldId, days = 7, cropType) => {
    const params = new URLSearchParams({ field_id: fieldId, days: days.toString() })
    if (cropType) params.append('crop_type', cropType)
    return apiClient.get(`/pests/trend?${params}`)
  },
}

// Canopy API
export const canopyAPI = {
  getDailyData: (fieldId, date) => {
    const params = new URLSearchParams({ field_id: fieldId })
    if (date) params.append('date', date)
    return apiClient.get(`/canopy/daily?${params}`)
  },
  getTrend: (fieldId, days = 7) => 
    apiClient.get(`/canopy/trend?field_id=${fieldId}&days=${days}`),
}

// Insights API
export const insightsAPI = {
  getZones: (fieldId, date) => {
    const params = new URLSearchParams({ field_id: fieldId })
    if (date) params.append('date', date)
    return apiClient.get(`/insights/zones?${params}`)
  },
}

// Alerts API
export const alertsAPI = {
  getActive: (fieldId) => apiClient.get(`/alerts/active?field_id=${fieldId}`),
  acknowledge: (alertId) => apiClient.post(`/alerts/acknowledge/${alertId}`),
}

// Analytics API
export const analyticsAPI = {
  getMonthly: (fieldId, month) => {
    const params = new URLSearchParams({ field_id: fieldId })
    if (month) params.append('month', month)
    return apiClient.get(`/analytics/monthly?${params}`)
  },
}

// Ingestion API (for testing)
export const ingestionAPI = {
  ingestDaily: (data) => apiClient.post('/ingestion/daily', data),
  getStatus: (fieldId) => apiClient.get(`/ingestion/status/${fieldId}`),
}

// Drone API
export const droneAPI = {
  getStatus: (droneId = 'drone_001') => 
    apiClient.get(`/drone/status?drone_id=${droneId}`),
  getFlightHistory: (droneId = 'drone_001', limit = 30, fieldId) => {
    const params = new URLSearchParams({ drone_id: droneId, limit: limit.toString() })
    if (fieldId) params.append('field_id', fieldId)
    return apiClient.get(`/drone/flights?${params}`)
  },
  updateStatus: (droneId, data) => 
    apiClient.post(`/drone/update-status?drone_id=${droneId}`, data),
  logFlight: (data) => 
    apiClient.post('/drone/log-flight', data),
}

export default apiClient
