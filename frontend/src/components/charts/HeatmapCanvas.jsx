import { useEffect, useRef, useState } from 'react'

/**
 * High-performance Canvas-based Heatmap Renderer
 * Renders heatmap grids (default target: 50x50 = 2,500 cells) efficiently using HTML5 Canvas
 */
export default function HeatmapCanvas({ 
  data, 
  width = 800, 
  height = 640,
  colorScheme = 'pest', // 'pest' | 'canopy' | 'overlay'
  onCellClick = null,
  maxDensity = 1
}) {
  const canvasRef = useRef(null)
  const [hoveredCell, setHoveredCell] = useState(null)
  const [tooltip, setTooltip] = useState({ visible: false, x: 0, y: 0, content: '' })

  // Color interpolation functions
  const getPestColor = (density, maxDensity) => {
    if (density === 0) return [52, 211, 153, 0.15] // Light green
    
    const normalized = density / maxDensity
    
    if (normalized < 0.2) {
      // Safe zone: light green
      const alpha = 0.2 + normalized * 1.5
      return [52, 211, 153, alpha]
    } else if (normalized < 0.4) {
      // Low concern: yellow-green
      const t = (normalized - 0.2) / 0.2
      const r = 52 + t * (163 - 52)
      const g = 211 + t * (230 - 211)
      const b = 153 + t * (53 - 153)
      const alpha = 0.4 + normalized * 1.5
      return [r, g, b, alpha]
    } else if (normalized < 0.6) {
      // Moderate: yellow-orange
      const t = (normalized - 0.4) / 0.2
      const r = 163 + t * (251 - 163)
      const g = 230 + t * (191 - 230)
      const b = 53 + t * (36 - 53)
      const alpha = 0.5 + normalized
      return [r, g, b, alpha]
    } else if (normalized < 0.8) {
      // High concern: orange-red
      const t = (normalized - 0.6) / 0.2
      const r = 251 + t * (251 - 251)
      const g = 191 + t * (146 - 191)
      const b = 36 + t * (60 - 36)
      const alpha = 0.6 + normalized * 0.8
      return [r, g, b, alpha]
    } else {
      // Critical hotspot: red
      const t = (normalized - 0.8) / 0.2
      const r = 251 + t * (239 - 251)
      const g = 146 + t * (68 - 146)
      const b = 60 + t * (68 - 60)
      const alpha = 0.7 + normalized * 0.3
      return [r, g, b, Math.min(alpha, 1)]
    }
  }

  const getCanopyColor = (coverage) => {
    if (coverage >= 80) return [34, 197, 94, 0.7]   // Excellent - green
    if (coverage >= 70) return [132, 204, 22, 0.6]  // Good - lime
    if (coverage >= 60) return [234, 179, 8, 0.5]   // Fair - yellow
    if (coverage >= 50) return [251, 146, 60, 0.6]  // Poor - orange
    return [220, 38, 38, 0.7]                        // Critical - red
  }

  const getOverlayColor = (pestDensity, canopyCoverage, maxDensity) => {
    const pestIssue = pestDensity > maxDensity * 0.3
    const canopyIssue = canopyCoverage < 60
    
    if (pestIssue && canopyIssue) return [220, 38, 38, 0.75]   // Critical - both issues
    if (pestIssue) return [251, 146, 60, 0.6]                   // Warning - pests
    if (canopyIssue) return [234, 179, 8, 0.5]                  // Warning - canopy
    return [52, 211, 153, 0.3]                                   // Healthy
  }

  // Bilinear interpolation for smooth gradients
  const bilinearInterpolate = (grid, x, y) => {
    const x0 = Math.floor(x)
    const x1 = Math.min(x0 + 1, grid[0].length - 1)
    const y0 = Math.floor(y)
    const y1 = Math.min(y0 + 1, grid.length - 1)
    
    const dx = x - x0
    const dy = y - y0
    
    const v00 = grid[y0]?.[x0] || 0
    const v10 = grid[y0]?.[x1] || 0
    const v01 = grid[y1]?.[x0] || 0
    const v11 = grid[y1]?.[x1] || 0
    
    const v0 = v00 * (1 - dx) + v10 * dx
    const v1 = v01 * (1 - dx) + v11 * dx
    
    return v0 * (1 - dy) + v1 * dy
  }

  // Main rendering function
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas || !data || !data.length) return

    const ctx = canvas.getContext('2d', { alpha: true })
    const dpr = window.devicePixelRatio || 1
    
    // Set canvas size with device pixel ratio for crisp rendering
    canvas.width = width * dpr
    canvas.height = height * dpr
    canvas.style.width = `${width}px`
    canvas.style.height = `${height}px`
    ctx.scale(dpr, dpr)

    const gridHeight = data.length
    const gridWidth = data[0]?.length || 0
    const cellWidth = width / gridWidth
    const cellHeight = height / gridHeight

    // Clear canvas
    ctx.clearRect(0, 0, width, height)

    // Render with smooth interpolation (optional - can be toggled)
    const useSmoothing = true
    const resolution = useSmoothing ? 2 : 1 // Higher = smoother but slower

    for (let py = 0; py < height; py += cellHeight / resolution) {
      for (let px = 0; px < width; px += cellWidth / resolution) {
        // Map pixel coordinates to grid coordinates
        const gridX = (px / width) * gridWidth
        const gridY = (py / height) * gridHeight
        
        // Get interpolated value
        const value = useSmoothing 
          ? bilinearInterpolate(data, gridX, gridY)
          : data[Math.floor(gridY)]?.[Math.floor(gridX)] || 0

        // Get color based on scheme
        let color
        if (colorScheme === 'pest') {
          color = getPestColor(value, maxDensity)
        } else if (colorScheme === 'canopy') {
          color = getCanopyColor(value)
        } else {
          color = getOverlayColor(value, 70, maxDensity) // Simplified for overlay
        }

        // Draw rectangle
        ctx.fillStyle = `rgba(${color[0]}, ${color[1]}, ${color[2]}, ${color[3]})`
        ctx.fillRect(px, py, cellWidth / resolution + 1, cellHeight / resolution + 1)
      }
    }

  // Draw grid lines for better visibility (optional)
  // For performance and clarity, show grid lines for reasonably small grids (<= 50x50)
  if (gridWidth <= 50 && gridHeight <= 50) {
      ctx.strokeStyle = 'rgba(0, 0, 0, 0.03)'
      ctx.lineWidth = 0.5
      
      // Vertical lines
      for (let x = 0; x <= gridWidth; x++) {
        const px = x * cellWidth
        ctx.beginPath()
        ctx.moveTo(px, 0)
        ctx.lineTo(px, height)
        ctx.stroke()
      }
      
      // Horizontal lines
      for (let y = 0; y <= gridHeight; y++) {
        const py = y * cellHeight
        ctx.beginPath()
        ctx.moveTo(0, py)
        ctx.lineTo(width, py)
        ctx.stroke()
      }
    }

    // Highlight hovered cell
    if (hoveredCell) {
      const { x, y } = hoveredCell
      ctx.strokeStyle = 'rgba(59, 130, 246, 0.8)'
      ctx.lineWidth = 2
      ctx.strokeRect(x * cellWidth, y * cellHeight, cellWidth, cellHeight)
    }

  }, [data, width, height, colorScheme, hoveredCell, maxDensity])

  // Mouse interaction handlers
  const handleMouseMove = (e) => {
    const canvas = canvasRef.current
    if (!canvas || !data) return

    const rect = canvas.getBoundingClientRect()
    const x = e.clientX - rect.left
    const y = e.clientY - rect.top

    const gridWidth = data[0]?.length || 0
    const gridHeight = data.length
    const cellWidth = width / gridWidth
    const cellHeight = height / gridHeight

    const gridX = Math.floor(x / cellWidth)
    const gridY = Math.floor(y / cellHeight)

    if (gridX >= 0 && gridX < gridWidth && gridY >= 0 && gridY < gridHeight) {
      setHoveredCell({ x: gridX, y: gridY })
      
      const value = data[gridY][gridX]
      const content = colorScheme === 'pest' 
        ? `Cell [${gridX}, ${gridY}]\nDensity: ${value.toFixed(2)}`
        : `Cell [${gridX}, ${gridY}]\nValue: ${value.toFixed(1)}%`
      
      setTooltip({
        visible: true,
        x: e.clientX,
        y: e.clientY,
        content
      })
    }
  }

  const handleMouseLeave = () => {
    setHoveredCell(null)
    setTooltip({ visible: false, x: 0, y: 0, content: '' })
  }

  const handleClick = (e) => {
    if (!onCellClick || !hoveredCell) return
    
    const value = data[hoveredCell.y][hoveredCell.x]
    onCellClick({ x: hoveredCell.x, y: hoveredCell.y, value })
  }

  return (
    <div className="relative inline-block">
      <canvas
        ref={canvasRef}
        className="cursor-crosshair rounded-lg border border-gray-200"
        onMouseMove={handleMouseMove}
        onMouseLeave={handleMouseLeave}
        onClick={handleClick}
        style={{ imageRendering: 'crisp-edges' }}
      />
      
      {/* Tooltip */}
      {tooltip.visible && (
        <div
          className="fixed pointer-events-none z-50 bg-gray-900 text-white text-xs px-3 py-2 rounded shadow-lg whitespace-pre-line"
          style={{
            left: tooltip.x + 10,
            top: tooltip.y + 10
          }}
        >
          {tooltip.content}
        </div>
      )}
    </div>
  )
}
