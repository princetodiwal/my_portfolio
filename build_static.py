from pathlib import Path
from shutil import copytree, rmtree
import re

from app import app


OUTPUT_DIR = Path("_site")
ROUTES = {
    "/": "index.html",
    "/skills": "skills/index.html",
    "/projects": "projects/index.html",
    "/certificates": "certificates/index.html",
    "/contact": "contact/index.html",
}
INTERNAL_PATHS = {
    "/": "index.html",
    "/skills": "skills/",
    "/projects": "projects/",
    "/certificates": "certificates/",
    "/contact": "contact/",
}


def relative_url(from_file: Path, target: str) -> str:
    source_dir = from_file.parent
    return target if source_dir == Path(".") else (
        "../" * len(source_dir.parts) + target
    )


def rewrite_local_links(html: str, output_file: Path) -> str:
    def rewrite_attr(match: re.Match[str]) -> str:
        attr, quote, url = match.groups()

        if url.startswith("/static/"):
            return f'{attr}={quote}{relative_url(output_file, "static/" + url.removeprefix("/static/"))}{quote}'

        if url in INTERNAL_PATHS:
            return f"{attr}={quote}{relative_url(output_file, INTERNAL_PATHS[url])}{quote}"

        return match.group(0)

    return re.sub(r'\b(href|src)=(["\'])(/[^"\']*)\2', rewrite_attr, html)


def build() -> None:
    if OUTPUT_DIR.exists():
        rmtree(OUTPUT_DIR)

    copytree("static", OUTPUT_DIR / "static")
    (OUTPUT_DIR / ".nojekyll").write_text("", encoding="utf-8")

    with app.test_client() as client:
        for route, destination in ROUTES.items():
            response = client.get(route)
            if response.status_code >= 400:
                raise RuntimeError(f"Failed to render {route}: HTTP {response.status_code}")

            output_file = OUTPUT_DIR / destination
            output_file.parent.mkdir(parents=True, exist_ok=True)
            html = response.get_data(as_text=True)
            output_file.write_text(rewrite_local_links(html, Path(destination)), encoding="utf-8")


if __name__ == "__main__":
    build()
