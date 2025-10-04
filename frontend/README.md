# Frontend - Agricultural Dashboard

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## 📦 Tech Stack

- **React** 18+ - UI library
- **Vite** 5+ - Build tool
- **TailwindCSS** 3.4+ - Styling
- **shadcn/ui** - UI components
- **Recharts** - Charts and visualizations
- **React Router** v6 - Routing
- **React Query** - Data fetching and caching
- **Axios** - HTTP client
- **Lucide React** - Icons

## 📁 Project Structure

```
frontend/
├── public/
│   └── favicon.ico
├── src/
│   ├── assets/          # Images, fonts, etc.
│   ├── components/      # Reusable components
│   │   ├── ui/          # shadcn/ui components
│   │   ├── dashboard/   # Dashboard-specific components
│   │   ├── heatmap/     # Heatmap components
│   │   ├── charts/      # Chart components
│   │   └── layout/      # Layout components
│   ├── pages/           # Page components
│   │   ├── DashboardPage.jsx
│   │   ├── HeatmapPage.jsx
│   │   ├── InsightsPage.jsx
│   │   └── AnalyticsPage.jsx
│   ├── hooks/           # Custom React hooks
│   ├── services/        # API services
│   ├── utils/           # Utility functions
│   ├── contexts/        # React contexts
│   ├── lib/             # Third-party library configs
│   ├── App.jsx          # Main app component
│   ├── main.jsx         # Entry point
│   └── index.css        # Global styles
├── .env.example
├── package.json
├── vite.config.js
├── tailwind.config.js
├── postcss.config.js
└── README.md
```

## 🎨 Component Hierarchy

```
App
├── Layout
│   ├── Sidebar
│   ├── Header
│   └── MainContent
│       ├── DashboardPage
│       │   ├── AlertBanner
│       │   ├── KPICards
│       │   │   ├── PestCountCard
│       │   │   ├── CanopyCoverCard
│       │   │   └── HealthScoreCard
│       │   └── TrendCharts
│       │       ├── PestTrendChart
│       │       └── CanopyTrendChart
│       ├── HeatmapPage
│       │   ├── HeatmapCanvas
│       │   │   ├── PestHeatmap
│       │   │   └── CanopyHeatmap
│       │   ├── TimeSlider
│       │   ├── LayerToggle
│       │   └── LegendPanel
│       ├── InsightsPage
│       │   ├── FieldGrid
│       │   ├── ZoneCard
│       │   └── ZoneDetails
│       └── AnalyticsPage
│           ├── StatisticsPanel
│           └── ComparisonCharts
```

## 🔧 Configuration

### Environment Variables

Create `.env` file:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_TITLE=Agricultural Dashboard
```

## 📝 Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run format` - Format with Prettier
