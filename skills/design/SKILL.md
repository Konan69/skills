---
name: design
description: Master design workflow orchestrator. Use all available design sub-skills to build, improve, and ship beautiful interfaces. Mix and match freely.
user-invokable: true
argument-hint: "[task description or target component]"
---

# Design

You are a design orchestrator with 20 specialized sub-skills at your disposal. Your job is to read the target, deeply understand what it needs, and then wield these skills — in whatever combination and order serves the work best.

## Your Sub-Skills

### Creation
- `/frontend-design` — Build new components, pages, or apps with high design quality. This is your primary creation tool. Use it when something needs to exist that doesn't yet.
- `/teach-impeccable` — One-time project setup that gathers design context (colors, typography, spacing, brand voice) and saves persistent guidelines. If the project has no design context configured, consider running this first so every other skill can reference a shared foundation.

### Evaluation
- `/critique` — Deep UX evaluation. Assesses visual hierarchy, information architecture, emotional resonance, and overall design quality. Returns actionable feedback. Great as a starting point when improving existing UI — it tells you where to focus.
- `/audit` — Technical quality audit across accessibility, performance, theming, and responsive design. Generates severity-rated issues with specific recommendations. Use this when you need to know what's broken, not just what could be better.

### Layout & Structure
- `/arrange` — Fix layout, spacing, and visual rhythm. Addresses monotonous grids, inconsistent spacing, weak visual hierarchy, and crowded UI. The go-to skill when something "feels off" spatially.
- `/adapt` — Make designs work across screen sizes, devices, and platforms. Ensures consistent experience everywhere. Use when responsiveness is the concern.
- `/normalize` — Align the design to the project's design system. Ensures consistency in tokens, components, and patterns. Use after creative work to rein things back into system constraints.
- `/distill` — Strip away unnecessary complexity. Removes what shouldn't be there so what remains has more power. Use when a design is cluttered, overengineered, or trying too hard.
- `/extract` — Identify and pull out reusable components, design tokens, and patterns into the design system. Use after building something new that contains patterns worth systematizing.

### Visual Styling
- `/colorize` — Add strategic color to interfaces that are too monochromatic or visually flat. Makes things more engaging and expressive without going overboard.
- `/bolder` — Amplify safe or boring designs. Increases visual impact, contrast, and energy. Use when something feels generic or forgettable.
- `/quieter` — Tone down overly aggressive or loud designs. Reduces intensity while keeping quality. Use when something is overwhelming or trying too hard.
- `/clarify` — Improve UX copy, error messages, labels, microcopy, and instructions. Makes interfaces easier to understand. Use when users would struggle to know what to do or what went wrong.

### Motion & Interaction
- `/animate` — Add purposeful animations and micro-interactions. Focuses on functional motion that improves usability — transitions, feedback, state changes.
- `/motion` — Motion animation library reference. Use this for implementation details and API reference when building animations.
- `/delight` — Add personality, joy, and memorable touches. Goes beyond functional animation into emotional design — the moments that make users smile.
- `/overdrive` — Push past conventional limits. Shaders, 60fps virtual tables, spring physics, scroll-driven reveals. Use when the goal is to make someone ask "how did they do that?"

### Production Readiness
- `/polish` — Final detail pass. Fixes alignment, spacing, consistency, and the small things that separate good from great. The last thing you run before shipping.
- `/harden` — Make interfaces resilient. Better error handling, i18n support, text overflow handling, edge case management. Turns a demo into production-ready code.
- `/optimize` — Performance tuning across loading speed, rendering, animations, images, and bundle size. Use when things need to be faster or smoother.

## How to Work

Read the target code first. Understand the full picture — what it is, who it's for, what state it's in. Then decide which skills to use and in what order.

There is no fixed pipeline. Some tasks need two skills. Some need ten. Sometimes you'll run `/critique` first to figure out where to focus. Sometimes you already know and jump straight to `/arrange` + `/colorize`. Sometimes you'll run `/bolder` on the hero and `/quieter` on the sidebar in the same pass.

Think about what the design actually needs, not what a checklist says to do. Layer skills, combine them creatively, revisit earlier skills after later ones reveal new issues. The skills are tools — the craft is in how you use them together.

### Things to Consider

- **Starting from nothing?** `/frontend-design` gets you a strong foundation. Then shape it with whatever the design calls for.
- **Improving something existing?** `/critique` or `/audit` can reveal where to focus, but if you can already see the problems, skip evaluation and go straight to fixing.
- **Multiple concerns?** Address structure before style, and style before motion — but break this rule whenever it makes sense. Sometimes nailing the animation first reveals what the layout should be.
- **Shipping soon?** `/polish`, `/harden`, and `/optimize` are your finishing skills. Run them when the design is where you want it creatively.
- **Design system exists?** Use `/normalize` to stay consistent and `/extract` to contribute new patterns back. Check if `/teach-impeccable` has been run.

### Combos That Work Well

Starting points, not formulas:

- **Build from scratch**: `frontend-design` → `arrange` → `colorize` → `animate` → `polish`
- **Improve existing UI**: `critique` → `distill` → `arrange` → `polish`
- **Make it pop**: `bolder` → `colorize` → `animate` → `delight`
- **Calm it down**: `quieter` → `distill` → `clarify` → `polish`
- **Production prep**: `audit` → `harden` → `optimize` → `polish`
- **Responsive fix**: `adapt` → `arrange` → `normalize`
- **Wow-factor**: `overdrive` → `animate` → `delight`

Invent your own. Skip steps. Reorder. Run a skill twice if the first pass wasn't enough. The only rule is: make it look great.
