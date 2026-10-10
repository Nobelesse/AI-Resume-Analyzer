# ResumeIntel UI Upgrade 0.9.0

The eight completed project milestones now display COMPLETED. Stale development notices and the Phase 2 UI demo caption have been removed. The main overview renders **real Streamlit button controls**, with session-scoped registered `st.Page` objects for safe navigation. Only permitted user/admin routes are available and the backend authorization still applies.

## Upload limit
The application enforces **2 MB = 2,000,000 bytes** in server-side validation. Streamlit's `server.maxUploadSize = 2` uses a MiB-aligned outer limit and is deliberately slightly more permissive; the application performs the final 2 MB check. This is intentional.

## Notes
Keyboard focus, reduced-motion support, phone layout and session handling must be verified in your browser. Animated previews are decorative and do not replace the real navigation tiles. Existing SQLite files and `.env` are never bundled for GitHub.
