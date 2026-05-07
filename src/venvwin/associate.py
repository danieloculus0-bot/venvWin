from __future__ import annotations

from pathlib import Path


def exe_desktop_handler_content() -> str:
    return """[Desktop Entry]
Type=Application
Name=Open with venvWin
Comment=Open Windows executables through venvWin capsules
Exec=venvwin open %f
Terminal=false
MimeType=application/x-ms-dos-executable;application/x-msdownload;application/vnd.microsoft.portable-executable;
NoDisplay=false
Categories=Utility;
"""


def msi_desktop_handler_content() -> str:
    return """[Desktop Entry]
Type=Application
Name=Install with venvWin
Comment=Install Windows MSI packages through venvWin capsules
Exec=venvwin open %f
Terminal=false
MimeType=application/x-msi;application/x-ms-installer;
NoDisplay=false
Categories=Utility;
"""


def write_file_association_handlers(applications_dir: Path) -> list[Path]:
    applications_dir.mkdir(parents=True, exist_ok=True)

    exe_handler = applications_dir / "venvwin-open-exe.desktop"
    msi_handler = applications_dir / "venvwin-open-msi.desktop"

    exe_handler.write_text(exe_desktop_handler_content(), encoding="utf-8")
    msi_handler.write_text(msi_desktop_handler_content(), encoding="utf-8")

    return [exe_handler, msi_handler]


def default_applications_dir(home: Path | None = None) -> Path:
    base = home or Path.home()
    return base / ".local" / "share" / "applications"
