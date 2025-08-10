'use client'

import React, { memo, useState, useCallback } from 'react'
import {
  Settings,
  Monitor,
  Bell,
  Shield,
  Database,
  Palette,
  Save,
  RotateCcw,
  Import,
  Download as Export,
  AlertTriangle,
  CheckCircle,
  Info
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useUIStore } from '@/stores/ui-store'

export interface AdvancedSettingsConfig {
  general: {
    autoSave: boolean
    autoSaveInterval: number
    confirmBeforeExit: boolean
    enableAnalytics: boolean
    maxRecentItems: number
    defaultWorkspace: string
  }
  appearance: {
    theme: 'light' | 'dark' | 'blue'
    compactMode: boolean
    reducedMotion: boolean
    showLineNumbers: boolean
    fontSize: 'small' | 'medium' | 'large'
    sidebarWidth: number
  }
  notifications: {
    enableDesktop: boolean
    enableSound: boolean
    taskCompletion: boolean
    errorAlerts: boolean
    systemUpdates: boolean
    emailDigest: boolean
    quietHours: {
      enabled: boolean
      start: string
      end: string
    }
  }
  performance: {
    maxMemoryUsage: number
    enableCaching: boolean
    cacheSize: number
    backgroundSync: boolean
    hardwareAcceleration: boolean
    preloadNextPage: boolean
    virtualScrolling: boolean
  }
  security: {
    enableEncryption: boolean
    sessionTimeout: number
    requirePasswordForSensitiveActions: boolean
    enableTwoFactor: boolean
    auditLogging: boolean
    ipWhitelist: string[]
    allowedFileTypes: string[]
  }
  data: {
    maxHistoryItems: number
    autoBackup: boolean
    backupInterval: 'hourly' | 'daily' | 'weekly'
    retentionPeriod: number
    exportFormat: 'json' | 'csv' | 'pdf'
    compressionEnabled: boolean
    cloudSync: boolean
  }
}

export interface AdvancedSettingsProps {
  config: AdvancedSettingsConfig
  onConfigChange: (config: AdvancedSettingsConfig) => void
  onSave: (config: AdvancedSettingsConfig) => void
  onReset: () => void
  onImport: (file: File) => void
  onExport: (format: 'json' | 'yaml') => void
  className?: string
}

const DEFAULT_CONFIG: AdvancedSettingsConfig = {
  general: {
    autoSave: true,
    autoSaveInterval: 30,
    confirmBeforeExit: true,
    enableAnalytics: true,
    maxRecentItems: 10,
    defaultWorkspace: 'default'
  },
  appearance: {
    theme: 'light',
    compactMode: false,
    reducedMotion: false,
    showLineNumbers: true,
    fontSize: 'medium',
    sidebarWidth: 280
  },
  notifications: {
    enableDesktop: true,
    enableSound: false,
    taskCompletion: true,
    errorAlerts: true,
    systemUpdates: true,
    emailDigest: false,
    quietHours: {
      enabled: false,
      start: '22:00',
      end: '08:00'
    }
  },
  performance: {
    maxMemoryUsage: 1024,
    enableCaching: true,
    cacheSize: 100,
    backgroundSync: true,
    hardwareAcceleration: true,
    preloadNextPage: false,
    virtualScrolling: true
  },
  security: {
    enableEncryption: false,
    sessionTimeout: 24,
    requirePasswordForSensitiveActions: false,
    enableTwoFactor: false,
    auditLogging: true,
    ipWhitelist: [],
    allowedFileTypes: ['txt', 'md', 'json', 'js', 'ts', 'py', 'html', 'css']
  },
  data: {
    maxHistoryItems: 1000,
    autoBackup: false,
    backupInterval: 'daily',
    retentionPeriod: 90,
    exportFormat: 'json',
    compressionEnabled: true,
    cloudSync: false
  }
}

const TAB_CONFIGS = [
  {
    id: 'general',
    label: 'General',
    icon: Settings,
    description: 'Basic application settings and preferences'
  },
  {
    id: 'appearance',
    label: 'Appearance',
    icon: Palette,
    description: 'Visual theme and layout customization'
  },
  {
    id: 'notifications',
    label: 'Notifications',
    icon: Bell,
    description: 'Alert and notification preferences'
  },
  {
    id: 'performance',
    label: 'Performance',
    icon: Monitor,
    description: 'Memory usage and performance optimization'
  },
  {
    id: 'security',
    label: 'Security',
    icon: Shield,
    description: 'Privacy and security configuration'
  },
  {
    id: 'data',
    label: 'Data & Storage',
    icon: Database,
    description: 'Data management and backup settings'
  }
]

const AdvancedSettings = memo<AdvancedSettingsProps>(({
  config,
  onConfigChange,
  onSave,
  onReset,
  onImport,
  onExport,
  className
}) => {
  const { reducedMotion } = useUIStore(state => ({ reducedMotion: state.reducedMotion }))
  const [activeTab, setActiveTab] = useState('general')
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false)

  const handleConfigChange = useCallback((section: keyof AdvancedSettingsConfig, updates: any) => {
    const newConfig = {
      ...config,
      [section]: {
        ...config[section],
        ...updates
      }
    }
    onConfigChange(newConfig)
    setHasUnsavedChanges(true)
  }, [config, onConfigChange])

  const handleSave = useCallback(() => {
    onSave(config)
    setHasUnsavedChanges(false)
  }, [config, onSave])

  const handleReset = useCallback(() => {
    onReset()
    setHasUnsavedChanges(false)
  }, [onReset])

  const handleFileImport = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      onImport(file)
      event.target.value = ''
    }
  }, [onImport])

  const renderGeneralSettings = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">General Settings</h3>
        
        <div className="grid gap-4">
          <div className="flex items-center justify-between">
            <div>
              <label className="font-medium text-gray-700 dark:text-gray-300">Auto-save</label>
              <p className="text-sm text-gray-500">Automatically save changes</p>
            </div>
            <input
              type="checkbox"
              checked={config.general.autoSave}
              onChange={(e) => handleConfigChange('general', { autoSave: e.target.checked })}
              className="w-4 h-4 text-blue-600"
            />
          </div>

          {config.general.autoSave && (
            <div>
              <label className="block font-medium text-gray-700 dark:text-gray-300 mb-2">
                Auto-save interval (seconds)
              </label>
              <input
                type="number"
                min="10"
                max="300"
                value={config.general.autoSaveInterval}
                onChange={(e) => handleConfigChange('general', { autoSaveInterval: parseInt(e.target.value) })}
                className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800"
              />
            </div>
          )}

          <div className="flex items-center justify-between">
            <div>
              <label className="font-medium text-gray-700 dark:text-gray-300">Confirm before exit</label>
              <p className="text-sm text-gray-500">Show confirmation dialog when closing</p>
            </div>
            <input
              type="checkbox"
              checked={config.general.confirmBeforeExit}
              onChange={(e) => handleConfigChange('general', { confirmBeforeExit: e.target.checked })}
              className="w-4 h-4 text-blue-600"
            />
          </div>

          <div>
            <label className="block font-medium text-gray-700 dark:text-gray-300 mb-2">
              Max recent items
            </label>
            <input
              type="number"
              min="5"
              max="50"
              value={config.general.maxRecentItems}
              onChange={(e) => handleConfigChange('general', { maxRecentItems: parseInt(e.target.value) })}
              className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800"
            />
          </div>
        </div>
      </div>
    </div>
  )

  const renderAppearanceSettings = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">Appearance Settings</h3>
        
        <div className="grid gap-4">
          <div>
            <label className="block font-medium text-gray-700 dark:text-gray-300 mb-2">Theme</label>
            <select
              value={config.appearance.theme}
              onChange={(e) => handleConfigChange('appearance', { theme: e.target.value })}
              className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800"
            >
              <option value="light">Light</option>
              <option value="dark">Dark</option>
              <option value="blue">Blue</option>
            </select>
          </div>

          <div>
            <label className="block font-medium text-gray-700 dark:text-gray-300 mb-2">Font Size</label>
            <select
              value={config.appearance.fontSize}
              onChange={(e) => handleConfigChange('appearance', { fontSize: e.target.value })}
              className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800"
            >
              <option value="small">Small</option>
              <option value="medium">Medium</option>
              <option value="large">Large</option>
            </select>
          </div>

          <div>
            <label className="block font-medium text-gray-700 dark:text-gray-300 mb-2">
              Sidebar Width (px)
            </label>
            <input
              type="range"
              min="200"
              max="400"
              step="10"
              value={config.appearance.sidebarWidth}
              onChange={(e) => handleConfigChange('appearance', { sidebarWidth: parseInt(e.target.value) })}
              className="w-full"
            />
            <div className="text-sm text-gray-500 mt-1">{config.appearance.sidebarWidth}px</div>
          </div>

          <div className="flex items-center justify-between">
            <div>
              <label className="font-medium text-gray-700 dark:text-gray-300">Compact mode</label>
              <p className="text-sm text-gray-500">Reduce spacing and padding</p>
            </div>
            <input
              type="checkbox"
              checked={config.appearance.compactMode}
              onChange={(e) => handleConfigChange('appearance', { compactMode: e.target.checked })}
              className="w-4 h-4 text-blue-600"
            />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <label className="font-medium text-gray-700 dark:text-gray-300">Reduced motion</label>
              <p className="text-sm text-gray-500">Disable animations for accessibility</p>
            </div>
            <input
              type="checkbox"
              checked={config.appearance.reducedMotion}
              onChange={(e) => handleConfigChange('appearance', { reducedMotion: e.target.checked })}
              className="w-4 h-4 text-blue-600"
            />
          </div>
        </div>
      </div>
    </div>
  )

  const renderNotificationSettings = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">Notification Settings</h3>
        
        <div className="grid gap-4">
          <div className="flex items-center justify-between">
            <div>
              <label className="font-medium text-gray-700 dark:text-gray-300">Desktop notifications</label>
              <p className="text-sm text-gray-500">Show system notifications</p>
            </div>
            <input
              type="checkbox"
              checked={config.notifications.enableDesktop}
              onChange={(e) => handleConfigChange('notifications', { enableDesktop: e.target.checked })}
              className="w-4 h-4 text-blue-600"
            />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <label className="font-medium text-gray-700 dark:text-gray-300">Sound notifications</label>
              <p className="text-sm text-gray-500">Play sound for notifications</p>
            </div>
            <input
              type="checkbox"
              checked={config.notifications.enableSound}
              onChange={(e) => handleConfigChange('notifications', { enableSound: e.target.checked })}
              className="w-4 h-4 text-blue-600"
            />
          </div>

          <div className="border-t border-gray-200 dark:border-gray-700 pt-4">
            <h4 className="font-medium text-gray-700 dark:text-gray-300 mb-3">Notification Types</h4>
            
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <label className="text-sm text-gray-600 dark:text-gray-400">Task completion</label>
                <input
                  type="checkbox"
                  checked={config.notifications.taskCompletion}
                  onChange={(e) => handleConfigChange('notifications', { taskCompletion: e.target.checked })}
                  className="w-4 h-4 text-blue-600"
                />
              </div>
              
              <div className="flex items-center justify-between">
                <label className="text-sm text-gray-600 dark:text-gray-400">Error alerts</label>
                <input
                  type="checkbox"
                  checked={config.notifications.errorAlerts}
                  onChange={(e) => handleConfigChange('notifications', { errorAlerts: e.target.checked })}
                  className="w-4 h-4 text-blue-600"
                />
              </div>
              
              <div className="flex items-center justify-between">
                <label className="text-sm text-gray-600 dark:text-gray-400">System updates</label>
                <input
                  type="checkbox"
                  checked={config.notifications.systemUpdates}
                  onChange={(e) => handleConfigChange('notifications', { systemUpdates: e.target.checked })}
                  className="w-4 h-4 text-blue-600"
                />
              </div>
            </div>
          </div>

          {config.notifications.quietHours.enabled && (
            <div className="border-t border-gray-200 dark:border-gray-700 pt-4">
              <h4 className="font-medium text-gray-700 dark:text-gray-300 mb-3">Quiet Hours</h4>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-gray-600 dark:text-gray-400 mb-1">Start time</label>
                  <input
                    type="time"
                    value={config.notifications.quietHours.start}
                    onChange={(e) => handleConfigChange('notifications', {
                      quietHours: { ...config.notifications.quietHours, start: e.target.value }
                    })}
                    className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800"
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-600 dark:text-gray-400 mb-1">End time</label>
                  <input
                    type="time"
                    value={config.notifications.quietHours.end}
                    onChange={(e) => handleConfigChange('notifications', {
                      quietHours: { ...config.notifications.quietHours, end: e.target.value }
                    })}
                    className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800"
                  />
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )

  const renderPerformanceSettings = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">Performance Settings</h3>
        
        <div className="grid gap-4">
          <div>
            <label className="block font-medium text-gray-700 dark:text-gray-300 mb-2">
              Max memory usage (MB)
            </label>
            <input
              type="number"
              min="256"
              max="4096"
              step="64"
              value={config.performance.maxMemoryUsage}
              onChange={(e) => handleConfigChange('performance', { maxMemoryUsage: parseInt(e.target.value) })}
              className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800"
            />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <label className="font-medium text-gray-700 dark:text-gray-300">Enable caching</label>
              <p className="text-sm text-gray-500">Cache data for faster access</p>
            </div>
            <input
              type="checkbox"
              checked={config.performance.enableCaching}
              onChange={(e) => handleConfigChange('performance', { enableCaching: e.target.checked })}
              className="w-4 h-4 text-blue-600"
            />
          </div>

          {config.performance.enableCaching && (
            <div>
              <label className="block font-medium text-gray-700 dark:text-gray-300 mb-2">
                Cache size (MB)
              </label>
              <input
                type="number"
                min="10"
                max="500"
                value={config.performance.cacheSize}
                onChange={(e) => handleConfigChange('performance', { cacheSize: parseInt(e.target.value) })}
                className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800"
              />
            </div>
          )}

          <div className="flex items-center justify-between">
            <div>
              <label className="font-medium text-gray-700 dark:text-gray-300">Hardware acceleration</label>
              <p className="text-sm text-gray-500">Use GPU for rendering when available</p>
            </div>
            <input
              type="checkbox"
              checked={config.performance.hardwareAcceleration}
              onChange={(e) => handleConfigChange('performance', { hardwareAcceleration: e.target.checked })}
              className="w-4 h-4 text-blue-600"
            />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <label className="font-medium text-gray-700 dark:text-gray-300">Virtual scrolling</label>
              <p className="text-sm text-gray-500">Improve performance for large lists</p>
            </div>
            <input
              type="checkbox"
              checked={config.performance.virtualScrolling}
              onChange={(e) => handleConfigChange('performance', { virtualScrolling: e.target.checked })}
              className="w-4 h-4 text-blue-600"
            />
          </div>
        </div>
      </div>
    </div>
  )

  const renderSecuritySettings = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">Security Settings</h3>
        
        <div className="grid gap-4">
          <div>
            <label className="block font-medium text-gray-700 dark:text-gray-300 mb-2">
              Session timeout (hours)
            </label>
            <input
              type="number"
              min="1"
              max="168"
              value={config.security.sessionTimeout}
              onChange={(e) => handleConfigChange('security', { sessionTimeout: parseInt(e.target.value) })}
              className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800"
            />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <label className="font-medium text-gray-700 dark:text-gray-300">Enable encryption</label>
              <p className="text-sm text-gray-500">Encrypt sensitive data at rest</p>
            </div>
            <input
              type="checkbox"
              checked={config.security.enableEncryption}
              onChange={(e) => handleConfigChange('security', { enableEncryption: e.target.checked })}
              className="w-4 h-4 text-blue-600"
            />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <label className="font-medium text-gray-700 dark:text-gray-300">Audit logging</label>
              <p className="text-sm text-gray-500">Log security-related events</p>
            </div>
            <input
              type="checkbox"
              checked={config.security.auditLogging}
              onChange={(e) => handleConfigChange('security', { auditLogging: e.target.checked })}
              className="w-4 h-4 text-blue-600"
            />
          </div>

          <div>
            <label className="block font-medium text-gray-700 dark:text-gray-300 mb-2">
              Allowed file types
            </label>
            <input
              type="text"
              value={config.security.allowedFileTypes.join(', ')}
              onChange={(e) => handleConfigChange('security', {
                allowedFileTypes: e.target.value.split(',').map(t => t.trim()).filter(Boolean)
              })}
              placeholder="txt, md, json, js, ts, py"
              className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800"
            />
            <p className="text-sm text-gray-500 mt-1">Comma-separated list of allowed file extensions</p>
          </div>
        </div>
      </div>
    </div>
  )

  const renderDataSettings = () => (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900 dark:text-gray-100 mb-4">Data & Storage Settings</h3>
        
        <div className="grid gap-4">
          <div>
            <label className="block font-medium text-gray-700 dark:text-gray-300 mb-2">
              Max history items
            </label>
            <input
              type="number"
              min="100"
              max="10000"
              step="100"
              value={config.data.maxHistoryItems}
              onChange={(e) => handleConfigChange('data', { maxHistoryItems: parseInt(e.target.value) })}
              className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800"
            />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <label className="font-medium text-gray-700 dark:text-gray-300">Auto backup</label>
              <p className="text-sm text-gray-500">Automatically backup data</p>
            </div>
            <input
              type="checkbox"
              checked={config.data.autoBackup}
              onChange={(e) => handleConfigChange('data', { autoBackup: e.target.checked })}
              className="w-4 h-4 text-blue-600"
            />
          </div>

          {config.data.autoBackup && (
            <div>
              <label className="block font-medium text-gray-700 dark:text-gray-300 mb-2">Backup interval</label>
              <select
                value={config.data.backupInterval}
                onChange={(e) => handleConfigChange('data', { backupInterval: e.target.value })}
                className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800"
              >
                <option value="hourly">Hourly</option>
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
              </select>
            </div>
          )}

          <div>
            <label className="block font-medium text-gray-700 dark:text-gray-300 mb-2">
              Data retention (days)
            </label>
            <input
              type="number"
              min="7"
              max="365"
              value={config.data.retentionPeriod}
              onChange={(e) => handleConfigChange('data', { retentionPeriod: parseInt(e.target.value) })}
              className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-800"
            />
          </div>

          <div className="flex items-center justify-between">
            <div>
              <label className="font-medium text-gray-700 dark:text-gray-300">Compression</label>
              <p className="text-sm text-gray-500">Compress data to save space</p>
            </div>
            <input
              type="checkbox"
              checked={config.data.compressionEnabled}
              onChange={(e) => handleConfigChange('data', { compressionEnabled: e.target.checked })}
              className="w-4 h-4 text-blue-600"
            />
          </div>
        </div>
      </div>
    </div>
  )

  const renderTabContent = () => {
    switch (activeTab) {
      case 'general':
        return renderGeneralSettings()
      case 'appearance':
        return renderAppearanceSettings()
      case 'notifications':
        return renderNotificationSettings()
      case 'performance':
        return renderPerformanceSettings()
      case 'security':
        return renderSecuritySettings()
      case 'data':
        return renderDataSettings()
      default:
        return renderGeneralSettings()
    }
  }

  return (
    <div className={cn('flex h-full bg-white dark:bg-gray-900', className)}>
      {/* Sidebar */}
      <div className="w-64 border-r border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800">
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-gray-100">Settings</h2>
        </div>
        
        <nav className="p-2">
          {TAB_CONFIGS.map((tab) => {
            const IconComponent = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={cn(
                  'w-full flex items-center gap-3 px-3 py-2 rounded-md text-left',
                  activeTab === tab.id
                    ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300'
                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700',
                  !reducedMotion && 'transition-colors duration-200'
                )}
              >
                <IconComponent className="w-5 h-5 flex-shrink-0" />
                <div className="min-w-0 flex-1">
                  <div className="font-medium">{tab.label}</div>
                  <div className="text-xs text-gray-500 truncate">{tab.description}</div>
                </div>
              </button>
            )
          })}
        </nav>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-3">
            {TAB_CONFIGS.find(t => t.id === activeTab)?.icon && (
              React.createElement(TAB_CONFIGS.find(t => t.id === activeTab)!.icon, {
                className: 'w-6 h-6 text-blue-500'
              })
            )}
            <div>
              <h1 className="text-xl font-semibold text-gray-900 dark:text-gray-100">
                {TAB_CONFIGS.find(t => t.id === activeTab)?.label}
              </h1>
              <p className="text-sm text-gray-500">
                {TAB_CONFIGS.find(t => t.id === activeTab)?.description}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            {hasUnsavedChanges && (
              <div className="flex items-center gap-1 text-amber-600 text-sm">
                <AlertTriangle className="w-4 h-4" />
                Unsaved changes
              </div>
            )}

            <input
              type="file"
              accept=".json,.yaml,.yml"
              onChange={handleFileImport}
              className="hidden"
              id="settings-import"
            />
            
            <button
              onClick={() => document.getElementById('settings-import')?.click()}
              className={cn(
                'px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700',
                !reducedMotion && 'transition-colors duration-200'
              )}
            >
              <Import className="w-4 h-4 mr-1" />
              Import
            </button>

            <button
              onClick={() => onExport('json')}
              className={cn(
                'px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700',
                !reducedMotion && 'transition-colors duration-200'
              )}
            >
              <Export className="w-4 h-4 mr-1" />
              Export
            </button>

            <button
              onClick={handleReset}
              className={cn(
                'px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700',
                !reducedMotion && 'transition-colors duration-200'
              )}
            >
              <RotateCcw className="w-4 h-4 mr-1" />
              Reset
            </button>

            <button
              onClick={handleSave}
              disabled={!hasUnsavedChanges}
              className={cn(
                'px-3 py-1.5 text-sm rounded-md',
                hasUnsavedChanges
                  ? 'bg-blue-600 text-white hover:bg-blue-700'
                  : 'bg-gray-100 dark:bg-gray-700 text-gray-400 cursor-not-allowed',
                !reducedMotion && 'transition-colors duration-200'
              )}
            >
              <Save className="w-4 h-4 mr-1" />
              Save Changes
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-auto p-6">
          {renderTabContent()}
        </div>
      </div>
    </div>
  )
})

AdvancedSettings.displayName = 'AdvancedSettings'

export default AdvancedSettings