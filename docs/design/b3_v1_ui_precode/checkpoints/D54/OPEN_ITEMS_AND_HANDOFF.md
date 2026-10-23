# Open Issues and Coding Handoff

1. Test the D54 HTML with previously saved palette data in the owner's Windows Chrome/Edge; mock storage origin remains browser-scoped.
2. Owner acceptance decision: is the desired MODULE rule 75% opacity (D54, higher fidelity of selected hue) or 75% transparency (previous prototype)? They are inverse and cannot simultaneously guarantee saturated blue over a saturated yellow background.
3. Complete the workspace/module/info/dataflow flow and its contract mapping; D54 only corrects color studio and theme role application.
4. Build reusable React design tokens, popovers, palette state model, modules and test fixtures. Do not copy the monolithic HTML as production source.
5. Keep all LAB/PAPER/LIVE and writer/grant boundaries. The Git snapshot is documentary, not formal coding or runtime authorization.
6. Add automated browser checks for first-open geometry, 100/50/100 saturation return, role index 2 binding, light/dark theme contrast, responsive layout and saved theme reload.

QA locally run in headless Chromium at 1500, 1104, 840, and 600px.
Initial triangle tip error [0.074,0.028,0.079,0.004] px; 50% error ~0.042 px. With mock yellow background and blue module role #127FE0, CSS module color used #127FE0 at 75% opacity. No JavaScript page errors in those runs.
