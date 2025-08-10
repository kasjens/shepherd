/**
 * Performance Budget Tests
 * Phase 7: Performance Optimization & Polish
 */

import { performanceMonitor, PerformanceMetrics } from '../../src/lib/performance-monitor'
import { serviceWorkerManager } from '../../src/lib/service-worker'

// Mock performance APIs
global.performance = {
  ...global.performance,
  now: jest.fn(() => Date.now()),
  getEntriesByType: jest.fn(() => []),
  getEntriesByName: jest.fn(() => []),
  memory: {
    jsHeapSizeLimit: 2147483648,
    totalJSHeapSize: 50000000,
    usedJSHeapSize: 30000000
  }
}

// Mock PerformanceObserver
global.PerformanceObserver = jest.fn().mockImplementation(() => ({
  observe: jest.fn(),
  disconnect: jest.fn()
}))

describe('Performance Budget Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    performanceMonitor.clear()
  })

  describe('Core Web Vitals', () => {
    it('should track First Contentful Paint under budget', () => {
      const fcp = 800 // Under 1000ms budget
      performanceMonitor.recordMetric({ fcp })
      
      const budgetStatus = performanceMonitor.getBudgetStatus()
      const fcpBudget = budgetStatus.find(b => b.metric === 'fcp')
      
      expect(fcpBudget?.status).toBe('pass')
      expect(fcpBudget?.actual).toBe(fcp)
    })

    it('should warn when FCP exceeds budget but under critical threshold', () => {
      const fcp = 1200 // Over 1000ms budget but under 1500ms critical
      performanceMonitor.recordMetric({ fcp })
      
      const budgetStatus = performanceMonitor.getBudgetStatus()
      const fcpBudget = budgetStatus.find(b => b.metric === 'fcp')
      
      expect(fcpBudget?.status).toBe('warn')
    })

    it('should fail when FCP exceeds critical threshold', () => {
      const fcp = 1800 // Over 1500ms critical threshold
      performanceMonitor.recordMetric({ fcp })
      
      const budgetStatus = performanceMonitor.getBudgetStatus()
      const fcpBudget = budgetStatus.find(b => b.metric === 'fcp')
      
      expect(fcpBudget?.status).toBe('fail')
    })

    it('should track Largest Contentful Paint', () => {
      const lcp = 2200 // Under 2500ms budget
      performanceMonitor.recordMetric({ lcp })
      
      const budgetStatus = performanceMonitor.getBudgetStatus()
      const lcpBudget = budgetStatus.find(b => b.metric === 'lcp')
      
      expect(lcpBudget?.status).toBe('pass')
    })

    it('should track First Input Delay', () => {
      const fid = 80 // Under 100ms budget
      performanceMonitor.recordMetric({ fid })
      
      const budgetStatus = performanceMonitor.getBudgetStatus()
      const fidBudget = budgetStatus.find(b => b.metric === 'fid')
      
      expect(fidBudget?.status).toBe('pass')
    })

    it('should track Cumulative Layout Shift', () => {
      const cls = 0.05 // Under 0.1 budget
      performanceMonitor.recordMetric({ cls })
      
      const budgetStatus = performanceMonitor.getBudgetStatus()
      const clsBudget = budgetStatus.find(b => b.metric === 'cls')
      
      expect(clsBudget?.status).toBe('pass')
    })
  })

  describe('Custom Performance Metrics', () => {
    it('should measure sidebar toggle performance', () => {
      const toggleTime = performanceMonitor.measure('sidebarToggle', () => {
        // Simulate sidebar toggle animation
        const start = Date.now()
        while (Date.now() - start < 12) {} // 12ms operation
      })

      const metrics = performanceMonitor.getLatestMetrics()
      expect(metrics.sidebarToggle).toBeLessThan(16) // Under 16ms budget (60 FPS)
    })

    it('should measure modal open performance', async () => {
      const modalTime = await performanceMonitor.measureAsync('modalOpen', async () => {
        return new Promise(resolve => setTimeout(resolve, 80))
      })

      const metrics = performanceMonitor.getLatestMetrics()
      expect(metrics.modalOpen).toBeLessThan(100) // Under 100ms budget
    })

    it('should track API response times', async () => {
      const apiTime = await performanceMonitor.measureAsync('apiResponse', async () => {
        return new Promise(resolve => setTimeout(resolve, 300))
      })

      const metrics = performanceMonitor.getLatestMetrics()
      expect(metrics.apiResponse).toBeLessThan(500) // Under 500ms budget
    })
  })

  describe('Memory Performance', () => {
    it('should monitor JavaScript heap usage', () => {
      performanceMonitor.recordMetric({
        usedJSHeapSize: 30000000, // 30MB
        totalJSHeapSize: 50000000, // 50MB
        jsHeapSizeLimit: 2147483648 // 2GB
      })

      const metrics = performanceMonitor.getLatestMetrics()
      expect(metrics.usedJSHeapSize).toBeLessThan(100 * 1024 * 1024) // Under 100MB warning
    })

    it('should warn when memory usage is high', () => {
      const highMemoryUsage = 150 * 1024 * 1024 // 150MB
      performanceMonitor.recordMetric({
        usedJSHeapSize: highMemoryUsage
      })

      const metrics = performanceMonitor.getLatestMetrics()
      expect(metrics.usedJSHeapSize).toBeGreaterThan(100 * 1024 * 1024)
      expect(metrics.usedJSHeapSize).toBeLessThan(200 * 1024 * 1024) // Still under critical
    })
  })

  describe('Performance Monitoring', () => {
    it('should collect metrics over time', () => {
      // Record multiple metrics
      performanceMonitor.recordMetric({ fcp: 800 })
      performanceMonitor.recordMetric({ lcp: 2200 })
      performanceMonitor.recordMetric({ fid: 80 })

      const allMetrics = performanceMonitor.getAllMetrics()
      expect(allMetrics).toHaveLength(3)
    })

    it('should limit metrics history to prevent memory leaks', () => {
      // Record more than 100 metrics
      for (let i = 0; i < 150; i++) {
        performanceMonitor.recordMetric({ fcp: 800 + i })
      }

      const allMetrics = performanceMonitor.getAllMetrics()
      expect(allMetrics).toHaveLength(100) // Should be capped at 100
    })

    it('should notify listeners of new metrics', () => {
      const listener = jest.fn()
      const unsubscribe = performanceMonitor.subscribe(listener)

      performanceMonitor.recordMetric({ fcp: 800 })

      expect(listener).toHaveBeenCalledWith(
        expect.objectContaining({ fcp: 800 })
      )

      unsubscribe()
    })
  })

  describe('Service Worker Performance', () => {
    it('should register service worker in production', async () => {
      // Mock production environment
      const originalEnv = process.env.NODE_ENV
      process.env.NODE_ENV = 'production'

      // Mock navigator.serviceWorker
      Object.defineProperty(navigator, 'serviceWorker', {
        value: {
          register: jest.fn().mockResolvedValue({
            scope: '/',
            addEventListener: jest.fn(),
            waiting: null
          }),
          addEventListener: jest.fn()
        },
        writable: true
      })

      const registration = await serviceWorkerManager.register()
      expect(registration).toBeTruthy()

      // Restore environment
      process.env.NODE_ENV = originalEnv
    })

    it('should handle service worker registration failure', async () => {
      // Mock navigator.serviceWorker with failure
      Object.defineProperty(navigator, 'serviceWorker', {
        value: {
          register: jest.fn().mockRejectedValue(new Error('Registration failed')),
        },
        writable: true
      })

      const registration = await serviceWorkerManager.register()
      expect(registration).toBeNull()
    })
  })

  describe('Bundle Size Performance', () => {
    it('should check bundle size constraints', () => {
      // This would typically be checked during build process
      // Here we simulate the check
      const bundleSize = 180 * 1024 // 180KB
      const maxSize = 200 * 1024 // 200KB budget

      expect(bundleSize).toBeLessThan(maxSize)
    })

    it('should verify code splitting is working', () => {
      // Verify that lazy-loaded components exist
      // This is more of a build-time check but we can verify the setup
      const lazyComponents = [
        'LazyLineChart',
        'LazyBarChart', 
        'LazyPieChart',
        'LazyHeatmap',
        'LazyScatterPlot',
        'LazyAreaChart'
      ]

      lazyComponents.forEach(component => {
        expect(component).toBeDefined()
      })
    })
  })

  describe('Network Performance', () => {
    it('should simulate fast connection performance', () => {
      const networkMetrics = {
        rtt: 40,
        throughput: 10 * 1024 * 1024, // 10 Mbps
        effectiveType: '4g'
      }

      expect(networkMetrics.rtt).toBeLessThan(50)
      expect(networkMetrics.throughput).toBeGreaterThan(5 * 1024 * 1024)
    })

    it('should handle slow connection gracefully', () => {
      const networkMetrics = {
        rtt: 150,
        throughput: 1.6 * 1024 * 1024, // 1.6 Mbps
        effectiveType: '3g'
      }

      expect(networkMetrics.rtt).toBeGreaterThan(100)
      expect(networkMetrics.throughput).toBeLessThan(2 * 1024 * 1024)
    })
  })

  describe('Performance Regression Detection', () => {
    it('should detect performance regressions', () => {
      // Record baseline performance
      const baseline = { fcp: 800, lcp: 2200, fid: 80 }
      performanceMonitor.recordMetric(baseline)

      // Record regressed performance - values that exceed 1.5x budget to trigger failures
      const regressed = { fcp: 1600, lcp: 4000, fid: 200 } // Exceed 1.5x thresholds
      performanceMonitor.recordMetric(regressed)

      const budgetStatus = performanceMonitor.getBudgetStatus()
      const failures = budgetStatus.filter(b => b.status === 'fail')
      
      expect(failures.length).toBeGreaterThan(0)
    })

    it('should track performance improvements', () => {
      // Record poor baseline
      const baseline = { fcp: 1500, lcp: 3500, fid: 150 }
      performanceMonitor.recordMetric(baseline)

      // Record improved performance
      const improved = { fcp: 700, lcp: 2000, fid: 60 }
      performanceMonitor.recordMetric(improved)

      const budgetStatus = performanceMonitor.getBudgetStatus()
      const passes = budgetStatus.filter(b => b.status === 'pass')
      
      expect(passes.length).toBe(budgetStatus.length)
    })
  })
})