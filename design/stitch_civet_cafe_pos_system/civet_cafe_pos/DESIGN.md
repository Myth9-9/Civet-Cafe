---
name: Civet Cafe POS
colors:
  surface: '#fff8f6'
  surface-dim: '#fbd1c4'
  surface-bright: '#fff8f6'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#fff1ed'
  surface-container: '#ffe9e3'
  surface-container-high: '#ffe2da'
  surface-container-highest: '#ffdbd0'
  on-surface: '#2c160e'
  on-surface-variant: '#504442'
  inverse-surface: '#442a22'
  inverse-on-surface: '#ffede8'
  outline: '#827472'
  outline-variant: '#d3c3c0'
  surface-tint: '#745853'
  primary: '#271310'
  on-primary: '#ffffff'
  primary-container: '#3e2723'
  on-primary-container: '#ae8d87'
  inverse-primary: '#e3beb8'
  secondary: '#655d5a'
  on-secondary: '#ffffff'
  secondary-container: '#ece0dc'
  on-secondary-container: '#6b6360'
  tertiary: '#181818'
  on-tertiary: '#ffffff'
  tertiary-container: '#2c2d2c'
  on-tertiary-container: '#959492'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#ffdad4'
  primary-fixed-dim: '#e3beb8'
  on-primary-fixed: '#2b1613'
  on-primary-fixed-variant: '#5b403c'
  secondary-fixed: '#ece0dc'
  secondary-fixed-dim: '#cfc4c0'
  on-secondary-fixed: '#201a18'
  on-secondary-fixed-variant: '#4c4542'
  tertiary-fixed: '#e4e2e0'
  tertiary-fixed-dim: '#c7c6c4'
  on-tertiary-fixed: '#1b1c1b'
  on-tertiary-fixed-variant: '#464746'
  background: '#fff8f6'
  on-background: '#2c160e'
  surface-variant: '#ffdbd0'
typography:
  display-lg:
    fontFamily: Lexend
    fontSize: 40px
    fontWeight: '600'
    lineHeight: 48px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Lexend
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
  headline-md:
    fontFamily: Lexend
    fontSize: 24px
    fontWeight: '500'
    lineHeight: 32px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-lg:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: 0.01em
  label-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.04em
  headline-lg-mobile:
    fontFamily: Lexend
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 8px
  xs: 4px
  sm: 12px
  md: 24px
  lg: 40px
  grid-gutter: 16px
  pos-touch-target: 48px
---

## Brand & Style
The brand personality is artisanal yet efficient, blending the warmth of a boutique coffee house with the precision of high-performance software. The target audience includes baristas, cafe managers, and servers who require a tool that feels natural in a hospitality environment while maintaining rigorous functional speed.

The design style is **Modern Corporate with Tactile Warmth**. It leans into a "Soft Minimalist" aesthetic, utilizing heavy whitespace and a refined color palette to reduce cognitive load during peak hours. The emotional response should be one of calm reliability—using organic tones to offset the stress of a fast-paced retail environment.

## Colors
The palette is grounded in a "Bean-to-Cup" narrative. 
- **Primary (Deep Espresso):** Used for critical actions, navigation headers, and primary branding elements to provide a strong visual anchor.
- **Secondary (Warm Latte):** Applied to secondary buttons, toggle backgrounds, and subtle dividers to maintain warmth without high contrast.
- **Tertiary (Cream):** The main surface color, providing a soft, non-clinical alternative to pure white.
- **Accents:** Soft Sage signals availability and "paid" statuses, while Terracotta indicates occupied tables or urgent errors.

This design system fully supports dark mode, where surfaces transition to "Roast Black" (#1B1311) and text shifts to low-contrast creams to prevent eye strain in dimly lit evening service.

## Typography
The typography strategy prioritizes legibility at a distance (for tablet use) and rapid scanning. **Lexend** is used for headlines and numerical values (prices, totals) because its expanded character width and geometric clarity make it exceptionally readable for quick glancing. 

**Inter** handles all body copy and UI labels. It provides a systematic, utilitarian feel that ensures dense POS grids remain organized. Use `label-lg` for button text and `label-sm` for metadata like timestamps or tax breakdown to maintain a clear information hierarchy.

## Layout & Spacing
The layout uses a **Fluid Grid** for the main POS terminal and a **Fixed Sidebar** for the current order/basket. 
- **Desktop:** 12-column grid with 24px margins. The product gallery occupies 8 columns; the receipt sidebar occupies 4 columns.
- **Tablet:** 8-column grid with 16px margins. The receipt sidebar is collapsible to maximize the product selection area.
- **Touch-First Design:** All interactive elements (buttons, list items) must adhere to a minimum 48px height to ensure high-accuracy input during fast service. High-density layouts are achieved by reducing internal padding within cards while maintaining generous outer margins between functional groups.

## Elevation & Depth
The design system employs **Tonal Layers** combined with **Ambient Shadows**. Instead of harsh black shadows, we use shadows tinted with the primary espresso hue (e.g., `rgba(62, 39, 35, 0.08)`) to maintain the warm aesthetic.

- **Level 0 (Base):** The main application background in Cream (#FDFBF9).
- **Level 1 (Cards):** Slightly elevated with a 4px blur shadow. Used for product items and menu categories.
- **Level 2 (Active/Floating):** Used for the active order sidebar and modals, featuring an 12px blur to suggest it sits atop the workspace.
- **Interactive Depth:** Buttons use a subtle inner shadow on "pressed" states to simulate a tactile, physical push, reinforcing the café-environment feel.

## Shapes
The shape language is purposefully **Rounded** to evoke a friendly, organic atmosphere. 
- **Standard UI Elements (Buttons, Inputs):** 0.5rem (8px) radius.
- **Product Cards:** 1rem (16px) radius to create a soft, approachable "tiled" look in the menu grid.
- **Status Indicators (Pills):** Fully rounded (pill-shaped) to distinguish them from functional buttons.
- **Selection States:** Use a 2px solid border in Espresso to highlight selected items, maintaining the rounded geometry.

## Components
- **Buttons:** Primary buttons are Solid Espresso with Cream text. Secondary buttons are Ghost-style with a Latte border. Active/Success buttons (Pay/Complete) use the Sage accent.
- **Product Cards:** High-density cards featuring a top-aligned image (optional), middle-aligned name in `label-lg`, and bottom-aligned price in `headline-md`.
- **Order List:** Use zebra-striping with a very light Latte tint (#F5F0EE) for every second row to assist in line-item tracking.
- **Chips/Status:** Used for table status (e.g., "Table 4 - Occupied"). They use a low-opacity background of the accent color with high-opacity text of the same hue for maximum accessibility.
- **Input Fields:** Soft beige backgrounds with Espresso bottom-borders that animate to a full outline on focus.
- **Numpad:** A custom component for the POS featuring oversized touch targets (64px+) with Lexend typography for rapid numerical entry.