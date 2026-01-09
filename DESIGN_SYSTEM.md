# College Portal - Design System Documentation

## 🎨 Design Foundation

### Design Philosophy
- **Modern SaaS Aesthetic**: Clean, professional, with subtle depth
- **Light Theme with Gradients**: Soft backgrounds with colorful accents
- **Glassmorphism**: Frosted glass effects with backdrop blur
- **Micro-interactions**: Smooth transitions and hover states
- **Accessible**: High contrast, readable typography, WCAG compliant

---

## 🎭 Color System

### Background Gradients
```css
/* Primary Background */
bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50

/* Gradient Orbs (Decorative) */
- Top Right: from-blue-400/20 to-indigo-400/20
- Middle Left: from-violet-400/15 to-purple-400/15  
- Bottom Right: from-cyan-400/20 to-blue-400/20
```

### Component Gradients by Feature

#### Navigation & Primary Actions
- **Dashboard**: `hover:from-blue-50 hover:to-indigo-50` + `text-blue-700`
- **Students**: `hover:from-violet-50 hover:to-purple-50` + `text-violet-700`
- **Courses**: `hover:from-emerald-50 hover:to-teal-50` + `text-emerald-700`
- **My Courses**: `hover:from-indigo-50 hover:to-blue-50` + `text-indigo-700`
- **Grading**: `hover:from-amber-50 hover:to-orange-50` + `text-amber-700`
- **Transcripts**: `hover:from-cyan-50 hover:to-sky-50` + `text-cyan-700`
- **Analytics**: `hover:from-rose-50 hover:to-pink-50` + `text-rose-700`
- **Django Admin**: `hover:from-slate-100 hover:to-slate-200` + `text-slate-900`

#### Stat Cards
```css
/* Users Card */
bg-gradient-to-br from-blue-50 to-indigo-50
Icon: from-blue-600 to-indigo-600
Shadow: shadow-blue-500/30

/* Students Card */
bg-gradient-to-br from-violet-50 to-purple-50
Icon: from-violet-600 to-purple-600
Shadow: shadow-violet-500/30

/* Course Offerings Card */
bg-gradient-to-br from-teal-50 to-cyan-50
Icon: from-teal-600 to-cyan-600
Shadow: shadow-teal-500/30
```

#### Buttons & CTAs
```css
/* Primary Button */
bg-gradient-to-r from-blue-600 to-indigo-600
shadow-lg shadow-blue-500/30
hover:shadow-xl hover:scale-105

/* Secondary Button */
border border-slate-200 bg-white
hover:bg-slate-50 hover:shadow-md
```

---

## 📐 Layout Structure

### Fixed Sidebar Layout
```
┌─────────────────────────────────────────┐
│  Sidebar (Fixed)    │   Main Content    │
│  264px wide         │   Flexible        │
│                     │                   │
│  ┌──────────────┐   │  ┌─────────────┐ │
│  │  Logo/Brand  │   │  │  Top Bar    │ │
│  ├──────────────┤   │  ├─────────────┤ │
│  │              │   │  │             │ │
│  │  Navigation  │   │  │   Content   │ │
│  │              │   │  │             │ │
│  ├──────────────┤   │  │             │ │
│  │  User Info   │   │  │             │ │
│  └──────────────┘   │  └─────────────┘ │
└─────────────────────────────────────────┘
```

### Sidebar Specifications
- **Width**: `w-64` (256px)
- **Position**: `fixed inset-y-0 left-0`
- **Z-index**: `z-50`
- **Background**: `bg-white/80 backdrop-blur-xl`
- **Border**: `border-r border-white/10`
- **Shadow**: `shadow-2xl`

### Main Content Area
- **Offset**: `lg:pl-64` (matches sidebar width)
- **Top Bar**: Sticky with breadcrumbs
- **Content Padding**: `p-4 lg:p-6`

### Mobile Responsive
- Sidebar hidden by default: `-translate-x-full lg:translate-x-0`
- Hamburger menu shows sidebar overlay
- Backdrop overlay: `bg-slate-900/50 backdrop-blur-sm`

---

## 🎯 Component Patterns

### Card Component
```html
<div class="rounded-2xl border border-slate-200/60 bg-white/90 p-6 shadow-lg backdrop-blur-xl transition-all hover:shadow-2xl hover:-translate-y-1">
  <!-- Card content -->
</div>
```

**Variants:**
- **Stat Card**: Add gradient background + decorative blur orb
- **Action Card**: Add relative positioning for gradient orb effect
- **Info Card**: Use `from-white/90 to-blue-50/50` gradient

### Navigation Link
```html
<a class="group flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium text-slate-700 transition-all hover:bg-gradient-to-r hover:from-[color]-50 hover:to-[color]-50 hover:text-[color]-700">
  <svg class="h-5 w-5 text-slate-400 group-hover:text-[color]-600 transition">
    <!-- Icon -->
  </svg>
  Label
</a>
```

### Button Component
```html
<!-- Primary -->
<button class="inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-blue-500/30 transition-all hover:shadow-xl hover:scale-105 active:scale-95">
  Text
  <svg><!-- Icon --></svg>
</button>

<!-- Secondary -->
<button class="inline-flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 shadow-sm transition-all hover:bg-slate-50 hover:shadow-md active:scale-95">
  Text
</button>
```

### Toast Notification
```html
<div class="flex items-start gap-3 rounded-xl border border-slate-200 bg-white/95 backdrop-blur-xl px-4 py-3 shadow-2xl">
  <div class="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-blue-600 to-indigo-600 text-white">
    <svg><!-- Icon --></svg>
  </div>
  <div class="flex-1 text-sm font-medium text-slate-800">Message</div>
  <button class="text-slate-400 hover:text-slate-600 transition">
    <svg><!-- Close icon --></svg>
  </button>
</div>
```

---

## ✨ Animation & Transitions

### Standard Transitions
```css
/* Default for interactive elements */
transition-all

/* Hover scale effects */
hover:scale-105      /* Buttons, cards */
active:scale-95      /* Button press */
hover:-translate-y-1 /* Card lift */

/* Backdrop transitions */
backdrop-blur-xl
```

### Alpine.js Transitions
```html
<!-- Fade In/Out -->
x-transition:enter="transition ease-out duration-300"
x-transition:enter-start="translate-y-2 opacity-0"
x-transition:enter-end="translate-y-0 opacity-100"

<!-- Sidebar slide -->
x-transition:enter="transition-opacity ease-linear duration-300"
```

---

## 📝 Typography

### Font Family
```css
font-family: 'Inter', system-ui, sans-serif
```

### Font Sizes & Weights
```css
/* Page Title */
text-3xl font-bold

/* Section Title */
text-xl font-bold

/* Card Title */
text-lg font-bold

/* Navigation Item */
text-sm font-medium

/* Body Text */
text-sm text-slate-600

/* Caption/Help Text */
text-xs text-slate-500
```

### Text Colors
```css
/* Headings */
text-slate-900

/* Body Text */
text-slate-700 (default)
text-slate-600 (secondary)

/* Muted/Helper Text */
text-slate-500
text-slate-400 (icons)
```

### Gradient Text
```css
bg-gradient-to-r from-blue-700 to-indigo-600 bg-clip-text text-transparent
```

---

## 🎪 Effects Library

### Glassmorphism
```css
bg-white/80 backdrop-blur-xl
bg-white/90 backdrop-blur-xl
border border-white/10
```

### Gradient Orbs (Decorative)
```html
<div class="absolute -right-4 -top-4 h-20 w-20 rounded-full bg-[color]-400/10 blur-2xl transition-all group-hover:scale-150"></div>
```

### Box Shadows
```css
/* Cards */
shadow-lg        /* Default */
shadow-xl        /* Elevated */
shadow-2xl       /* Prominent */

/* With color tint */
shadow-lg shadow-blue-500/30
```

---

## 📱 Responsive Breakpoints

```css
/* Mobile First Approach */
sm:   640px   /* Small tablets */
md:   768px   /* Tablets */
lg:   1024px  /* Desktop (sidebar shows) */
xl:   1280px  /* Large desktop */
2xl:  1536px  /* Extra large */
```

### Common Patterns
```css
/* Hide on mobile, show on desktop */
hidden lg:block

/* Full width on mobile, grid on desktop */
grid-cols-1 lg:grid-cols-3

/* Stack on mobile, flex on desktop */
flex-col lg:flex-row
```

---

## 🎨 Icon System

### Heroicons (Outline)
- **Size**: `h-5 w-5` for navigation, `h-6 w-6` for cards
- **Stroke Width**: `stroke-width="2"`
- **Color**: `text-slate-400` default, changes on hover with `group-hover:text-[color]-600`

### Icon Colors by Context
- Dashboard: `text-blue-600`
- Students: `text-violet-600`
- Courses: `text-emerald-600`
- Grading: `text-amber-600`
- Transcripts: `text-cyan-600`
- Analytics: `text-rose-600`

---

## 🔧 Utility Classes Reference

### Spacing Scale
```css
gap-3    /* 12px */
gap-4    /* 16px */
gap-6    /* 24px */
gap-8    /* 32px */

p-3, p-4, p-6, p-8
px-4, py-2.5
```

### Border Radius
```css
rounded-lg     /* 8px - buttons */
rounded-xl     /* 12px - cards, inputs */
rounded-2xl    /* 16px - major cards */
rounded-full   /* Pills, avatars */
```

### Borders
```css
border border-slate-200       /* Default */
border border-slate-200/60    /* Subtle */
border border-white/10        /* On gradients */
```

---

## 📋 Page Template Structure

```html
{% extends 'portal/base.html' %}

{% block title %}Page Title | College Portal{% endblock %}

{% block breadcrumb %}
<svg class="h-4 w-4 text-slate-400"><!-- Arrow --></svg>
<span class="text-slate-900 font-medium">Current Page</span>
{% endblock %}

{% block body %}
<div class="space-y-8">
  <!-- Page Header -->
  <div class="rounded-2xl border border-slate-200/60 bg-gradient-to-br from-white/90 to-blue-50/50 p-8 shadow-xl backdrop-blur-xl">
    <h1 class="text-3xl font-bold bg-gradient-to-r from-blue-700 to-indigo-600 bg-clip-text text-transparent">
      Page Title
    </h1>
    <p class="mt-2 text-slate-600 font-medium">Description</p>
  </div>

  <!-- Content Sections -->
  <div>
    <h2 class="text-xl font-bold text-slate-900 mb-4">Section Title</h2>
    <!-- Content -->
  </div>
</div>
{% endblock %}
```

---

## 🎯 Best Practices

### DO ✅
- Use gradient backgrounds for visual hierarchy
- Maintain consistent spacing (multiples of 4)
- Add hover states to all interactive elements
- Use backdrop-blur for depth
- Keep text readable (proper contrast)
- Add smooth transitions
- Use role-based visibility

### DON'T ❌
- Overuse bright gradients (keep them subtle)
- Mix too many gradient colors in one view
- Use pure black or pure white
- Skip mobile responsiveness
- Forget loading states
- Remove ARIA labels
- Hardcode colors (use Tailwind classes)

---

## 🚀 Component Checklist

When building a new page/component:

- [ ] Page header with gradient background
- [ ] Breadcrumb navigation
- [ ] Proper spacing (space-y-8 for sections)
- [ ] Role-based visibility (`{% if is_admin %}`)
- [ ] Responsive grid layouts
- [ ] Hover states on interactive elements
- [ ] Loading states for async content
- [ ] Error handling UI
- [ ] Mobile-friendly layout
- [ ] Proper semantic HTML
- [ ] HTMX for dynamic updates where needed
- [ ] Alpine.js for client-side interactions

---

## 📚 Resources

- **Font**: Inter (Google Fonts)
- **Icons**: Heroicons Outline
- **CSS Framework**: Tailwind CSS v4
- **JS Libraries**: Alpine.js, HTMX
- **Color Palette**: Tailwind Default Colors

---

**Last Updated**: January 7, 2026
**Version**: 1.0.0
