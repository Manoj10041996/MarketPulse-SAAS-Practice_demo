# React / UI Rules

- Function components with hooks only. No class components.
- Everything typed. Props get an explicit `interface`/`type`; no `any`, no implicit props.
- One component, one responsibility. If a component is doing two things (e.g. fetching data and rendering a table), split it; extract a custom hook for reusable logic.
- API calls live in a services layer (`src/api/`), never inline `fetch`/`axios` calls inside components.
- Local state first. Use `useState`/`useReducer` for component-local state; reach for context (or a store) only when state is genuinely shared across distant components — don't prop-drill more than one or two levels.
- Co-locate related files. A component's styles and types live next to it, not in a distant shared folder, unless truly shared.
- Accessible by default. Semantic HTML elements, `alt` text on images, labels on form inputs — not an afterthought.
- Naming: `PascalCase` for components and their files, `camelCase` for functions, variables, and hooks (`useSomething`).
