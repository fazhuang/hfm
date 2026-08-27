# HFM Agent Instructions

## Scope

These rules govern UI component discovery and reuse for the HFM project.
Follow the project's existing framework, design tokens, accessibility patterns,
and component conventions. Do not migrate the project to React or add a new UI
framework merely to use one of the resources below.

## Selection order

1. Reuse an existing HFM component or utility when it already solves the need.
2. Use shadcn/ui as the conceptual foundation for standard controls and design-system patterns.
3. Use Beautiful UI for AI-native surfaces: chat, streaming output, thinking states,
   tool calls, approvals, agent tasks, context/source cards, diffs, and workflows.
4. Use beUI for polished React/Next.js motion components when the project is already
   compatible with React, Motion, and Tailwind.
5. Use Rare UI only for distinctive, bounded visual moments such as landing-page
   heroes, branded empty states, or portfolio-style interactions.
6. Use Transitions.dev for small, isolated CSS or React motion effects such as
   modal, toast, tab, loading, success, error, shimmer, and number transitions.

Use the smallest source that solves the requirement. Do not install multiple
implementations of the same component or import a complete UI library for one effect.

## Framework compatibility

- Inspect the current project framework before selecting a resource.
- React-only components from Beautiful UI, beUI, and Rare UI must not be added to
  a Vue or non-React surface without an explicit implementation decision.
- Prefer the CSS version of Transitions.dev when it avoids a framework dependency.
- Adapt visual ideas manually only when the resulting code follows existing HFM
  patterns and preserves the same interaction and accessibility behavior.

## Installation and review workflow

Before adding third-party UI code:

1. Identify the exact component and the user-facing requirement it satisfies.
2. Search the repository for an existing equivalent.
3. Inspect the source, dependencies, registry metadata, and license.
4. Prefer a pinned or reviewed source revision when the registry supports it.
5. Preview the change with `shadcn view`, `--dry-run`, or `--diff` where applicable.
6. Add only the required component and its required dependencies.
7. Run the project's typecheck, lint, build, and relevant tests.

Never execute an install command copied from an unreviewed registry blindly.
Treat registry components as third-party source code, not as trusted packages.

## shadcn registries

Use the shadcn CLI only when the target project is configured for it. For a
third-party component, inspect before installing:

```bash
npx shadcn view <registry>/<component>
npx shadcn add <registry>/<component> --dry-run
npx shadcn add <registry>/<component> --diff
```

Do not add registry configuration unless the project actually needs that registry.

## Motion and accessibility

- Motion must communicate state or support orientation; it must not be the only
  indication of success, failure, progress, or availability.
- Preserve keyboard access, focus management, Escape handling, usable touch targets,
  and semantic HTML.
- Respect `prefers-reduced-motion`; provide the same functional result without
  movement, blur, scale, or particle effects.
- Check layout, performance, and interaction behavior on mobile as well as desktop.

## Visual consistency

- Reuse HFM tokens for color, typography, spacing, radius, shadow, and focus states.
- Do not introduce direct hex colors, arbitrary inline styles, or a second design
  language when an HFM token or utility already exists.
- Prefer one coherent motion scale across a page; do not mix unrelated spring,
  easing, and duration conventions without a reason.

## Output expectations

When selecting a resource, briefly state:

- which existing component or resource was selected;
- why it fits the requirement;
- what dependencies and license apply;
- what verification was run.

If no listed resource fits, say so and implement the smallest native solution.
