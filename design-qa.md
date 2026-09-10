# HFM Homepage Design QA

- source visual truth: `/Users/likeming/.codex/generated_images/01a07303-9dfd-7142-84dd-91a77e43892b/exec-286addc0-5cf2-41e1-b8df-1df3545226e2.png`
- implementation: `http://localhost:5199/`
- implementation screenshot: browser-rendered Codex In-app Browser capture in this turn (`1280 x 720`, CSS viewport `1280 x 720`, device scale factor 1)
- source pixels: `1536 x 1024`; implementation pixels: `1280 x 720`; comparison normalized by matching the responsive desktop composition, with no device frame
- state: light theme, homepage at `/`, no search query

## Comparison

Full-view comparison confirms the selected direction: paper canvas, editorial serif hierarchy, documentary book/heritage imagery, single dominant search action, and four knowledge-world entry points directly below the hero. Focused comparison covered the hero title, search form, image crops, navigation order, and four-domain entry band.

Required fidelity surfaces:

- Fonts/typography: existing HFM Songti/system font tokens retained; large serif title and restrained metadata hierarchy match the source direction.
- Spacing/layout rhythm: split hero and immediate four-domain band implemented responsively; no horizontal overflow at the observed 1280px viewport.
- Colors/tokens: existing warm canvas, surface, text, heritage, accent, and border tokens reused; no new palette introduced.
- Images/assets: existing project book scan and heritage classroom assets used directly with semantic captions and alt text.
- Copy/content: existing `HOME_HERO`, `HOME_CHAPTERS`, and `HOME_DOMAINS` projections reused; no fabricated metrics or routes.

## Findings

No actionable P0/P1/P2 findings remain. The source is a 1536px-wide concept and the implementation was captured at 1280px, so exact pixel matching is not claimed; the responsive composition remains intact.

## Interaction evidence

- Search `甲乙经` submitted from `#home-search-input` and navigated to `/search?q=%E7%94%B2%E4%B9%99%E7%BB%8F`.
- Browser console error log: empty.
- DOM verification: one homepage H1, one `#home-domains` section, eight homepage sections, no horizontal overflow at 1280px.

## Comparison history

- Initial implementation: replaced the previous hero with the selected image direction and moved the existing four-domain section directly below the hero.
- Post-fix evidence: build passed; browser capture showed the intended hero, search, documentary imagery, and four-domain structure; no further P0/P1/P2 fix required.

## Implementation checklist

- [x] Reuse existing Vue components, routes, projections, tokens, and supplied assets.
- [x] Keep search functional and preserve the `#home-search-input` contract.
- [x] Verify production build and browser rendering.
- [x] Check console errors and horizontal overflow.

## Follow-up Polish

- [P3] If exact marketing-page parity is required, capture a 1440px browser viewport and tune the existing public header density to the concept mockup.

final result: passed
