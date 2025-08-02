/** @type {import('next').NextConfig} */
const nextConfig = {
  // Basic configuration for development
  reactStrictMode: true,
  
  // Handle external modules and Tauri API
  webpack: (config, { isServer }) => {
    // Ignore Tauri modules during build
    config.externals = [...(config.externals || []), '@tauri-apps/api']
    
    return config
  },
}

module.exports = nextConfig