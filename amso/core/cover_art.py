"""Extraction des images de couverture (pochettes intégrées aux fichiers ou dans le dossier)."""

from __future__ import annotations

import re
from pathlib import Path

import mutagen

SUPPORTED_IMAGE_EXTENSIONS = (
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
    ".bmp",
    ".jfif",
    ".gif",
    ".tiff",
    ".tif",
    ".avif",
    ".ico",
)


def find_cover_image_in_folder(folder: Path, audio_stem: str = "") -> bytes | None:
    """Recherche la meilleure image de pochette disponible dans le dossier spécifié.

    Prend en compte folder.png, folder.jpg, cover, front, album, le nom du fichier audio,
    ou toute autre image présente dans le répertoire.
    Gère également les sous-dossiers multi-disques (CD1, Disc 2, etc.) en remontant au parent.
    """
    if not folder.is_dir():
        return None

    try:
        candidates = [f for f in folder.iterdir() if f.is_file() and f.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS]
    except OSError:
        candidates = []

    # Si aucun fichier image n'est présent dans le sous-dossier, tester le parent si CD1/Disc 1
    if not candidates and folder.parent != folder:
        folder_lower = folder.name.strip().lower()
        if folder_lower in {
            "cd1",
            "cd2",
            "cd3",
            "cd4",
            "cd5",
            "disc 1",
            "disc 2",
            "disc 3",
            "disc 4",
            "disc 5",
            "disc1",
            "disc2",
            "disc3",
            "disc4",
            "disk 1",
            "disk 2",
            "disk 3",
        }:
            try:
                candidates = [
                    f for f in folder.parent.iterdir() if f.is_file() and f.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS
                ]
            except OSError:
                candidates = []

    norm_audio_stem = audio_stem.strip().lower()

    def _score_image(file_path: Path) -> int:
        stem = file_path.stem.strip().lower()
        # 1. Priorité absolue : nom exact "folder" (folder.png, folder.jpg, etc.)
        if stem == "folder":
            score = 1000
        # 2. Pochette standard ("cover", "front")
        elif stem == "cover":
            score = 950
        elif stem == "front":
            score = 900
        # 3. Image portant exactement le même nom que le fichier audio (insensible à la casse)
        elif norm_audio_stem and stem == norm_audio_stem:
            score = 850
        # 4. Album / Artwork / Jacket / AlbumArt / CD / Disc
        elif stem in {"album", "artwork", "albumart", "albumartsmall", "jacket", "disc", "cd"}:
            score = 800
        else:
            # 5. Mots-clés composés séparés par des délimiteurs (_ - . ou espace)
            # Ex: "front_cover", "album-art", "soundtrack_artwork", "folder_1"
            # Ne matche JAMAIS des préfixes arbitraires sans délimiteur comme "exfolder"
            tokens = set(re.split(r"[\s_\-\.]+", stem))
            if "folder" in tokens:
                score = 750
            elif "cover" in tokens or "front" in tokens:
                score = 700
            elif "artwork" in tokens or "album" in tokens or "jacket" in tokens:
                score = 650
            elif "albumart" in tokens:
                score = 650
            elif "disc" in tokens or "cd" in tokens:
                score = 600
            else:
                # Aucune correspondance avec un nom de pochette audio -> image ignorée
                return 0

        # Bonus pour formats courants et bonus taille de fichier
        ext = file_path.suffix.lower()
        if ext in {".png", ".jpg", ".jpeg", ".webp", ".ico"}:
            score += 15
        try:
            sz = file_path.stat().st_size
            if sz > 1024:
                score += min(50, sz // 10240)
        except OSError:
            pass
        return score

    valid_candidates = []
    for cand in candidates:
        sc = _score_image(cand)
        if sc > 0:
            valid_candidates.append((sc, cand))

    if not valid_candidates:
        return None

    valid_candidates.sort(key=lambda x: x[0], reverse=True)
    for _, cand in valid_candidates:
        try:
            data = cand.read_bytes()
            if data and len(data) > 0:
                return data
        except OSError:
            continue
    return None


def extract_cover_art(file_path: str | Path) -> bytes | None:
    """Extrait l'image de couverture (pochette) d'un fichier audio ou de son dossier.

    1. Vérifie en priorité les tags intégrés (ID3 APIC, FLAC pictures, MP4 covr, OGG/Opus metadata_block_picture, WMA).
    2. Si aucune pochette n'est intégrée dans le fichier, recherche automatiquement dans le répertoire
       du fichier (folder.png, folder.jpg, cover, front, ou tout autre format image disponible).
    """
    try:
        path = Path(file_path).resolve()
    except Exception:
        return None

    # Si on passe directement un dossier
    if path.is_dir():
        return find_cover_image_in_folder(path)

    if not path.is_file():
        return None

    # 1. Tentative d'extraction depuis les métadonnées intégrées via Mutagen
    try:
        audio = mutagen.File(str(path))
        if audio is not None:
            # FLAC et formats compatibles avec audio.pictures
            if hasattr(audio, "pictures") and audio.pictures:
                data = bytes(audio.pictures[0].data)
                if data:
                    return data

            # MP3 / AIFF avec tags ID3
            if hasattr(audio, "tags") and audio.tags:
                tags = audio.tags
                # Recherche de frames APIC (ID3v2)
                for key in tags.keys():
                    if key.startswith("APIC"):
                        frame = tags[key]
                        if hasattr(frame, "data") and frame.data:
                            return bytes(frame.data)

                # MP4 / M4A (tag covr)
                if "covr" in tags:
                    covr = tags["covr"]
                    if covr and len(covr) > 0 and len(covr[0]) > 0:
                        return bytes(covr[0])

                # OGG / Opus / Vorbis Comment (metadata_block_picture)
                if "metadata_block_picture" in tags:
                    mbp = tags["metadata_block_picture"]
                    if mbp and len(mbp) > 0:
                        import base64

                        from mutagen.flac import Picture

                        pic = Picture(base64.b64decode(mbp[0]))
                        if pic and pic.data:
                            return bytes(pic.data)

                # WMA / ASF (WM/Picture)
                if "WM/Picture" in tags:
                    pic = tags["WM/Picture"]
                    if pic and len(pic) > 0:
                        raw = getattr(pic[0], "value", pic[0])
                        if isinstance(raw, (bytes, bytearray)) and len(raw) > 0:
                            return bytes(raw)
    except Exception:
        pass

    # 2. Fallback automatique : recherche dans le dossier du fichier audio
    parent = path.parent
    audio_stem = path.stem.strip().lower()
    return find_cover_image_in_folder(parent, audio_stem=audio_stem)
