# Arcus Innovation Studios - Design Director Integration Guide

**How to apply Arcus brand standards within the Design Director workflow**

---

## Overview

This guide explains how the Design Director's 6-phase elevation protocol integrates with Arcus Innovation Studios brand standards. When creating Arcus-branded materials, the Design Director maintains its systematic approach while ensuring perfect brand compliance.

---

## Integration Strategy

**Core Principle:** Design Director provides the elevation methodology (the "how"), while Arcus brand standards provide the visual identity (the "what").

**Workflow Integration:**
1. Design Director's 6-phase protocol remains unchanged
2. Arcus brand elements replace generic exemplars in Phase 3-4
3. Additional brand compliance checks added in Phase 5
4. Brand-appropriate delivery in Phase 6

---

## Phase-by-Phase Integration

### Phase 1: Functional Foundation

**Standard Design Director process applies:**
- Ensure content accuracy and completeness
- Establish logical hierarchy
- Verify functionality

**Arcus-specific additions:**
- Identify document type (proposal, contract, presentation, letterhead, etc.)
- Determine audience (C-suite, board, client, partner)
- Note any Arcus-specific requirements (logo placement, specific templates)

**Quality Gate:** Content works correctly + audience identified

---

### Phase 2: Design Interrogation

**Standard Design Director interrogation applies, plus:**

**Arcus-specific interrogation:**
- Is this material for Arcus or an Arcus client?
- What audience level? (Board/C-suite, client proposal, partnership agreement)
- Which document template applies? (Letterhead, offer letter, contract, presentation)
- Should logo be included? Where and what size?
- What color palette is appropriate for this audience?

**Interrogation Checklist:**
- [ ] Audience identified (C-suite/board/client/partner)
- [ ] Document type determined (proposal/contract/presentation/report)
- [ ] Logo requirements identified (placement, size, variation)
- [ ] Color palette selected (professional/data-focused/strategic innovation)
- [ ] Typography needs assessed (formal vs. modern)

**Quality Gate:** All design weaknesses identified + Arcus brand requirements clear

---

### Phase 3: Technique Selection

**Replace exemplar references with Arcus brand:**

**Typography Techniques:**

Instead of:
- "Stripe-style typography with Inter"
- "Linear's bold hierarchy"

Use:
- **Arcus system fonts** (Apple system stack)
- **Arcus hierarchy**: H1 32-36px Navy, H2 24-28px Navy, Body 14px Charcoal
- **Arcus line heights**: 1.7 for body, 1.2 for headers
- **Arcus letter spacing**: -0.02em for large text

**Color Techniques:**

Instead of:
- "Stripe's #0A2540 blue"
- "Linear's #5E6AD2 purple"

Use:
- **Arcus Navy** (`#0A2540`) for headers and authority
- **Arcus Teal** (`#00BFB3`) for accents and CTAs
- **Arcus Slate** (`#425466`) for secondary text
- **Arcus Charcoal** (`#1A1F36`) for body text
- **Arcus Gray scale** for backgrounds and dividers

**Layout Techniques:**

- **8-point grid**: 8, 16, 24, 32, 48, 64, 96px (Arcus standard)
- **Spacing scale**: Use Arcus CSS variables (--space-sm through --space-4xl)
- **White space**: Generous, professional, C-level appropriate

**Visual Element Techniques:**

- **Shadows**: Arcus shadow variables (--shadow-sm, --shadow-md, --shadow-lg)
- **Border radius**: Arcus standards (4px subtle, 8px cards, 12px modals)
- **Borders**: 1px Gray 200 standard, 2px Teal emphasis, 3px Navy strong

**Selected Techniques (2-3 max):**
1. **Arcus typography hierarchy** (Navy headers, Charcoal body, proper scale)
2. **Arcus color application** (Navy + Teal + Gray, strategic use)
3. **8-point spacing grid** (consistent, professional spacing)

**Quality Gate:** 2-3 Arcus-specific techniques selected

---

### Phase 4: Systematic Application

**Apply Arcus techniques consistently throughout:**

**Typography Application:**
```
Document titles → 32-36px, 700 weight, Navy (#0A2540), -0.02em tracking
Section headers → 24-28px, 600-700 weight, Navy (#0A2540)
Subsections → 18-20px, 600 weight, Slate (#425466)
Body text → 14px, 400 weight, Charcoal (#1A1F36), 1.7 line height
Captions → 12px, 400 weight, Gray 600 (#6B7280)
```

**Color Application:**
```
Primary headers → Navy (#0A2540)
Accents/CTAs → Teal (#00BFB3)
Secondary text → Slate (#425466)
Body text → Charcoal (#1A1F36)
Backgrounds → White (#FFFFFF) or Gray 50/100
Borders → Gray 200 (#E5E7EB) standard, Teal emphasis
Success states → Green (#10B981)
Warnings → Amber (#F59E0B)
Errors → Red (#EF4444)
```

**Spacing Application:**
```
Paragraph gaps → 16px (--space-md)
Section margins → 48-64px (--space-2xl to --space-3xl)
List items → 8px (--space-sm)
Card padding → 24-32px (--space-lg to --space-xl)
Page margins → 48-96px (--space-2xl to --space-4xl)
```

**Logo Application:**
```
Letterhead → Top left, 2-2.5" width
Presentations (title) → Centered, 2-3" width
Presentations (slides) → Top right, 1-1.5" width
Reports → Top left or center, 2-2.5" width
Clear space → Height of "A" on all sides
```

**Document Template Application:**

For each document type, follow Arcus templates:
- **Letterhead**: 1" margins (1.25" top), 2px Teal header border, 10px footer
- **Offer Letter**: Position details box (Gray 50 bg, 3px Teal border-left)
- **Contract**: Centered title, two-column party info, Navy table headers
- **Presentation**: Navy gradient title slide, logo top-right on content slides

**Quality Gate:** Arcus techniques applied consistently to ALL elements

---

### Phase 5: Quality Validation

**Standard Design Director validation, plus Arcus brand compliance:**

**Brand Compliance Checks:**

**Color Compliance:**
- [ ] All colors from Arcus palette (no generic blues/grays)
- [ ] Navy used for all primary headers
- [ ] Teal used strategically (not overused)
- [ ] Contrast meets WCAG AA (4.5:1 minimum)
- [ ] No more than 3 colors per section

**Typography Compliance:**
- [ ] System font stack used
- [ ] Hierarchy matches Arcus standards (32-36px titles, 24-28px headers, 14px body)
- [ ] Line heights correct (1.7 body, 1.2-1.4 headers)
- [ ] Letter spacing applied (-0.02em large text)
- [ ] Color appropriate for text type (Navy headers, Charcoal body)

**Logo Compliance:**
- [ ] Logo included (if external document)
- [ ] Logo placement correct for document type
- [ ] Logo size meets minimums (0.75" print, 120px digital)
- [ ] Clear space maintained (height of "A")
- [ ] No distortion, effects, or color changes
- [ ] Correct variation used (Navy on White, White on Navy)

**Spacing Compliance:**
- [ ] 8-point grid followed
- [ ] Spacing values from Arcus scale
- [ ] Generous white space for C-level audience
- [ ] Consistent spacing throughout
- [ ] Page margins appropriate (1" standard, 1.25" top for letterhead)

**Template Compliance:**
- [ ] Correct template structure for document type
- [ ] Header/footer formatted correctly
- [ ] Signature blocks positioned properly (if applicable)
- [ ] Professional tone throughout

**Accessibility Compliance:**
- [ ] WCAG AA contrast (4.5:1 body, 3:1 large text)
- [ ] Text size minimums (14px body)
- [ ] Focus states present (web)
- [ ] Color not sole indicator
- [ ] Alt text on images

**Professional Polish:**
- [ ] Would this pass Arcus C-level standards?
- [ ] Board-ready quality?
- [ ] Hand-crafted appearance (not template-based)?
- [ ] Consistent with other Arcus materials?

**Quality Gate:** All brand compliance checks pass + Design Director quality standards met

---

### Phase 6: Delivery Preparation

**Standard delivery (process NOT shown):**
- Deliver polished file directly
- Brief description highlighting key features
- Professional tone appropriate for Arcus
- No mention of design process

**Extended delivery (if requested):**
- Deliver polished file
- Note key brand applications:
  - "Applied Arcus Navy and Teal palette for executive credibility"
  - "Followed Arcus 8-point spacing grid for professional polish"
  - "Integrated Arcus letterhead template with logo placement"
- Reference Arcus brand standards adherence
- Keep explanation brief and specific

**File Format:**
Based on document type (see Arcus brand standards):
- Proposals: PDF (300 DPI, embedded fonts, Adobe RGB)
- Contracts: PDF + DOCX
- Presentations: PDF + PPTX
- Letterhead: DOCX template

**Quality Gate:** Delivery appropriate for Arcus professional standards

---

## Common Scenarios

### Scenario 1: Board Presentation

**Audience:** C-suite and board members
**Requirements:** Conservative, data-focused, board-ready quality

**Phase 1:** Ensure all data accurate, slides logical
**Phase 2:** Interrogate for clarity, hierarchy, credibility
**Phase 3:** Select Arcus Navy + Teal palette, Arcus typography, generous spacing
**Phase 4:** Apply to all slides:
- Title slide: Navy gradient background, white 48px title, Teal 20px subtitle
- Content slides: Logo top right (1.5"), Navy 28px headers, Charcoal 16px body
- Data charts: Navy primary, Teal accents, clean visualization
- Spacing: 48px section margins, 16px bullet gaps
**Phase 5:** Validate all compliance checks, ensure board-ready quality
**Phase 6:** Deliver PDF + PPTX with professional description

### Scenario 2: Client Proposal

**Audience:** Prospective client (C-suite level)
**Requirements:** Strategic, innovation-focused, value-driven

**Phase 1:** Ensure value proposition clear, deliverables outlined
**Phase 2:** Interrogate for persuasiveness, credibility, clarity
**Phase 3:** Select Arcus Navy + Teal + Blue Light palette, strong hierarchy, clear CTAs
**Phase 4:** Apply throughout:
- Cover: Logo top left (2.5"), Navy title (36px), Teal subtitle
- Headers: Navy 24px, Teal for key benefits
- Body: Charcoal 14px, generous line height (1.7)
- CTAs: Teal backgrounds, white text
- Data/metrics: Blue Light charts, Navy annotations
**Phase 5:** Validate brand compliance, ensure proposal-ready quality
**Phase 6:** Deliver PDF with description emphasizing value proposition

### Scenario 3: Offer Letter

**Audience:** Candidate for employment
**Requirements:** Professional, formal, credible, welcoming

**Phase 1:** Ensure all offer details accurate and complete
**Phase 2:** Interrogate for clarity, formality, professionalism
**Phase 3:** Select Arcus letterhead template, Navy + Teal palette, formal hierarchy
**Phase 4:** Apply Arcus letterhead template:
- Header: Logo left (2"), contact info right, 2px Teal border
- Title: "OFFER OF EMPLOYMENT" - Navy, bold, right-aligned
- Body: 14px Charcoal, 1.7 line height
- Position details: Gray 50 background box, 3px Teal border-left, 24px padding
- Signature block: Professional spacing
- Footer: 10px Gray 600, centered
**Phase 5:** Validate template compliance, professional quality
**Phase 6:** Deliver DOCX template for signing

### Scenario 4: Service Agreement Contract

**Audience:** Client organization (legal review + C-suite)
**Requirements:** Professional, formal, scannable, trust-building

**Phase 1:** Ensure all terms clear, sections logical
**Phase 2:** Interrogate for legal clarity, scannability, professionalism
**Phase 3:** Select Arcus contract template, Navy + White palette, structured hierarchy
**Phase 4:** Apply Arcus contract template:
- Title page: Centered layout, "ARCUS" 32px Navy, "Innovation Studios" 16px Teal
- Document type: 20px semi-bold Slate
- Party info: Two columns, Gray 50 background, 8px border-radius
- Section headers: 18px Navy, numbered (1. SCOPE OF SERVICES)
- Tables: Navy headers (white text), Gray 50 alternating rows
- Signature block: Two columns, 64px margin-top, 2px Gray 300 border-top
**Phase 5:** Validate contract template compliance, legal professionalism
**Phase 6:** Deliver PDF + DOCX

---

## Troubleshooting

### Issue: Colors don't look "Arcus"

**Solution:**
- Verify exact hex codes used (#0A2540 Navy, #00BFB3 Teal, #425466 Slate)
- Ensure Navy is primary header color (not generic blue)
- Check Teal is used for accents only (not overused)
- Confirm neutrals are from Arcus gray scale

### Issue: Typography feels generic

**Solution:**
- Verify hierarchy: 32-36px titles (2.5-3x body size)
- Check weights: 700 for titles, 600 for headers, 400 for body
- Ensure line heights: 1.7 for body (generous), 1.2 for headers
- Apply letter spacing: -0.02em for large text
- Use Navy for headers (not black)

### Issue: Logo placement incorrect

**Solution:**
- Check document type requirements in quick reference
- Verify size meets minimums (0.75" print, 120px digital)
- Ensure clear space (height of "A" on all sides)
- Use correct variation (Navy on White, White on Navy)
- No effects, distortion, or color changes

### Issue: Spacing feels cramped

**Solution:**
- Apply 8-point grid strictly
- Use generous spacing for C-level audience (48-64px section margins)
- Ensure 16px paragraph gaps minimum
- Check page margins (1" standard, 1.25" top for letterhead)
- Add breathing room around key elements

### Issue: Doesn't feel "board-ready"

**Solution:**
- Increase formality: Navy + Teal + White only (minimal accents)
- Ensure conservative tone throughout
- Add more white space (C-suite preference)
- Verify professional quality: no template appearance
- Check all compliance items in Phase 5 validation

---

## Quick Decision Trees

### Which Color Palette?

```
Is audience C-suite/Board?
├─ Yes → Navy + Teal + White (minimal accents)
└─ No → Is it innovation-focused?
    ├─ Yes → Navy + Teal + Blue Light (strategic)
    └─ No → Navy + Gray scale + Teal accents (data-focused)
```

### Which Logo Size?

```
What document type?
├─ Letterhead → 2-2.5" width
├─ Presentation title → 2-3" width (centered)
├─ Presentation slides → 1-1.5" width (top right)
├─ Report → 2-2.5" width
├─ Proposal cover → 2-3" width
├─ Contract → 2-2.5" width (centered)
└─ Business card → 1-1.5" width
```

### Which Typography Size?

```
What's the content type?
├─ Document title → 32-36px (Navy, 700 weight)
├─ Section header → 24-28px (Navy, 600-700 weight)
├─ Subsection → 18-20px (Slate or Navy, 600 weight)
├─ Body text → 14px (Charcoal, 400 weight, 1.7 line height)
├─ Caption → 12px (Gray 600, 400 weight)
└─ Legal/Footer → 10px (Gray 600, 400 weight)
```

---

## Best Practices Summary

**Always:**
1. Start with Arcus brand standards (this guide)
2. Apply Design Director elevation protocol with Arcus elements
3. Use exact Arcus hex codes (never approximations)
4. Follow 8-point spacing grid
5. Ensure WCAG AA compliance
6. Validate against Arcus quality checklist
7. Deliver in appropriate file format

**Never:**
1. Use generic colors (Stripe/Linear palettes) instead of Arcus
2. Alter logo colors, proportions, or add effects
3. Skip clear space around logo
4. Use fonts outside Arcus system stack
5. Ignore 8-point spacing grid
6. Compromise accessibility standards
7. Deliver without brand compliance validation

---

## Resources

**Primary Reference:**
- [Arcus Brand Standards](arcus-brand-standards.md) - Complete specification

**Quick Lookups:**
- [Arcus Quick Reference](arcus-quick-reference.md) - Fast tables and specs

**Quality Assurance:**
- [Arcus Quality Checklist](arcus-quality-checklist.md) - Pre-delivery validation

**Design Director Core:**
- [Design Director SKILL.md](../../SKILL.md) - Main skill documentation
- [Elevation Protocol](../../references/elevation-protocol.md) - 6-phase process

---

**Version:** 1.0.0
**Updated:** December 2025
**Contact:** contact@arcusstudios.com
