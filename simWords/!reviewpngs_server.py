r"""Serve !reviewpngs.html and open clicked PNG files in Windows' default PNG application.

Run: py !reviewpngs_server.py --folder "D:\HostGatorFiles\public_html\notes\simTemp"
Then open: http://localhost:8081/!reviewpngs.html
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
import webbrowser
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

DEFAULT_FOLDER = Path(r"D:\HostGatorFiles\public_html\notes\simWords")
SNAGIT_EDITOR = Path(r"C:\Program Files\TechSmith\Snagit\SnagitEditor.exe")


def open_png(file_path: Path) -> None:
    """Open the original PNG in Snagit, falling back to the Windows association."""
    if SNAGIT_EDITOR.is_file():
        subprocess.Popen([str(SNAGIT_EDITOR), str(file_path)])
    else:
        os.startfile(file_path)


def safe_file(directory: Path, name: str, suffix: str) -> Path:
    """Return a direct child file path, rejecting paths outside the review folder."""
    path = (directory / Path(name).name).resolve()
    if path.parent != directory or path.suffix.lower() != suffix:
        raise ValueError(f"Invalid {suffix} file name: {name}")
    return path


def paired_text(path: Path) -> Path:
    return path.with_suffix(".txt")


def rename_pair(source: Path, target: Path) -> None:
    """Rename a PNG and its optional TXT measurement without copying image data."""
    if source != target:
        source.replace(target)
        source_text, target_text = paired_text(source), paired_text(target)
        if source_text.is_file():
            target_text.unlink(missing_ok=True)
            source_text.replace(target_text)


def apply_changes(directory: Path, payload: dict) -> None:
    """Apply staged review changes using native filesystem operations."""
    versions = payload.get("versions", {})
    suffixes = payload.get("suffixes", {})
    measurements = payload.get("measurements", {})

    for base_name, selected_name in versions.items():
        base = safe_file(directory, base_name, ".png")
        selected = safe_file(directory, selected_name, ".png")
        if not selected.is_file():
            raise FileNotFoundError(selected.name)
        group_prefix = base.stem
        for candidate in directory.glob(f"{group_prefix}*.png"):
            if candidate != selected and (candidate.stem == group_prefix or candidate.stem.startswith(f"{group_prefix}(")):
                candidate.unlink(missing_ok=True)
                paired_text(candidate).unlink(missing_ok=True)
        rename_pair(selected, base)

    for source_name, is_checked in suffixes.items():
        source = safe_file(directory, source_name, ".png")
        if not source.is_file():
            continue
        target_name = f"{source.stem}(x).png" if is_checked else source.name.replace("(x).png", ".png")
        rename_pair(source, safe_file(directory, target_name, ".png"))

    for name, value in measurements.items():
        path = safe_file(directory, name, ".png")
        if path.is_file():
            paired_text(path).write_text(f"{max(0, round(float(value)))}\n", encoding="ascii")


class ReviewHandler(SimpleHTTPRequestHandler):
    def end_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, X-File-Name")
        super().end_headers()

    def do_OPTIONS(self) -> None:
        self.send_response(HTTPStatus.NO_CONTENT)
        self.end_headers()

    def do_GET(self) -> None:
        request_path = urlparse(self.path).path
        if not request_path.startswith("/open/"):
            super().do_GET()
            return

        file_name = unquote(request_path.removeprefix("/open/"))
        file_path = (self.directory_path / file_name).resolve()
        if (
            file_path.parent != self.directory_path.resolve()
            or file_path.suffix.lower() != ".png"
            or not file_path.is_file()
        ):
            self.send_error(HTTPStatus.NOT_FOUND, "PNG file not found")
            return
        open_png(file_path)
        self.send_response(HTTPStatus.NO_CONTENT)
        self.end_headers()

    def do_POST(self) -> None:
        if urlparse(self.path).path == "/apply":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                payload = json.loads(self.rfile.read(content_length))
                apply_changes(self.directory_path.resolve(), payload)
            except (OSError, ValueError, json.JSONDecodeError) as error:
                self.send_error(HTTPStatus.BAD_REQUEST, str(error))
                return
            self.send_response(HTTPStatus.NO_CONTENT)
            self.end_headers()
            return
        if urlparse(self.path).path != "/open":
            self.send_error(HTTPStatus.NOT_FOUND, "Endpoint not found")
            return
        file_name = Path(unquote(self.headers.get("X-File-Name", "outline.png"))).name
        if Path(file_name).suffix.lower() != ".png":
            self.send_error(HTTPStatus.BAD_REQUEST, "Only PNG files can be opened")
            return
        content_length = int(self.headers.get("Content-Length", 0))
        if not content_length:
            self.send_error(HTTPStatus.BAD_REQUEST, "PNG data is missing")
            return
        launch_directory = Path(tempfile.gettempdir()) / "simWords-review"
        launch_directory.mkdir(exist_ok=True)
        file_path = launch_directory / file_name
        file_path.write_bytes(self.rfile.read(content_length))
        open_png(file_path)
        self.send_response(HTTPStatus.NO_CONTENT)
        self.end_headers()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the simWords PNG review server.")
    parser.add_argument("--folder", type=Path, default=DEFAULT_FOLDER, help="Folder containing review PNG files")
    parser.add_argument("--port", type=int, default=8081, help="Local server port")
    parser.add_argument("--open-browser", action="store_true", help="Open the review page after the server starts")
    args = parser.parse_args()
    directory = args.folder.resolve()
    if not directory.is_dir():
        parser.error(f"Folder does not exist: {directory}")

    handler = type("ConfiguredReviewHandler", (ReviewHandler,), {"directory_path": directory})
    server = ThreadingHTTPServer(("localhost", args.port), handler)
    print(f"Serving {directory} at http://localhost:{args.port}/!reviewpngs.html")
    if args.open_browser:
        webbrowser.open(f"http://localhost:{args.port}/!reviewpngs.html")
    server.serve_forever()


if __name__ == "__main__":
    main()