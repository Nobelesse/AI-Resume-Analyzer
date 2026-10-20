# Stop desktop shortcut icon

The **Start** desktop shortcut retains `app/assets/app_icon.ico`. The **Stop** shortcut uses the separate red power-symbol asset `app/assets/stop_app_icon.ico`, converted from the approved artwork. No in-app Streamlit images or themes have been changed.

From the installed project root on Windows, run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\install_desktop_shortcut.ps1
```

The shortcut installer updates the existing icons in place. If Explorer caches the old icon, refresh the Desktop or sign out and sign in again.
