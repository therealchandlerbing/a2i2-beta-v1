# Arcus Innovation Studios - Quick Reference

**Fast lookup for Design Director integration**

---

## Color Palette

### Primary Colors

| Color | Hex | RGB | CSS Variable | Use Case |
|-------|-----|-----|--------------|----------|
| **Arcus Navy** | `#0A2540` | 10, 37, 64 | `--arcus-navy` | Headers, formal text, primary brand, document titles |
| **Arcus Teal** | `#00BFB3` | 0, 191, 179 | `--arcus-teal` | Accents, CTAs, data highlights, strategic emphasis |
| **Arcus Slate** | `#425466` | 66, 84, 102 | `--arcus-slate` | Secondary text, subheadings |
| **Charcoal** | `#1A1F36` | 26, 31, 54 | `--arcus-charcoal` | Body text, paragraphs |
| **White** | `#FFFFFF` | 255, 255, 255 | `--arcus-white` | Backgrounds, negative space |

### Neutral Colors

| Color | Hex | CSS Variable | Use Case |
|-------|-----|--------------|----------|
| **Gray 50** | `#FAFBFC` | `--arcus-gray-50` | Lightest backgrounds |
| **Gray 100** | `#F3F4F6` | `--arcus-gray-100` | Subtle backgrounds, cards |
| **Gray 200** | `#E5E7EB` | `--arcus-gray-200` | Borders, dividers |
| **Gray 300** | `#D1D5DB` | `--arcus-gray-300` | Inactive elements |
| **Gray 600** | `#6B7280` | `--arcus-gray-600` | Supporting text, captions |
| **Gray 700** | `#425466` | `--arcus-gray-700` | Secondary text (same as Slate) |
| **Gray 900** | `#1A1F36` | `--arcus-gray-900` | Primary text (same as Charcoal) |

### Accent Colors (Use Sparingly)

| Color | Hex | CSS Variable | Use Case |
|-------|-----|--------------|----------|
| **Success Green** | `#10B981` | `--arcus-green` | Positive metrics, success states |
| **Warning Amber** | `#F59E0B` | `--arcus-amber` | Cautions, attention items |
| **Alert Red** | `#EF4444` | `--arcus-red` | Risks, critical items, errors |
| **Blue Light** | `#0096FF` | `--arcus-blue-light` | Charts, data viz, alt accent |

### Color Combinations

**Professional (Default):**
- Navy + Teal + White + Charcoal

**Data-Focused:**
- Navy + Gray scale + Teal accents

**Strategic Innovation:**
- Navy + Teal + Blue Light

---

## Typography Hierarchy

| Level | Size | Weight | Color | Line Height | Use Case |
|-------|------|--------|-------|-------------|----------|
| **H1 - Document Titles** | 32-36px (print)<br>36-48px (digital) | 700 (Bold) | Navy | 1.2 | Document titles, main headers |
| **H2 - Section Headers** | 24-28px (print)<br>24-32px (digital) | 600-700 | Navy | 1.3 | Section headers, slide titles |
| **H3 - Subsections** | 18-20px | 600 | Slate or Navy | 1.4 | Subsections, protocols |
| **Body Text** | 14px (std)<br>15-16px (optimal) | 400 | Charcoal | 1.7 | Paragraphs, main content |
| **Caption/Small** | 12px | 400 | Gray 600 | 1.5 | Footnotes, captions |
| **Legal/Footer** | 10px | 400 | Gray 600 | 1.4 | Legal text, footer info |

### Font Stack

```css
/* Primary (System Sans) */
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;

/* Monospace (Data/Code) */
font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
```

### Typography Quick Rules

- **Hierarchy:** 2.5-3x size difference between H1 and body
- **Line Height:** 1.7 for body, 1.2-1.4 for headings
- **Letter Spacing:** -0.02em for large text, 0 for body
- **Max Line Length:** 50-75 characters for readability

---

## Logo Usage Matrix

| Document Type | Logo Placement | Size | Variation |
|---------------|---------------|------|-----------|
| **Letterhead** | Top left | 2-2.5" width | Navy on White |
| **Presentations (title)** | Centered | 2-3" width | Navy on White or White on Navy |
| **Presentations (slides)** | Top right | 1-1.5" width | Navy on White (small) |
| **Reports** | Top left or center | 2-2.5" width | Navy on White |
| **Proposals (cover)** | Top left | 2-3" width | Navy on White |
| **Contracts** | Centered header | 2-2.5" width | Navy on White |
| **Business Cards** | Front - left/center | 1-1.5" width | Navy on White or White on Navy |

### Logo Minimum Sizes

- **Print:** 0.75 inches (19mm) width minimum
- **Digital:** 120px width minimum
- **Presentations:** 1.5 inches (38mm) recommended
- **Business Cards:** 1 inch (25mm) minimum

### Logo Clear Space

Maintain clear space equal to **height of letter "A"** on all sides.

---

## Spacing System (8pt Grid)

| Size | Pixels | CSS Variable | Use Case |
|------|--------|--------------|----------|
| **XS** | 4px | `--space-xs` | Tight spacing, minor adjustments |
| **SM** | 8px | `--space-sm` | List items, close relationships |
| **MD** | 16px | `--space-md` | Paragraph spacing, standard gaps |
| **LG** | 24px | `--space-lg` | Section spacing, cards |
| **XL** | 32px | `--space-xl` | Major sections, page elements |
| **2XL** | 48px | `--space-2xl` | Section margins, major divisions |
| **3XL** | 64px | `--space-3xl` | Page sections, large spacing |
| **4XL** | 96px | `--space-4xl` | Page margins, document edges |

### Common Spacing Applications

| Context | Spacing | Usage |
|---------|---------|-------|
| Between paragraphs | 16px (MD) | Standard body text |
| Section margins | 48-64px (2XL-3XL) | Major content sections |
| List item spacing | 8px (SM) | Vertical rhythm |
| Card padding | 24-32px (LG-XL) | Content cards, callouts |
| Page margins | 48-96px (2XL-4XL) | Document edges |
| Header spacing | 32-48px (XL-2XL) | After headers |

---

## Document Templates Quick Specs

### Letterhead

- **Page Size:** 8.5" × 11" or A4
- **Margins:** 1" all sides, 1.25" top
- **Logo:** Top left, 2-2.5" width
- **Header Border:** 2px Teal underline
- **Body Font:** 14px, 1.7 line height
- **Footer:** 10px, centered, Gray 600

### Offer Letter

- **Header:** Logo left, "OFFER OF EMPLOYMENT" right
- **Position Details Box:** Gray 50 background, 3px Teal border-left, 24px padding
- **Signature Block:** Two sections with acceptance area

### Contract/Agreement

- **Title Page:** Centered, Navy/Teal, 3px Teal separator
- **Party Info:** Two columns, Gray 50 background
- **Tables:** Navy header, alternating rows
- **Signature:** Two columns, 64px+ margin-top

### Presentations

- **Title Slide:** Navy gradient background, white text, Teal subtitle
- **Content Slides:** Logo top right, Navy titles, 3-5 bullets max
- **Fonts:** 24-28px titles, 14-16px body

---

## Visual Elements

### Shadows

```css
/* Light */
--shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);

/* Medium */
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);

/* Large */
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
```

### Border Radius

- **Subtle:** 4px (`--radius-sm`) - Buttons, inputs
- **Cards:** 8px (`--radius-md`)
- **Modals:** 12px (`--radius-lg`)
- **Pills:** 9999px (fully rounded)

### Borders

- **Standard:** 1px solid Gray 200
- **Emphasis:** 2px solid Teal
- **Strong:** 3px solid Navy

---

## Accessibility Quick Checks

- ✓ **Contrast:** 4.5:1 minimum (body), 3:1 minimum (large text 18pt+)
- ✓ **Focus States:** Never remove, 2-3px outline
- ✓ **Text Size:** 14px minimum for body
- ✓ **Touch Targets:** 44x44px minimum (web)
- ✓ **Color Meaning:** Never use color alone, add icons/text
- ✓ **Alt Text:** All images must have descriptive alt text
- ✓ **Semantic Structure:** Use proper headings, lists, etc.

---

## Audience-Specific Palettes

| Audience | Primary Colors | Accent Colors | Notes |
|----------|---------------|---------------|-------|
| **C-Suite/Board** | Navy + Teal + White | Minimal | Conservative, data-focused, board-ready |
| **Client Proposals** | Navy + Teal + Blue Light | Strategic | Innovation-focused, value-driven |
| **Partnership Agreements** | Navy + White | Minimal Teal | Professional, formal, trust-building |

---

## File Formats

| Document Type | Format | Notes |
|---------------|--------|-------|
| **Proposals** | PDF | 300 DPI, embedded fonts, Adobe RGB |
| **Contracts** | PDF + DOCX | PDF for signing, DOCX for editing |
| **Presentations** | PDF + PPTX | PDF for sharing, PPTX for editing |
| **Letterhead** | DOCX template | Editable, locked header/footer |
| **Email** | HTML + Plain Text | HTML formatting, plain text fallback |

---

## CSS Variables (Complete Reference)

```css
:root {
    /* Primary Brand Colors */
    --arcus-navy: #0A2540;
    --arcus-teal: #00BFB3;
    --arcus-slate: #425466;

    /* Neutral Colors */
    --arcus-charcoal: #1A1F36;
    --arcus-white: #FFFFFF;
    --arcus-gray-50: #FAFBFC;
    --arcus-gray-100: #F3F4F6;
    --arcus-gray-200: #E5E7EB;
    --arcus-gray-300: #D1D5DB;
    --arcus-gray-600: #6B7280;
    --arcus-gray-700: #425466;
    --arcus-gray-900: #1A1F36;

    /* Accent Colors */
    --arcus-blue-light: #0096FF;
    --arcus-green: #10B981;
    --arcus-amber: #F59E0B;
    --arcus-red: #EF4444;

    /* Typography */
    --font-primary: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
    --font-mono: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;

    /* Spacing (8pt grid) */
    --space-xs: 4px;
    --space-sm: 8px;
    --space-md: 16px;
    --space-lg: 24px;
    --space-xl: 32px;
    --space-2xl: 48px;
    --space-3xl: 64px;
    --space-4xl: 96px;

    /* Border Radius */
    --radius-sm: 4px;
    --radius-md: 8px;
    --radius-lg: 12px;

    /* Shadows */
    --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}
```

---

## Pre-Delivery Checklist

Before delivering any Arcus-branded material:

- [ ] Logo present and correctly sized
- [ ] Brand colors used accurately (Navy, Teal, Slate)
- [ ] Typography hierarchy followed (H1: 32-36px Navy, Body: 14px Charcoal)
- [ ] 8-point spacing grid applied
- [ ] Contrast requirements met (WCAG AA 4.5:1)
- [ ] Professional tone maintained (C-level appropriate)
- [ ] Proofread for errors
- [ ] Appropriate file format
- [ ] Clear space around logo respected
- [ ] No logo distortion or effects

---

**Version:** 1.0.0 | **Updated:** December 2025 | **Contact:** contact@arcusstudios.com
