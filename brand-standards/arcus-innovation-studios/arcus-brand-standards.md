# Arcus Innovation Studios Brand Standards

**For Design Director Skill Integration**

---

## Purpose

This document provides comprehensive brand standards for Arcus Innovation Studios. When the Design Director skill is used to create materials for Arcus, these standards take precedence and guide all visual design decisions.

## Integration with Design Director

When creating Arcus-branded materials:

1. **Read this document first** before applying design-director techniques
2. **Use Arcus brand palette** instead of exemplar colors (Stripe, Linear, etc.)
3. **Follow Arcus logo placement** rules
4. **Apply Arcus typography hierarchy** as specified
5. **Consider audience-specific** Arcus guidance (C-suite and board level)
6. **Validate against Arcus quality checklist**

The Design Director's elevation protocol still applies, but with Arcus brand elements as the foundation.

---

## Brand Identity

### Core Values Reflected in Design

Arcus Innovation Studios delivers systematic innovation evaluation for organizations addressing the 90% failure rate through data-driven assessment methodology. The brand reflects:

- **Precision** - Systematic, rigorous methodology
- **Credibility** - Trusted advisors at C-level and board level
- **Strategic Insight** - Board-ready decisions and evaluations
- **Professional Excellence** - Executive-grade quality standards

### Visual Personality

- **Systematic and precise** - Clean design with intentional structure
- **Credible and trustworthy** - Professional without being cold
- **Strategic and insightful** - Data-driven and analytical
- **Executive-focused** - Board-ready quality throughout

### Brand Positioning

Arcus delivers systematic innovation evaluation through:
- 6,000+ technologies evaluated across 13 years of data
- 30-day decision cycles reducing risk
- Board-ready assessments for strategic implementation
- C-level and board-level advisory services

---

## Color Palette

### Primary Colors (Use Most Frequently)

**Arcus Navy (Primary Brand Color)**
- HEX: `#0A2540`
- RGB: 10, 37, 64
- CSS Variable: `--arcus-navy`
- **Use for:** Headers, primary text, executive materials, document titles, formal communications
- **Design Director note:** This is the anchor color - use for credibility and professionalism
- **WCAG AA:** Passes with white text at 16.1:1 contrast ratio

**Arcus Teal (Innovation & Strategic Energy)**
- HEX: `#00BFB3`
- RGB: 0, 191, 179
- CSS Variable: `--arcus-teal`
- **Use for:** Accents, CTAs, data highlights, strategic emphasis, innovation-focused content
- **Design Director note:** Use sparingly for strategic energy and innovation signals
- **WCAG AA:** Passes with white text at 3.6:1 contrast ratio

**Arcus Slate (Secondary Text)**
- HEX: `#425466`
- RGB: 66, 84, 102
- CSS Variable: `--arcus-slate`
- **Use for:** Secondary text, subheadings, supporting content
- **Design Director note:** Provides hierarchy without overwhelming navy
- **WCAG AA:** Passes with white text at 8.2:1 contrast ratio

### Neutral Colors

**Charcoal (Body Text)**
- HEX: `#1A1F36`
- RGB: 26, 31, 54
- CSS Variable: `--arcus-charcoal`
- **Use for:** Body text, paragraphs, content

**White (Backgrounds)**
- HEX: `#FFFFFF`
- RGB: 255, 255, 255
- CSS Variable: `--arcus-white`
- **Use for:** Backgrounds, negative space, clarity

**Gray Scale (Supporting Elements)**
- Gray 50: `#FAFBFC` - Lightest backgrounds
- Gray 100: `#F3F4F6` - Subtle backgrounds, cards
- Gray 200: `#E5E7EB` - Borders, dividers
- Gray 300: `#D1D5DB` - Inactive elements
- Gray 600: `#6B7280` - Supporting text, captions
- Gray 700: `#425466` - Secondary text (same as Slate)
- Gray 900: `#1A1F36` - Primary text (same as Charcoal)

### Accent Colors (Use Sparingly)

**Success Green**
- HEX: `#10B981`
- RGB: 16, 185, 129
- CSS Variable: `--arcus-green`
- **Use for:** Positive metrics, success states, growth indicators

**Warning Amber**
- HEX: `#F59E0B`
- RGB: 245, 158, 11
- CSS Variable: `--arcus-amber`
- **Use for:** Cautions, attention items, warnings

**Alert Red**
- HEX: `#EF4444`
- RGB: 239, 68, 68
- CSS Variable: `--arcus-red`
- **Use for:** Risks, critical items, error states, urgent attention

**Blue Light (Data Visualization)**
- HEX: `#0096FF`
- RGB: 0, 150, 255
- CSS Variable: `--arcus-blue-light`
- **Use for:** Charts, data visualizations, alternative accent

### Color Application Principles

**Primary Usage:**
- Arcus Navy for all primary headers and formal document titles
- Teal for strategic accents, CTAs, and innovation-focused content
- Limit to 2-3 colors per document section for clarity
- Use neutrals for 80% of content, brand colors for 20%
- Ensure 4.5:1 contrast ratio minimum (WCAG AA compliance)

**Color Combinations:**

**Professional (Default):**
- Navy + Teal + White + Charcoal
- Most formal, board-ready materials

**Data-Focused:**
- Navy + Gray scale + Teal accents
- Analytics, dashboards, metrics

**Strategic Innovation:**
- Navy + Teal + Blue Light
- Innovation assessments, technology evaluations

---

## Typography

### Font System

**Primary Font Stack:**
```css
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
```
CSS Variable: `--font-primary`

**Monospace Font Stack (Data/Code):**
```css
font-family: 'SF Mono', Monaco, 'Cascadia Code', 'Roboto Mono', Consolas, 'Courier New', monospace;
```
CSS Variable: `--font-mono`

**Design Director note:** Use system fonts for reliability across platforms while maintaining executive-grade presentation.

### Typography Hierarchy

**Document Title (H1)**
- Size: 32-36px (print), 36-48px (digital)
- Weight: 700 (Bold)
- Color: Navy (`#0A2540`)
- Letter Spacing: -0.02em (tighter for large text)
- Line Height: 1.2
- **Use for:** Document titles, main headers, presentation titles

**Section Header (H2)**
- Size: 24-28px (print), 24-32px (digital)
- Weight: 600-700 (Semi-bold to Bold)
- Color: Navy (`#0A2540`)
- Letter Spacing: -0.01em
- Line Height: 1.3
- **Use for:** Section headers, major divisions, slide titles

**Subsection Header (H3)**
- Size: 18-20px
- Weight: 600 (Semi-bold)
- Color: Slate (`#425466`) or Navy
- Letter Spacing: 0
- Line Height: 1.4
- **Use for:** Subsections, protocols, frameworks

**Body Text**
- Size: 14px (standard), 15-16px (optimal readability)
- Weight: 400 (Regular)
- Color: Charcoal (`#1A1F36`)
- Line Height: 1.7 (generous for readability)
- Max Width: 50-75 characters per line
- **Use for:** Paragraphs, main content, body copy

**Caption / Small Text**
- Size: 12px
- Weight: 400 (Regular)
- Color: Gray 600 (`#6B7280`)
- Line Height: 1.5
- **Use for:** Footnotes, image captions, supporting information

**Legal / Footer**
- Size: 10px
- Weight: 400 (Regular)
- Color: Gray 600 (`#6B7280`)
- Line Height: 1.4
- **Use for:** Legal text, footer information, disclaimers

### Typography Best Practices

1. **Hierarchy is critical** - Use 2.5-3x size difference between H1 and body
2. **Line height matters** - 1.7 for body, 1.2-1.4 for headings
3. **Letter spacing** - Tighter for large text (-0.02em), normal for body
4. **Color for meaning** - Navy for authority, Slate for supporting, Charcoal for content
5. **Consistency** - Apply typography rules throughout entire document

---

## Logo & Visual Identity

### Logo Concept

The Arcus logo represents precision and systematic thinking. The stylized "A" with arc/infinity element symbolizes continuous evaluation and interconnected ecosystems.

### Logo Variations

**Primary Logo (Navy on White)**
- Standard usage for most materials
- Navy color (`#0A2540`)
- White or light backgrounds

**Reversed Logo (White on Navy)**
- Dark background applications
- White color (`#FFFFFF`)
- Navy or dark backgrounds

**Alternative Logo (Teal on White)**
- Digital applications only
- Teal color (`#00BFB3`)
- Use for digital-first materials, web interfaces

**Text-Based Lockup (For Templates)**
- **Primary text:** "ARCUS" in Navy, bold
- **Tagline:** "Innovation Studios" in Teal, regular weight
- Use in letterhead headers, email signatures, and text-only contexts
- Maintains brand identity when graphical logo cannot be used
- Font: System sans-serif, "ARCUS" 24-32px, tagline 14-16px

### Logo Usage Guidelines

**Minimum Size Requirements:**
- Print Materials: 0.75 inches (19mm) width minimum
- Digital Materials: 120px width minimum
- Presentations: 1.5 inches (38mm) width recommended
- Letterhead: 2-2.5 inches (50-64mm) width
- Business Cards: 1 inch (25mm) width minimum

**Clear Space:**
- Maintain minimum clear space equal to height of letter "A" on all sides
- No text, graphics, or other elements within clear space zone
- Ensures logo prominence and readability

**Logo Placement:**

| Document Type | Logo Placement | Size |
|---------------|---------------|------|
| **Letterhead** | Top left | 2-2.5" width |
| **Presentations (title slide)** | Centered | 2-3" width |
| **Presentations (content slides)** | Top right corner | 1-1.5" width |
| **Reports** | Top left or center | 2-2.5" width |
| **Proposals** | Cover - top left | 2-3" width |
| **Contracts** | Centered header | 2-2.5" width |
| **Business Cards** | Front - left or centered | 1-1.5" width |

### Logo Don'ts (Never)

- ✗ Stretch or distort logo proportions
- ✗ Change logo colors (except approved variations)
- ✗ Add effects (shadows, glows, gradients, outlines)
- ✗ Rotate or skew logo
- ✗ Place on busy backgrounds without white/navy container
- ✗ Use below minimum size requirements
- ✗ Violate clear space requirements

---

## Spacing System

### 8-Point Grid

All spacing follows an 8-point grid system for consistent, professional layouts:

- **4px (XS):** `--space-xs` - Tight spacing, minor adjustments
- **8px (SM):** `--space-sm` - List items, close relationships
- **16px (MD):** `--space-md` - Paragraph spacing, standard gaps
- **24px (LG):** `--space-lg` - Section spacing, cards
- **32px (XL):** `--space-xl` - Major sections, page elements
- **48px (2XL):** `--space-2xl` - Section margins, major divisions
- **64px (3XL):** `--space-3xl` - Page sections, large spacing
- **96px (4XL):** `--space-4xl` - Page margins, document edges

### Spacing Application

| Context | Recommended Spacing | Usage |
|---------|-------------------|-------|
| **Between paragraphs** | 16px (MD) | Standard body text spacing |
| **Section margins** | 48-64px (2XL-3XL) | Major content sections |
| **List item spacing** | 8px (SM) | Vertical rhythm in lists |
| **Card padding** | 24-32px (LG-XL) | Content cards, callouts |
| **Page margins** | 48-96px (2XL-4XL) | Document edges (print/digital) |
| **Header spacing** | 32-48px (XL-2XL) | After headers, before content |

---

## Document Templates

### Letterhead Standards

**Page Specifications:**
- Page Size: 8.5" × 11" (US Letter) or A4
- Margins: 1" (25mm) all sides, 1.25" (32mm) top
- Logo: Top left, 2-2.5" width
- Header Border: 2px Teal (`#00BFB3`) underline
- Body Font: 14px system sans-serif, 1.7 line height
- Footer: 10px, centered, Gray 600

**Header Layout:**
- Left: Logo (ARCUS + Innovation Studios tagline in Teal)
- Right: Contact information (Seattle • São Paulo • Cotonou, email, website)
- Border: 2px Teal horizontal line

**Footer:**
- Centered: "Arcus Innovation Studios | Systematic Innovation Evaluation | arcusstudios.com"
- Font: 10px, Gray 600

### Offer Letter / Employment Agreement

**Header:**
- Logo: Left side
- "OFFER OF EMPLOYMENT" / "CONFIDENTIAL": Right side, Navy, bold

**Content Structure:**
- Date: Navy, 14px
- Recipient address
- Salutation
- Body text: 14px, 1.7 line height
- **Position Details Box:**
  - Background: Gray 50 (`#F3F4F6`)
  - Border-left: 3px solid Teal
  - Padding: 24px
  - Border-radius: 8px
- Signature block with acceptance section

### Contract / Service Agreement

**Title Page:**
- Centered layout
- Logo: "ARCUS" (32px, bold, Navy) + "Innovation Studios" (16px, Teal)
- Document Type: 20px, semi-bold, Slate
- 3px Teal border separator

**Content Structure:**
- **Party Information Boxes:**
  - Two-column layout (Provider / Client in separate boxes)
  - Each box: Gray 50 (`#F3F4F6`) background
  - Padding: 20px
  - Border-radius: 8px

**Section Headers:**
- 18px, semi-bold, Navy
- Numbered (1. SCOPE OF SERVICES)

**Tables:**
- Header: Navy background, white text
- Rows: Alternating row colors with Gray 50
- Padding: 12px
- Border-bottom: 1px Gray 200

**Signature Block:**
- Two columns (Provider / Client)
- Border-top: 2px Gray 300
- Generous spacing (64px+ margin-top)

### Presentation Guidelines

**Title Slide:**
- Background: Navy gradient (Navy to Charcoal, 135deg)
- Title: 48px, bold, white
- Subtitle: 20px, Teal
- Date/Client: 14px, white with opacity

**Content Slides:**
- Logo: Top right, 1-1.5" width
- Title: 24-28px, Navy, bold
- Body: 14-16px, Charcoal
- Maximum 3-5 bullet points per slide

**Design Principles:**
- Clean hierarchy
- Generous white space
- Professional data visualization
- Consistent alignment and spacing

---

## Visual Elements

### Shadows (Use Sparingly)

**Light Shadow:**
```css
box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
```
Variable: `--shadow-sm`
Use: Subtle elevation, cards

**Medium Shadow:**
```css
box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
```
Variable: `--shadow-md`
Use: Elevated cards, dropdowns

**Large Shadow:**
```css
box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
```
Variable: `--shadow-lg`
Use: Modals, important elements

### Border Radius

- **Subtle (Buttons/Inputs):** 4px (`--radius-sm`)
- **Cards:** 8px (`--radius-md`)
- **Modals:** 12px (`--radius-lg`)
- **Pills:** 9999px (fully rounded)

### Borders

- **Standard:** 1px solid Gray 200 (`#E5E7EB`)
- **Emphasis:** 2px solid Teal (`#00BFB3`)
- **Strong:** 3px solid Navy (`#0A2540`)

---

## Best Practices

### Quality Standards

**Always:**
- ✓ Use exact hex codes for brand colors
- ✓ Maintain 8-point grid spacing system
- ✓ Include logo on all external documents
- ✓ Ensure WCAG AA contrast compliance (4.5:1 minimum)
- ✓ Follow typography hierarchy consistently
- ✓ Use professional tone appropriate for C-level audience
- ✓ Proofread for grammar, spelling, accuracy
- ✓ Apply brand elements systematically throughout

**Avoid:**
- ⚠ Mixing too many colors (limit to 2-3 per section)
- ⚠ Using decorative fonts or effects
- ⚠ Cluttered layouts without white space
- ⚠ Low-resolution images or distorted logos
- ⚠ Inconsistent spacing or alignment
- ⚠ Overly casual language in formal documents

**Never:**
- ✗ Alter logo colors or proportions
- ✗ Use colors outside approved palette
- ✗ Apply effects to logo (shadows, gradients, outlines)
- ✗ Place logo on busy backgrounds without container
- ✗ Use font sizes below minimums
- ✗ Ignore accessibility standards
- ✗ Mix competing visual styles

### File Formats & Delivery

| Document Type | Format | Notes |
|---------------|--------|-------|
| **Proposals** | PDF (print-quality) | 300 DPI, embedded fonts, Adobe RGB |
| **Contracts** | PDF + DOCX | PDF for signing, DOCX for editing |
| **Presentations** | PDF + PPTX | PDF for sharing, PPTX for editing |
| **Letterhead** | DOCX template | Editable with locked header/footer |
| **Email Communications** | HTML + Plain Text | HTML formatting, plain text fallback |

---

## Accessibility Requirements

**WCAG AA Compliance (Mandatory):**
- Color contrast 4.5:1 minimum for body text
- Color contrast 3:1 minimum for large text (18pt+)
- Color never sole indicator (include icons/text)
- Focus states never removed (2-3px outline)
- Touch targets 44x44px minimum for web
- Alt text for all images
- Semantic HTML structure

**Text Readability:**
- Body text 14px minimum
- Line height 1.5-1.7 for body text
- Max line length 50-75 characters
- Sufficient contrast for all text

---

## Audience-Specific Guidance

### C-Suite & Board Materials

**Color Palette:**
- Primary: Navy + Teal + White
- Minimal accent colors
- Conservative, data-focused

**Typography:**
- Clean hierarchy
- Generous spacing
- Professional tone throughout

**Content:**
- Executive summaries upfront
- Data-driven insights
- Strategic recommendations
- Board-ready quality

### Client Proposals

**Color Palette:**
- Navy + Teal + Blue Light
- Strategic energy
- Innovation-focused

**Typography:**
- Clear value proposition
- Benefit-oriented headers
- Professional credibility

**Content:**
- Methodology highlights
- Case studies/proof points
- Clear deliverables
- Pricing transparency

### Partnership Agreements

**Color Palette:**
- Navy + White + minimal Teal
- Professional, formal
- Trust-building

**Typography:**
- Legal clarity
- Structured hierarchy
- Scannable sections

**Content:**
- Clear terms
- Mutual benefits
- Compliance focus
- Professional credibility

---

## CSS Variables Reference

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

    /* Spacing Scale (8pt grid) */
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

## Version & Maintenance

**Version:** 1.0.0
**Last Updated:** December 2025
**Maintained By:** Arcus Innovation Studios
**Contact:** contact@arcusstudios.com

---

**Design Director Integration Note:**

When this brand module is active, Design Director's elevation protocol applies with Arcus brand elements as the foundation. The 6-phase protocol remains the same, but:

- **Phase 3 (Technique Selection):** Replace exemplar colors with Arcus palette
- **Phase 4 (Application):** Apply Arcus typography, spacing, and visual elements
- **Phase 5 (Validation):** Include Arcus brand compliance checks

The result should be professionally elevated AND perfectly on-brand for Arcus Innovation Studios.
