# Version 1.4.2.9 — Globe and Orbit Scale

Increase the globe size where browser room allows, and enlarge both orbit outlines around it while maintaining their former radial clearance from the sphere. Move the desktop center slightly toward the copy to make space for the larger geometry. Preserve the Dark Abyss + gold theme, ring palette and efficient closed-path rendering from v1.4.2.8.

The orbit radii are compensated for a target 1.08x scaling: `1 + (old_radius - 1) / 1.08`. Exact on-screen enlargement depends on the canvas dimensions and edge fitting; narrower windows may limit the increase.
