# Accessible React + Tailwind dashboard demo

An original public portfolio demonstration, not client code. A small, responsive project explorer with keyboard-friendly filters, explicit status, and deterministic sorting.

## Highlights

- React + TypeScript + Tailwind CSS with a Vite build.
- Search and status filters with native form controls and accessible labels.
- Keyboard-accessible project links, visible focus rings and screen-reader result counts.
- Derived filtering rather than duplicated state; empty-result feedback.
- Separated pure filtering logic and unit tests.
- Fictional records; no external API, analytics, credentials or personal information.

## Run

Requires Node.js 20+.

```bash
cd showcase/react-accessible-ui
npm install
npm run dev
```

Then open the localhost URL printed by Vite.

```bash
npm run test
npm run build
```

## Scope

This is an intentionally compact UI engineering example, not a deployed product. Data is in memory, and the project links are examples. Real deployments would add authenticated API access, loading/error states, accessibility testing with assistive technology and production observability.

Tech: React · TypeScript · Tailwind CSS · Vite · Vitest
