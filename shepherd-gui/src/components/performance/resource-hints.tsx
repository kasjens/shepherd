/**
 * Resource Hints Component
 * Phase 7: Performance Optimization & Polish
 */

import Head from 'next/head'

interface ResourceHintsProps {
  apiBaseUrl?: string
  websocketUrl?: string
  criticalResources?: string[]
}

export function ResourceHints({ 
  apiBaseUrl = 'http://localhost:8000',
  websocketUrl = 'ws://localhost:8000',
  criticalResources = []
}: ResourceHintsProps) {
  return (
    <Head>
      {/* DNS Prefetch for external domains */}
      <link rel="dns-prefetch" href="//fonts.googleapis.com" />
      <link rel="dns-prefetch" href="//fonts.gstatic.com" />
      
      {/* Preconnect to critical origins */}
      <link rel="preconnect" href={apiBaseUrl} crossOrigin="" />
      <link rel="preconnect" href="https://fonts.googleapis.com" crossOrigin="" />
      <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
      
      {/* Preload critical resources */}
      <link
        rel="preload"
        href="/Shepherd.png"
        as="image"
        type="image/png"
      />
      
      {/* Preload critical fonts */}
      <link
        rel="preload"
        href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
        as="style"
      />
      
      {/* Custom critical resources */}
      {criticalResources.map((resource, index) => (
        <link
          key={index}
          rel="preload"
          href={resource}
          as={getResourceType(resource)}
        />
      ))}
      
      {/* Prefetch likely navigation targets */}
      <link rel="prefetch" href="/analytics" />
      <link rel="prefetch" href="/settings" />
      
      {/* Module preload for critical JavaScript */}
      <link
        rel="modulepreload"
        href="/_next/static/chunks/main.js"
      />
      <link
        rel="modulepreload"
        href="/_next/static/chunks/pages/_app.js"
      />
      
      {/* Performance optimizations */}
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <meta httpEquiv="Content-Security-Policy" content="upgrade-insecure-requests" />
      
      {/* Resource hints for WebSocket connection */}
      {websocketUrl && (
        <link rel="preconnect" href={websocketUrl.replace('ws://', 'http://').replace('wss://', 'https://')} />
      )}
    </Head>
  )
}

/**
 * Determine resource type from URL for preload hints
 */
function getResourceType(url: string): string {
  if (url.match(/\.(js|mjs)$/)) return 'script'
  if (url.match(/\.css$/)) return 'style'
  if (url.match(/\.(png|jpg|jpeg|gif|webp|avif|svg)$/)) return 'image'
  if (url.match(/\.(woff|woff2|ttf|otf)$/)) return 'font'
  if (url.match(/\.(mp3|wav|ogg|m4a)$/)) return 'audio'
  if (url.match(/\.(mp4|webm|ogv)$/)) return 'video'
  return 'fetch'
}

/**
 * Critical Resource Preloader Hook
 */
export function useCriticalResourcePreloader() {
  const preloadResource = (url: string, as: string = 'fetch') => {
    if (typeof document === 'undefined') return
    
    const existingLink = document.querySelector(`link[href="${url}"]`)
    if (existingLink) return
    
    const link = document.createElement('link')
    link.rel = 'preload'
    link.href = url
    link.as = as
    
    if (as === 'font') {
      link.crossOrigin = 'anonymous'
    }
    
    document.head.appendChild(link)
  }
  
  const preloadScript = (url: string) => preloadResource(url, 'script')
  const preloadStyle = (url: string) => preloadResource(url, 'style')
  const preloadImage = (url: string) => preloadResource(url, 'image')
  const preloadFont = (url: string) => preloadResource(url, 'font')
  
  return {
    preloadResource,
    preloadScript,
    preloadStyle, 
    preloadImage,
    preloadFont
  }
}

/**
 * Adaptive Resource Loading based on connection speed
 */
export function useAdaptiveLoading() {
  const getConnectionInfo = () => {
    if (typeof navigator === 'undefined' || !('connection' in navigator)) {
      return { effectiveType: '4g', saveData: false }
    }
    
    const connection = (navigator as any).connection
    return {
      effectiveType: connection.effectiveType || '4g',
      saveData: connection.saveData || false,
      downlink: connection.downlink,
      rtt: connection.rtt
    }
  }
  
  const shouldLoadHighQuality = () => {
    const { effectiveType, saveData } = getConnectionInfo()
    
    if (saveData) return false
    if (effectiveType === 'slow-2g' || effectiveType === '2g') return false
    
    return true
  }
  
  const getImageQuality = () => {
    const { effectiveType, saveData } = getConnectionInfo()
    
    if (saveData || effectiveType === 'slow-2g') return 'low'
    if (effectiveType === '2g') return 'medium'
    if (effectiveType === '3g') return 'high'
    
    return 'ultra' // 4g or better
  }
  
  return {
    getConnectionInfo,
    shouldLoadHighQuality,
    getImageQuality
  }
}