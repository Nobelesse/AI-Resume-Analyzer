# v1.5.9.9.9.6 — Fast response desktop launcher and branded icon

The launcher opens the local loading page immediately and starts Streamlit in a minimized process. It checks the server health endpoint every 500 ms and redirects once a connection succeeds. Actual cold Streamlit startup **still takes time**: opening the splash in approximately a second is not the same as loading the complete app in a second. The launcher does not preload Ollama.

To install/update the icon on Windows: `powershell -ExecutionPolicy Bypass -File scripts\install_desktop_shortcut.ps1`.

Use the existing `.venv` on the user's own machine. Port 8501 must be free (or used by this app), otherwise a different server may open. A shortcut does not copy databases or models. The native launcher remains a simple batch file and is not a Windows service. If the splash remains, inspect the minimized terminal for errors.
