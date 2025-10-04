import { useState } from 'react'

export default function FlightPathMap({ fieldWidth = 50, fieldHeight = 50 }) {
  // Predetermined flight path waypoints (zigzag pattern for optimal coverage)
  const waypoints = [
    { x: 2, y: 2, label: 'Start' },
    { x: 48, y: 2, label: 'WP1' },
    { x: 48, y: 10, label: 'WP2' },
    { x: 2, y: 10, label: 'WP3' },
    { x: 2, y: 18, label: 'WP4' },
    { x: 48, y: 18, label: 'WP5' },
    { x: 48, y: 26, label: 'WP6' },
    { x: 2, y: 26, label: 'WP7' },
    { x: 2, y: 34, label: 'WP8' },
    { x: 48, y: 34, label: 'WP9' },
    { x: 48, y: 42, label: 'WP10' },
    { x: 2, y: 42, label: 'WP11' },
    { x: 25, y: 48, label: 'End' }
  ]

  // Calculate path segments
  const pathSegments = []
  for (let i = 0; i < waypoints.length - 1; i++) {
    pathSegments.push({
      from: waypoints[i],
      to: waypoints[i + 1]
    })
  }

  // Calculate SVG viewBox with padding
  const padding = 5
  const viewBoxWidth = fieldWidth + (padding * 2)
  const viewBoxHeight = fieldHeight + (padding * 2)

  return (
    <div className="bg-gray-50 rounded-lg p-6 border border-gray-200">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-800">🗺️ Predetermined Flight Path</h3>
        <div className="flex items-center space-x-4 text-sm">
          <div className="flex items-center space-x-1">
            <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
            <span className="text-gray-600">Waypoints</span>
          </div>
          <div className="flex items-center space-x-1">
            <div className="w-8 h-0.5 bg-blue-400"></div>
            <span className="text-gray-600">Flight Path</span>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg border-2 border-gray-300 p-4">
        <svg
          viewBox={`0 0 ${viewBoxWidth} ${viewBoxHeight}`}
          className="w-full h-auto"
          style={{ maxHeight: '500px' }}
        >
          {/* Field boundary */}
          <rect
            x={padding}
            y={padding}
            width={fieldWidth}
            height={fieldHeight}
            fill="#f0fdf4"
            stroke="#86efac"
            strokeWidth="0.5"
            rx="1"
          />

          {/* Grid lines */}
          {Array.from({ length: 6 }).map((_, i) => {
            const offset = ((fieldHeight / 5) * i) + padding
            return (
              <line
                key={`h-${i}`}
                x1={padding}
                y1={offset}
                x2={fieldWidth + padding}
                y2={offset}
                stroke="#d1fae5"
                strokeWidth="0.3"
                strokeDasharray="1,1"
              />
            )
          })}
          {Array.from({ length: 6 }).map((_, i) => {
            const offset = ((fieldWidth / 5) * i) + padding
            return (
              <line
                key={`v-${i}`}
                x1={offset}
                y1={padding}
                x2={offset}
                y2={fieldHeight + padding}
                stroke="#d1fae5"
                strokeWidth="0.3"
                strokeDasharray="1,1"
              />
            )
          })}

          {/* Flight path lines with animation */}
          {pathSegments.map((segment, idx) => (
            <line
              key={`path-${idx}`}
              x1={segment.from.x + padding}
              y1={segment.from.y + padding}
              x2={segment.to.x + padding}
              y2={segment.to.y + padding}
              stroke="#3b82f6"
              strokeWidth="0.5"
              strokeLinecap="round"
              strokeDasharray="2,1"
              opacity="0.7"
            >
              <animate
                attributeName="stroke-dashoffset"
                from="3"
                to="0"
                dur="2s"
                repeatCount="indefinite"
              />
            </line>
          ))}

          {/* Waypoint markers */}
          {waypoints.map((wp, idx) => (
            <g key={`wp-${idx}`}>
              {/* Waypoint circle */}
              <circle
                cx={wp.x + padding}
                cy={wp.y + padding}
                r={idx === 0 || idx === waypoints.length - 1 ? 1.5 : 1}
                fill={idx === 0 ? '#10b981' : idx === waypoints.length - 1 ? '#ef4444' : '#3b82f6'}
                stroke="white"
                strokeWidth="0.3"
              />
              
              {/* Waypoint label for start/end */}
              {(idx === 0 || idx === waypoints.length - 1) && (
                <text
                  x={wp.x + padding}
                  y={wp.y + padding - 2.5}
                  textAnchor="middle"
                  fontSize="2.5"
                  fontWeight="bold"
                  fill={idx === 0 ? '#10b981' : '#ef4444'}
                >
                  {wp.label}
                </text>
              )}
            </g>
          ))}

          {/* Drone icon at start position (animated) */}
          <g transform={`translate(${waypoints[0].x + padding}, ${waypoints[0].y + padding})`}>
            <circle cx="0" cy="0" r="2" fill="#fbbf24" opacity="0.3">
              <animate
                attributeName="r"
                values="2;3;2"
                dur="2s"
                repeatCount="indefinite"
              />
            </circle>
            <text
              x="0"
              y="0.8"
              textAnchor="middle"
              fontSize="3"
            >
              🚁
            </text>
          </g>
        </svg>

        {/* Legend and stats */}
        <div className="mt-4 grid grid-cols-3 gap-4 text-sm">
          <div className="bg-gray-50 rounded p-3">
            <p className="text-gray-600 text-xs mb-1">Total Distance</p>
            <p className="text-lg font-bold text-gray-900">~5.2 km</p>
          </div>
          <div className="bg-gray-50 rounded p-3">
            <p className="text-gray-600 text-xs mb-1">Waypoints</p>
            <p className="text-lg font-bold text-gray-900">{waypoints.length}</p>
          </div>
          <div className="bg-gray-50 rounded p-3">
            <p className="text-gray-600 text-xs mb-1">Est. Duration</p>
            <p className="text-lg font-bold text-gray-900">~28 min</p>
          </div>
        </div>

        <div className="mt-3 text-xs text-gray-500 italic">
          ℹ️ The drone follows a zigzag pattern for complete field coverage with 11m spray width
        </div>
      </div>
    </div>
  )
}
