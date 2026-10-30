"""Script d'automatisation de la publication/mise à jour de la GitHub Release.

Ce script :
1. Détecte automatiquement la version à publier (depuis le tag Git ou le CHANGELOG).
2. Récupère le token GitHub de manière sécurisée via git credential helper.
3. Extrait les notes de version depuis CHANGELOG.fr.md.
4. Intègre automatiquement les captures d'écran de la version courante (*vX.Y.Z*.png) et transversales (Global*.png).
5. Crée ou met à jour la Release GitHub via l'API REST avec un corps enrichi.
6. Téléverse l'archive dist/AMSO-Windows-vX.Y.Z.zip si elle n'est pas encore présente.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


def get_project_root() -> Path:
    return Path(__file__).parent.parent.resolve()


def get_github_token() -> str:
    """Récupère le token GitHub depuis les variables d'environnement ou git-credential."""
    import os

    for env_var in ["GITHUB_TOKEN", "GH_TOKEN"]:
        val = os.environ.get(env_var)
        if val:
            return val.strip()

    try:
        p = subprocess.Popen(
            ["git", "credential", "fill"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        out, _ = p.communicate("protocol=https\nhost=github.com\n")
        for line in out.splitlines():
            if line.startswith("password="):
                return line.split("=", 1)[1].strip()
    except Exception as e:
        print(f"Avertissement credential helper : {e}")

    raise RuntimeError(
        "Impossible de récupérer le token GitHub. "
        "Définissez GITHUB_TOKEN ou configurez vos identifiants Git."
    )


def get_repo_slug(project_root: Path) -> str:
    """Extrait 'propriétaire/dépôt' depuis le remote git origin."""
    try:
        res = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            check=True,
        )
        url = res.stdout.strip()
        # https://github.com/OWNER/REPO.git ou git@github.com:OWNER/REPO.git
        m = re.search(r"github\.com[/:]([\w\-]+)/([\w\-]+)(?:\.git)?", url)
        if m:
            return f"{m.group(1)}/{m.group(2)}"
    except Exception:
        pass
    return "LEF97/Audio-Multi-Source-Organizer"


def get_target_version(project_root: Path, explicit_tag: str | None = None) -> tuple[str, str]:
    """Retourne (tag, version_clean) ex: ('v0.2.0', '0.2.0')."""
    if explicit_tag:
        clean = explicit_tag.lstrip("v")
        tag = f"v{clean}"
        return tag, clean

    # Tenter via le dernier tag Git
    try:
        res = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            check=True,
        )
        tag = res.stdout.strip()
        clean = tag.lstrip("v")
        return tag, clean
    except Exception:
        pass

    # Repli : première version publiée dans CHANGELOG.fr.md
    changelog = project_root / "CHANGELOG.md"
    if changelog.exists():
        for line in changelog.read_text(encoding="utf-8").splitlines():
            m = re.match(r"^##\s+\[(\d+\.\d+\.\d+)\]", line)
            if m:
                clean = m.group(1)
                return f"v{clean}", clean

    raise RuntimeError("Impossible de déterminer la version cible pour la release.")


def extract_changelog_section(changelog_path: Path, version: str) -> str:
    """Extrait la section correspondant à la version dans un CHANGELOG."""
    if not changelog_path.exists():
        return ""

    content = changelog_path.read_text(encoding="utf-8")
    lines = content.splitlines()
    capturing = False
    release_lines: list[str] = []

    pattern = re.compile(rf"^##\s+\[{re.escape(version)}\]")

    for line in lines:
        if pattern.match(line):
            capturing = True
            continue
        if capturing and re.match(r"^##\s+\[", line):
            break
        if capturing:
            release_lines.append(line)

    return "\n".join(release_lines).strip()


def find_release_screenshots(project_root: Path, version: str) -> list[str]:
    """Trouve les captures d'écran de la version courante et globales."""
    screenshots_dir = project_root / "screenshots"
    if not screenshots_dir.exists():
        return []

    results: list[str] = []
    # Règle : captures contenant vX.Y.Z
    for img in sorted(screenshots_dir.glob(f"*v{version}*.png")):
        results.append(img.name)

    # Règle : captures transversales commençant par Global
    for img in sorted(screenshots_dir.glob("Global*.png")):
        if img.name not in results:
            results.append(img.name)

    return results


def build_release_body(
    repo_slug: str,
    tag: str,
    version: str,
    changelog_notes: str,
    screenshots: list[str],
) -> str:
    """Construit le contenu markdown complet de la GitHub Release."""
    sections: list[str] = []

    sections.append(f"# 🎵 Audio Multi-Source Organizer (AMSO) {tag}\n")
    sections.append(
        "> **AMSO** is an open-source application that unifies, deduplicates and synchronizes "
        "your local, cloud and streaming music libraries.\n"
    )
    sections.append("---\n")

    # Screenshots intégrés
    if screenshots:
        sections.append("### 📸 Release preview\n")
        for s in screenshots:
            url_s = urllib.parse.quote(s)
            img_url = f"https://raw.githubusercontent.com/{repo_slug}/{tag}/screenshots/{url_s}"
            sections.append(
                f'<p align="center">\n  <img src="{img_url}" alt="AMSO {tag} - {s}" width="800">\n</p>\n'
            )
        sections.append("---\n")

    # Tableau des téléchargements
    sections.append("## 📦 Official Windows downloads\n")
    sections.append("| File | Description | Format |")
    sections.append("| :--- | :--- | :--- |")
    sections.append(
        f"| **`AMSO-Windows-{tag}.zip`** | **Recommended full archive** (portable executable + translations + documentation) | `.zip` |"
    )
    sections.append(
        "| **`AMSO.exe`** | Standalone portable Windows executable | `.exe` |\n"
    )
    sections.append("### 🐧🍎 Linux and macOS — experimental, untested\n")
    sections.append(
        "These packages are built automatically by the CI but have **not been tested** on real systems. "
        "**VLC must be installed**; the `.dmg` is unsigned (right-click → Open). See the README for details; "
        "your feedback (`startup.log`, `crash.log`) is welcome.\n"
    )
    sections.append("| File | System |")
    sections.append("| :--- | :--- |")
    sections.append(f"| `AMSO-Linux-{tag}-x86_64.AppImage` / `.tar.gz` | Linux x86_64 |")
    sections.append(f"| `AMSO-macOS-arm64-{tag}.dmg` | macOS Apple Silicon |")
    sections.append(f"| `AMSO-macOS-x86_64-{tag}.dmg` | macOS Intel |\n")
    sections.append("---\n")

    # Journal des modifications
    sections.append("## 📝 Changelog\n")
    if changelog_notes:
        sections.append(changelog_notes)
    else:
        sections.append("See `CHANGELOG.md` for the list of changes.")
    sections.append("\n---\n")

    # Liens utiles
    sections.append(
        "**Useful links:**\n"
        f"- 🌟 [GitHub repository](https://github.com/{repo_slug})\n"
        "- 🎮 [Official itch.io page](https://arnaudlef97.itch.io/amso)\n"
        "- ☕ [Support the project on Ko-fi](https://ko-fi.com/arnaudlef97)\n"
    )

    return "\n".join(sections)


def publish_github_release(tag: str | None = None) -> int:
    """Publie ou met à jour la GitHub Release avec ses assets."""
    project_root = get_project_root()
    repo_slug = get_repo_slug(project_root)
    tag_name, clean_ver = get_target_version(project_root, tag)
    token = get_github_token()

    print("=" * 60)
    print(f"  AMSO — Publication GitHub Release pour {tag_name}")
    print(f"  Dépôt : {repo_slug}")
    print("=" * 60)

    changelog_file = project_root / "CHANGELOG.md"
    notes = extract_changelog_section(changelog_file, clean_ver)
    screenshots = find_release_screenshots(project_root, clean_ver)
    body = build_release_body(repo_slug, tag_name, clean_ver, notes, screenshots)

    title = f"AMSO {tag_name}"

    # Vérifier si la release existe déjà
    api_base = f"https://api.github.com/repos/{repo_slug}/releases"
    check_url = f"{api_base}/tags/{tag_name}"
    req_check = urllib.request.Request(
        check_url,
        headers={
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "AMSO-Release-Agent",
        },
    )

    existing_release: dict | None = None
    try:
        with urllib.request.urlopen(req_check) as r:
            existing_release = json.loads(r.read().decode("utf-8"))
            print(f"Release existante détectée (ID: {existing_release['id']}).")
    except urllib.error.HTTPError as e:
        if e.code != 404:
            print(f"Erreur HTTP lors de la vérification de la release : {e}")
            return 1

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json",
        "User-Agent": "AMSO-Release-Agent",
    }

    if existing_release:
        release_id = existing_release["id"]
        update_url = f"{api_base}/{release_id}"
        payload = {"name": title, "body": body, "draft": False, "prerelease": False}
        print(f"Mise à jour des notes et visuels sur la release {release_id}...")
        req = urllib.request.Request(
            update_url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="PATCH",
        )
    else:
        payload = {
            "tag_name": tag_name,
            "target_commitish": "main",
            "name": title,
            "body": body,
            "draft": False,
            "prerelease": False,
        }
        print(f"Création de la release officielle {tag_name}...")
        req = urllib.request.Request(
            api_base,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )

    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            html_url = data.get("html_url", "")
            upload_url_tmpl = data.get("upload_url", "")
            assets = data.get("assets", [])
            print(f"[OK] Release publiée : {html_url}")
    except urllib.error.HTTPError as e:
        print(f"[ERREUR] Échec requête GitHub : {e.read().decode('utf-8')}")
        return 1

    # Téléversement de l'archive ZIP si elle n'est pas encore attachée
    zip_filename = f"AMSO-Windows-{tag_name}.zip"
    zip_path = project_root / "dist" / zip_filename
    existing_asset_names = [a.get("name") for a in assets]

    if zip_path.exists() and zip_filename not in existing_asset_names:
        upload_url = upload_url_tmpl.split("{")[0] + f"?name={zip_filename}"
        print(f"Téléversement de l'archive {zip_filename} ({zip_path.stat().st_size / (1024*1024):.1f} Mo)...")
        with open(zip_path, "rb") as f:
            zip_bytes = f.read()

        upload_req = urllib.request.Request(
            upload_url,
            data=zip_bytes,
            headers={
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json",
                "Content-Type": "application/zip",
                "User-Agent": "AMSO-Release-Agent",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(upload_req) as u_resp:
                u_data = json.loads(u_resp.read().decode("utf-8"))
                print(f"[OK] Asset attaché avec succès : {u_data.get('browser_download_url')}")
        except urllib.error.HTTPError as e:
            print(f"[AVERTISSEMENT] Échec de l'upload de l'asset : {e.read().decode('utf-8')}")
    else:
        if zip_filename in existing_asset_names:
            print(f"L'asset {zip_filename} est déjà présent dans la release.")

    print("\n" + "=" * 60)
    print("  SUCCÈS : GitHub Release synchronisée avec succès !")
    print(f"  Consulter : {html_url}")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Publier automatiquement la GitHub Release")
    parser.add_argument("--tag", type=str, help="Tag Git cible (ex: v0.2.0)")
    args = parser.parse_args()
    sys.exit(publish_github_release(tag=args.tag))
