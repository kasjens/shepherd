/**
 * Performance Budget Configuration for Phase 7 Optimization
 * Based on GUI implementation plan targets
 */

module.exports = {
  // Bundle Size Budgets
  budgets: [
    {
      type: 'bundle',
      name: 'main',
      maximumWarning: '200kb',
      maximumError: '250kb'
    },
    {
      type: 'entry',
      name: 'polyfills',
      maximumWarning: '50kb',
      maximumError: '75kb'
    },
    {
      type: 'any',
      maximumWarning: '300kb',
      maximumError: '400kb'
    }
  ],
  
  // Core Web Vitals Targets
  webVitals: {
    FCP: 1000,     // First Contentful Paint < 1s
    LCP: 2500,     // Largest Contentful Paint < 2.5s  
    FID: 100,      // First Input Delay < 100ms
    CLS: 0.1,      // Cumulative Layout Shift < 0.1
    TTI: 3500,     // Time to Interactive < 3.5s
    TBT: 300,      // Total Blocking Time < 300ms
  },

  // Performance KPIs from implementation plan
  performance: {
    sidebarToggle: 16,    // Sidebar animation < 16ms per frame (60 FPS)
    messageRender: 50,    // Message render < 50ms
    modalOpen: 100,       // Modal opening < 100ms
    apiResponse: 500,     // API response < 500ms
    websocketLatency: 50, // WebSocket latency < 50ms
  },

  // Lighthouse Thresholds
  lighthouse: {
    performance: 90,      // Performance score > 90
    accessibility: 90,    // Accessibility score > 90
    bestPractices: 90,    // Best practices score > 90
    seo: 85,             // SEO score > 85
    pwa: 80,             // PWA score > 80 (if applicable)
  },

  // Bundle Analysis Settings
  analysis: {
    outputDir: '.next/analyze',
    generateReport: process.env.ANALYZE === 'true',
    formats: ['html', 'json'],
    threshold: {
      warning: 0.1,  // Warn if bundle increases by 10%
      error: 0.2     // Error if bundle increases by 20%
    }
  },

  // Memory Usage Targets
  memory: {
    jsHeapSizeLimit: 2147483648,     // 2GB limit
    maxHeapSize: 100 * 1024 * 1024,  // 100MB warning threshold
    criticalHeapSize: 200 * 1024 * 1024, // 200MB critical threshold
  },

  // Network Performance
  network: {
    slowConnection: {
      rtt: 150,           // 150ms round-trip time
      throughput: 1.6 * 1024 * 1024, // 1.6 Mbps
    },
    fastConnection: {
      rtt: 40,            // 40ms round-trip time  
      throughput: 10 * 1024 * 1024,  // 10 Mbps
    }
  }
}