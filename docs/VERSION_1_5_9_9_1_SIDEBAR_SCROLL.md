# Version 1.5.9.9.1 — Sidebar Scroll Repair

Fixes a regression from the global starfield: `stSidebar` had `overflow:hidden`, preventing access to below-the-fold user and admin routes on shorter screens. Restores an independent scroll area in Streamlit's `stSidebarContent` while preserving decorative stars and all application routes. No changes to skill data, SQLite, login, matching or reports.

**Check on Windows:** log into a user and admin account; scroll with the pointer over the sidebar until Job Match Studio and AI Career Finder are visible; select each page. Check sidebar collapse/expand, keyboard navigation, a 720px-high browser window and reduced-motion mode.
