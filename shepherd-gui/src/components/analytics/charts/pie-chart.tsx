'use client'

import React, { useEffect, useRef, useCallback } from 'react'
import { ChartConfig } from '../advanced-dashboard'

export interface PieChartProps {
  data: any[]
  config: ChartConfig
  width: string | number
  height: string | number
  onError?: (error: string) => void
  onLoadingChange?: (isLoading: boolean) => void
}

export default function PieChart({ data, config, width, height, onError, onLoadingChange }: PieChartProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const animationRef = useRef<number>(0)

  const drawChart = useCallback((processedData: any[], animationProgress = 1) => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // Set canvas size
    const rect = canvas.getBoundingClientRect()
    const dpr = window.devicePixelRatio || 1
    canvas.width = rect.width * dpr
    canvas.height = rect.height * dpr
    ctx.scale(dpr, dpr)

    // Clear canvas
    ctx.clearRect(0, 0, rect.width, rect.height)

    if (processedData.length === 0) {
      ctx.fillStyle = '#9CA3AF'
      ctx.font = '14px sans-serif'
      ctx.textAlign = 'center'
      ctx.fillText('No data available', rect.width / 2, rect.height / 2)
      return
    }

    // Chart dimensions
    const centerX = rect.width / 2
    const centerY = rect.height / 2
    const radius = Math.min(rect.width, rect.height) * 0.35
    const innerRadius = radius * 0.4 // For donut chart effect

    // Calculate total and percentages
    const total = processedData.reduce((sum, item) => sum + item.value, 0)
    if (total === 0) return

    // Colors
    const colors = config.colors || [
      '#3B82F6', '#EF4444', '#10B981', '#F59E0B', '#8B5CF6',
      '#06B6D4', '#EC4899', '#84CC16', '#F97316', '#6366F1'
    ]

    // Draw pie slices
    let currentAngle = -Math.PI / 2 // Start at top
    const maxAngle = currentAngle + (Math.PI * 2 * animationProgress)

    processedData.forEach((item, index) => {
      const sliceAngle = (item.value / total) * Math.PI * 2
      const endAngle = Math.min(currentAngle + sliceAngle, maxAngle)
      
      if (currentAngle >= maxAngle) return

      // Draw slice
      ctx.beginPath()
      ctx.moveTo(centerX, centerY)
      ctx.arc(centerX, centerY, radius, currentAngle, endAngle)
      ctx.closePath()
      ctx.fillStyle = colors[index % colors.length]
      ctx.fill()

      // Draw slice border
      ctx.strokeStyle = '#FFFFFF'
      ctx.lineWidth = 2
      ctx.stroke()

      // Draw inner circle for donut effect (optional)
      if ((config as any).type === 'donut') {
        ctx.beginPath()
        ctx.arc(centerX, centerY, innerRadius, 0, Math.PI * 2)
        ctx.fillStyle = '#FFFFFF'
        ctx.fill()
      }

      // Draw labels
      if (sliceAngle > 0.1) { // Only show labels for slices > ~6 degrees
        const labelAngle = currentAngle + sliceAngle / 2
        const labelRadius = radius * 0.7
        const labelX = centerX + Math.cos(labelAngle) * labelRadius
        const labelY = centerY + Math.sin(labelAngle) * labelRadius

        ctx.fillStyle = '#FFFFFF'
        ctx.font = 'bold 11px sans-serif'
        ctx.textAlign = 'center'
        ctx.textBaseline = 'middle'
        
        const percentage = ((item.value / total) * 100).toFixed(1)
        ctx.fillText(`${percentage}%`, labelX, labelY)
      }

      currentAngle = endAngle
    })

    // Draw center text for donut charts
    if ((config as any).type === 'donut') {
      ctx.fillStyle = '#374151'
      ctx.font = 'bold 16px sans-serif'
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'
      ctx.fillText('Total', centerX, centerY - 10)
      
      ctx.font = '14px sans-serif'
      ctx.fillText(total.toLocaleString(), centerX, centerY + 10)
    }

    // Interactive hover effects
    const handleMouseMove = (e: MouseEvent) => {
      const rect = canvas.getBoundingClientRect()
      const mouseX = e.clientX - rect.left
      const mouseY = e.clientY - rect.top

      const dx = mouseX - centerX
      const dy = mouseY - centerY
      const distance = Math.sqrt(dx * dx + dy * dy)

      if (distance <= radius && distance >= innerRadius) {
        let angle = Math.atan2(dy, dx) + Math.PI / 2
        if (angle < 0) angle += Math.PI * 2

        let currentAngle = 0
        let hoveredSlice = -1

        for (let i = 0; i < processedData.length; i++) {
          const sliceAngle = (processedData[i].value / total) * Math.PI * 2
          if (angle >= currentAngle && angle <= currentAngle + sliceAngle) {
            hoveredSlice = i
            break
          }
          currentAngle += sliceAngle
        }

        if (hoveredSlice >= 0) {
          const item = processedData[hoveredSlice]
          const percentage = ((item.value / total) * 100).toFixed(1)
          canvas.title = `${item.label}: ${item.value} (${percentage}%)`
          canvas.style.cursor = 'pointer'
        } else {
          canvas.title = ''
          canvas.style.cursor = 'default'
        }
      } else {
        canvas.title = ''
        canvas.style.cursor = 'default'
      }
    }

    canvas.removeEventListener('mousemove', handleMouseMove)
    canvas.addEventListener('mousemove', handleMouseMove)

    // Legend
    if (config.showLegend !== false) {
      const legendY = rect.height - 60
      const legendItemWidth = rect.width / Math.min(processedData.length, 4)

      processedData.slice(0, 4).forEach((item, index) => {
        const x = (index * legendItemWidth) + 20
        
        // Legend color box
        ctx.fillStyle = colors[index % colors.length]
        ctx.fillRect(x, legendY, 12, 12)
        
        // Legend text
        ctx.fillStyle = '#374151'
        ctx.font = '11px sans-serif'
        ctx.textAlign = 'left'
        ctx.fillText(item.label, x + 18, legendY + 9)
      })

      if (processedData.length > 4) {
        ctx.fillText(`+${processedData.length - 4} more`, rect.width - 80, legendY + 9)
      }
    }

  }, [config])

  // Process data and render chart
  useEffect(() => {
    onLoadingChange?.(true)

    try {
      // Process and aggregate data
      const processedData = data.reduce((acc: any[], item: any) => {
        const label = item[config.xAxis || 'category'] || item.label || 'Unknown'
        const yAxisKey = Array.isArray(config.yAxis) ? config.yAxis[0] : config.yAxis || 'value'
        const value = parseFloat(item[yAxisKey]) || 0
        
        const existing = acc.find(d => d.label === label)
        if (existing) {
          existing.value += value
        } else {
          acc.push({ label, value })
        }
        
        return acc
      }, [])

      // Sort by value descending
      processedData.sort((a, b) => b.value - a.value)

      if (config.animate !== false) {
        let progress = 0
        const animate = () => {
          progress += 0.03
          if (progress <= 1) {
            drawChart(processedData, progress)
            animationRef.current = requestAnimationFrame(animate)
          } else {
            drawChart(processedData)
            onLoadingChange?.(false)
          }
        }
        animate()
      } else {
        drawChart(processedData)
        onLoadingChange?.(false)
      }
    } catch (error) {
      onError?.(error instanceof Error ? error.message : 'Unknown error')
      onLoadingChange?.(false)
    }

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current)
      }
    }
  }, [data, config, drawChart, onError, onLoadingChange])

  return (
    <div className="w-full h-full relative">
      <canvas
        ref={canvasRef}
        className="w-full h-full"
        style={{ width, height }}
      />
    </div>
  )
}