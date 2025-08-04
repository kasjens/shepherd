# 🎨 Design System

UI/UX design system and visual guidelines for Shepherd.

## 📋 Design Documentation

### Component System
- **[UI Components](ui-components.md)** - Complete component library and specifications
- **[Layout System](layout-system.md)** - Grid system, spacing, and responsive design
- **[Theme Design](theme-design.md)** - Color palettes, typography, and visual identity

### Style Guidelines  
- **[Style Guide](style-guide.md)** - Brand guidelines and design principles *(Coming Soon)*

## 🎯 Design Overview

### Design Principles
- **Professional & Clean** - Enterprise-grade visual appearance
- **Intuitive Navigation** - Clear information hierarchy
- **Responsive Design** - Seamless across all screen sizes
- **Accessibility First** - WCAG 2.1 AA compliance
- **Performance Focused** - Optimized for fast loading

### Technology Stack
- **Next.js 15** - React framework with App Router
- **Tailwind CSS 4** - Utility-first styling
- **Shadcn/ui** - High-quality component primitives
- **Tauri 2** - Native desktop integration
- **TypeScript** - Type-safe development

## 🌈 Theme System

### Available Themes
- **Light Theme** - Clean, bright interface for daily use
- **Dark Theme** - Reduced eye strain for extended sessions  
- **Blue Theme** - Professional corporate appearance

### Theme Features
- **System Integration** - Respects OS theme preferences
- **Persistent Storage** - Theme choice remembered across sessions
- **Smooth Transitions** - Animated theme switching
- **High Contrast** - Accessible color ratios

## 📱 Layout Architecture

### Three-Panel Layout
```
┌─────────────────────────────────────────────┐
│                 Top Bar                     │
├──────────┬──────────────────┬───────────────┤
│   Left   │       Main       │     Right     │
│  Panel   │     Content      │    Panel      │
│  (25%)   │      (50%)       │    (25%)      │
│          │                  │               │
└──────────┴──────────────────┴───────────────┘
```

### Responsive Breakpoints
- **Desktop**: 1200px+ (three-panel layout)
- **Tablet**: 768px-1199px (collapsible panels)
- **Mobile**: <768px (single-panel with navigation)

## 🎨 Visual Identity

### Color System
- **Primary**: Blue gradient palette
- **Secondary**: Neutral grays  
- **Accent**: Status colors (success, warning, error)
- **Surface**: Background and card colors

### Typography
- **Headings**: Inter font family
- **Body**: System font stack
- **Code**: JetBrains Mono

## 🔗 Related Resources

- **[Architecture](../04-architecture/)** - Technical component architecture
- **[Development](../05-development/)** - GUI development workflow
- **[User Guides](../02-user-guides/)** - Feature usage documentation

---

**Start with [UI Components](ui-components.md) for the complete component library!**