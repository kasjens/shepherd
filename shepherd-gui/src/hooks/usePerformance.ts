'use client'

import { useEffect, useRef, useState } from 'react'
import { 
  measurePerformance, 
  getWebVitals, 
  PerformanceMetrics,
  isLowEndDevice,
  performanceMonitor
} from '@/lib/performance'

/**
 * Hook for tracking component render performance
 */
export const useRenderPerformance = (componentName: string) => {
  const startTimeRef = useRef<number>()
  const [renderTime, setRenderTime] = useState<number>(0)
  
  useEffect(() => {
    startTimeRef.current = performance.now()
  })
  
  useEffect(() => {
    if (startTimeRef.current) {
      const duration = performance.now() - startTimeRef.current
      setRenderTime(duration)
      
      if (performanceMonitor) {
        performanceMonitor.addMetric(`${componentName}-render`, duration)
      }
    }
  })
  
  return renderTime
}

/**
 * Hook for monitoring Web Vitals
 */
export const useWebVitals = () => {
  const [metrics, setMetrics] = useState<PerformanceMetrics>({})
  const [loading, setLoading] = useState(true)
  
  useEffect(() => {
    getWebVitals()
      .then((vitals) => {
        setMetrics(vitals)
        setLoading(false)
      })
      .catch(() => {
        setLoading(false)
      })
  }, [])
  
  return { metrics, loading }
}

/**
 * Hook for performance-aware rendering based on device capabilities
 */
export const usePerformanceMode = () => {
  const [isLowEnd, setIsLowEnd] = useState(false)
  const [reducedMotion, setReducedMotion] = useState(false)
  
  useEffect(() => {
    // Check device performance
    setIsLowEnd(isLowEndDevice())
    
    // Check user preferences for reduced motion
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
    setReducedMotion(mediaQuery.matches)
    
    const handleChange = (e: MediaQueryListEvent) => {
      setReducedMotion(e.matches)
    }
    
    mediaQuery.addEventListener('change', handleChange)
    return () => mediaQuery.removeEventListener('change', handleChange)
  }, [])
  
  return {
    isLowEnd,
    reducedMotion,
    shouldReduceAnimations: isLowEnd || reducedMotion,
    shouldVirtualizeList: isLowEnd,
    maxItemsToRender: isLowEnd ? 10 : 50
  }
}

/**
 * Hook for measuring async operations
 */
export const useAsyncPerformance = () => {
  const measureAsync = async <T>(
    name: string,
    operation: () => Promise<T>
  ): Promise<{ result: T; duration: number }> => {
    const duration = await measurePerformance(name, operation)
    const result = await operation()
    
    return { result, duration }
  }
  
  return { measureAsync }
}

/**
 * Hook for performance budgets and warnings
 */
export const usePerformanceBudget = (
  budgets: Record<string, number> = {
    'component-render': 16, // 16ms for 60fps
    'api-call': 500,        // 500ms for API calls
    'page-load': 2000,      // 2s for page load
  }
) => {
  const [violations, setViolations] = useState<string[]>([])
  
  useEffect(() => {
    if (!performanceMonitor) return
    
    const checkBudgets = () => {
      const newViolations: string[] = []
      
      Object.entries(budgets).forEach(([metric, budget]) => {
        const average = performanceMonitor.getAverageMetric(metric)
        if (average > budget) {
          newViolations.push(`${metric}: ${average.toFixed(2)}ms (budget: ${budget}ms)`)
        }
      })
      
      setViolations(newViolations)
    }
    
    const interval = setInterval(checkBudgets, 5000) // Check every 5 seconds
    return () => clearInterval(interval)
  }, [budgets])
  
  return { violations }
}

/**
 * Hook for tracking long tasks that might block the main thread
 */
export const useLongTaskMonitor = () => {
  const [longTasks, setLongTasks] = useState<PerformanceEntry[]>([])
  
  useEffect(() => {
    if (!('PerformanceObserver' in window)) return
    
    const observer = new PerformanceObserver((list) => {
      const tasks = list.getEntries()
      setLongTasks(prev => [...prev, ...tasks].slice(-10)) // Keep last 10 tasks
    })
    
    try {
      observer.observe({ entryTypes: ['longtask'] })
    } catch (e) {
      // Longtask API might not be supported
      console.warn('Long task monitoring not supported')
    }
    
    return () => observer.disconnect()
  }, [])
  
  return { longTasks }
}

/**
 * Hook for memory usage monitoring (if available)
 */
export const useMemoryMonitor = () => {
  const [memoryInfo, setMemoryInfo] = useState<any>(null)
  
  useEffect(() => {
    if (!(window as any).performance?.memory) return
    
    const updateMemoryInfo = () => {
      const memory = (window as any).performance.memory
      setMemoryInfo({
        used: memory.usedJSHeapSize,
        total: memory.totalJSHeapSize,
        limit: memory.jsHeapSizeLimit,
        percentage: (memory.usedJSHeapSize / memory.totalJSHeapSize) * 100
      })
    }
    
    updateMemoryInfo()
    const interval = setInterval(updateMemoryInfo, 2000)
    
    return () => clearInterval(interval)
  }, [])
  
  return { memoryInfo }
}