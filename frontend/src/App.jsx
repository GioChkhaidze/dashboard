import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Layout from './components/layout/Layout'
import DashboardPage from './pages/DashboardPage'
import HeatmapPage from './pages/HeatmapPage'
import InsightsPage from './pages/InsightsPage'
import AnalyticsPage from './pages/AnalyticsPage'
import DroneDetailsPage from './pages/DroneDetailsPage'

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/heatmap" element={<HeatmapPage />} />
          <Route path="/insights" element={<InsightsPage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
          <Route path="/drone" element={<DroneDetailsPage />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App
