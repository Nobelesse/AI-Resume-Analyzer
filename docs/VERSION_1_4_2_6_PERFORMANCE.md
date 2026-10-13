# Version 1.4.2.7 — Hero Orbit Performance Fix

Optimized orbit rendering from hundreds of shadow-blurred 2D segment strokes per frame to two closed paths, each stroked twice. Orbit rotation is now independent of the mouse-controlled sphere. Pixel density is capped at 1.5, frame pacing targets 30 FPS, and the star count is moderated for Windows laptops with integrated graphics.

The original purple and cyan color palette, dark abyss hero, text, ATS system, O*NET catalog, SQLite and Ollama components are preserved. Automated source tests do not replace testing frame pacing in Chrome on the target laptop.
