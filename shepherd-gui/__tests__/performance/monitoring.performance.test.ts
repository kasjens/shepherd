import {
  measurePerformance,
  PerformanceMonitor,
  throttle,
  debounce,
  isLowEndDevice
} from '@/lib/performance'

// Mock performance APIs
const mockPerformance = {
  now: jest.fn(() => Date.now()),
  mark: jest.fn(),
  measure: jest.fn(() => ({ duration: 15 })),
  clearMarks: jest.fn(),
  clearMeasures: jest.fn(),
}

Object.defineProperty(global, 'performance', {
  value: mockPerformance,
  writable: true
})

describe('Performance Monitoring Utilities', () => {
  beforeEach(() => {
    jest.clearAllMocks()
    mockPerformance.now.mockReturnValue(1000)
  })

  describe('measurePerformance', () => {
    test('measures synchronous function execution time', async () => {
      const testFunction = jest.fn()
      const duration = await measurePerformance('test-sync', testFunction)
      
      expect(mockPerformance.mark).toHaveBeenCalledWith('test-sync-start')
      expect(mockPerformance.mark).toHaveBeenCalledWith('test-sync-end')
      expect(mockPerformance.measure).toHaveBeenCalledWith('test-sync', 'test-sync-start', 'test-sync-end')
      expect(duration).toBe(15)
    })
  })

  describe('PerformanceMonitor', () => {
    let monitor: PerformanceMonitor

    beforeEach(() => {
      monitor = new PerformanceMonitor()
    })

    afterEach(() => {
      monitor.destroy()
    })

    test('adds and tracks custom metrics', () => {
      monitor.addMetric('test-metric', 100)
      monitor.addMetric('test-metric', 150)
      
      const metrics = monitor.getMetrics()
      expect(metrics).toHaveLength(2)
      expect(metrics[0].name).toBe('test-metric')
      expect(metrics[0].value).toBe(100)
    })

    test('calculates average metrics correctly', () => {
      monitor.addMetric('component-render', 10)
      monitor.addMetric('component-render', 20)
      monitor.addMetric('component-render', 30)
      
      const average = monitor.getAverageMetric('component-render')
      expect(average).toBe(20)
    })
  })

  describe('Performance Utilities', () => {
    test('throttle function limits execution frequency', (done) => {
      const mockFn = jest.fn()
      const throttledFn = throttle(mockFn, 100)
      
      throttledFn()
      throttledFn()
      
      expect(mockFn).toHaveBeenCalledTimes(1)
      done()
    })

    test('debounce function delays execution', (done) => {
      const mockFn = jest.fn()
      const debouncedFn = debounce(mockFn, 100)
      
      debouncedFn()
      debouncedFn()
      
      expect(mockFn).toHaveBeenCalledTimes(0)
      
      setTimeout(() => {
        expect(mockFn).toHaveBeenCalledTimes(1)
        done()
      }, 150)
    })
  })

  describe('Device Performance Detection', () => {
    test('detects low-end device based on hardware concurrency', () => {
      Object.defineProperty(navigator, 'hardwareConcurrency', {
        value: 2,
        configurable: true
      })
      
      expect(isLowEndDevice()).toBe(true)
    })
  })
})