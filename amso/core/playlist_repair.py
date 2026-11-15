"""Recherche automatique et scoring de fichiers audio pour réparer les playlists."""

from __future__ import annotations

import logging
import os
import re
import unicodedata
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from pathlib import Path

from amso.core.database import DatabaseManager, PlaylistEntryRecord, TrackRecord
from amso.core.metadata import SUPPORTED_AUDIO_EXTENSIONS, extract_metadata

logger = logging.getLogger(__name__)

MIN_PROPOSAL_SCORE = 60
AUTO_CHECK_SCORE = 85

_LEADING_TRACK_NUM_RE = re.compile(r"^\s*(?:\d{1,3}\s*[-._)]\s*|\[\d{1,3}\]\s*)")
_EXTRACT_TRACK_NUM_RE = re.compile(r"^\s*(?:\[(\d{1,3})\]|(\d{1,3})\s*[-._)])")
_FEAT_RE = re.compile(r"\b(?:ft|feat|featuring)\.?\b", re.IGNORECASE)
_NON_ALNUM_RE = re.compile(r"[^\w\s]+", re.UNICODE)
_WHITESPACE_RE = re.compile(r"\s+")


@dataclass(slots=True)
class RepairCandidate:
    """Fichier audio candidat pour remplacer une entrée de playlist introuvable."""

    path: str
    score: int
    source_kind: str  # "local_dir" ou "library_db"
    title: str | None = None
    artist: str | None = None
    duration_seconds: float | None = None


@dataclass(slots=True)
class EntryRepairProposal:
    """Ensemble des propositions triées pour une entrée de playlist en anomalie."""

    entry_index: int
    entry: PlaylistEntryRecord
    candidates: list[RepairCandidate] = field(default_factory=list)

    @property
    def best(self) -> RepairCandidate | None:
        """Retourne le meilleur candidat s'il existe."""
        return self.candidates[0] if self.candidates else None


def _extract_track_number(text: str) -> int | None:
    """Extrait un numéro de piste entier en tête de chaîne (ex. '001 - Titre' -> 1)."""
    if not text:
        return None
    m = _EXTRACT_TRACK_NUM_RE.match(text)
    if not m:
        return None
    raw = m.group(1) or m.group(2)
    return int(raw) if raw else None


def normalize_match_text(text: str, *, strip_track_prefix: bool = False) -> str:
    """Normalise un texte (sans accents, minuscules, ponctuation nettoyée) pour comparaison."""
    if not text:
        return ""
    cleaned = text.strip()
    if strip_track_prefix:
        cleaned = _LEADING_TRACK_NUM_RE.sub("", cleaned)
    cleaned = _FEAT_RE.sub(" ", cleaned)
    decomposed = unicodedata.normalize("NFKD", cleaned)
    no_accents = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    alnum = _NON_ALNUM_RE.sub(" ", no_accents.lower().replace("_", " "))
    return _WHITESPACE_RE.sub(" ", alnum).strip()


def _text_similarity(a: str, b: str) -> float:
    """Retourne un ratio de similarité [0.0, 1.0] entre deux chaînes normalisées."""
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0
    seq_ratio = SequenceMatcher(None, a, b).ratio()
    tokens_a = set(a.split())
    tokens_b = set(b.split())
    if not tokens_a or not tokens_b:
        return seq_ratio
    overlap = len(tokens_a & tokens_b) / max(len(tokens_a), len(tokens_b))
    if a in b or b in a:
        min_len = min(len(a), len(b))
        max_len = max(len(a), len(b))
        containment = 0.78 + 0.22 * (min_len / max_len)
        return max(seq_ratio, overlap, containment)
    return max(seq_ratio, overlap)


def collect_local_audio_files(
    playlist_dir: Path,
    *,
    max_depth: int = 1,
    max_files: int = 1000,
) -> list[Path]:
    """Liste les fichiers audio dans le dossier de la playlist (et sous-dossiers proches)."""
    if not playlist_dir.is_dir():
        return []

    found: list[Path] = []
    queue: list[tuple[Path, int]] = [(playlist_dir, 0)]

    while queue and len(found) < max_files:
        current_dir, depth = queue.pop(0)
        try:
            with os.scandir(current_dir) as it:
                entries = sorted(it, key=lambda e: e.name.lower())
        except OSError:
            continue

        for item in entries:
            if len(found) >= max_files:
                break
            if item.name.startswith("."):
                continue
            try:
                if item.is_file():
                    if Path(item.name).suffix.lower() in SUPPORTED_AUDIO_EXTENSIONS:
                        found.append(Path(item.path))
                elif item.is_dir() and depth < max_depth:
                    queue.append((Path(item.path), depth + 1))
            except OSError:
                continue

    return found


def _score_candidate(
    *,
    entry_title_norm: str,
    entry_artist_norm: str,
    entry_stem_norm: str,
    entry_duration: float | None,
    entry_ext: str,
    playlist_dir_norm: str,
    cand_path: Path,
    cand_title: str | None,
    cand_artist: str | None,
    cand_duration: float | None,
    entry_track_num: int | None = None,
    cand_track_number: int | None = None,
) -> int:
    """Calcule un score de correspondance [0, 100] entre une anomalie et un candidat."""
    cand_stem_norm = normalize_match_text(cand_path.stem, strip_track_prefix=True)
    cand_title_norm = normalize_match_text(cand_title or "", strip_track_prefix=True)
    cand_artist_norm = normalize_match_text(cand_artist or "")
    cand_parent_norm = normalize_match_text(cand_path.parent.name)
    cand_grandparent_norm = normalize_match_text(cand_path.parent.parent.name)

    # 1. Titre (jusqu'à 45 pts, ou 62 pts si durée absente)
    sim_stem = _text_similarity(entry_title_norm, cand_stem_norm)
    sim_tag = _text_similarity(entry_title_norm, cand_title_norm) if cand_title_norm else 0.0
    title_sim = max(sim_stem, sim_tag)
    title_score = title_sim * 45.0

    # 2. Nom de fichier d'origine (jusqu'à 15 pts)
    orig_stem_sim = _text_similarity(entry_stem_norm, cand_stem_norm)
    stem_score = orig_stem_sim * 15.0

    # Garde-fou anti-faux-positifs : si le titre/nom a une ressemblance trop faible (< 45 %),
    # durée + artiste + dossier seuls ne doivent pas suffire à proposer le fichier.
    if entry_title_norm and max(title_sim, orig_stem_sim) < 0.45:
        return 0

    # 3. Durée (jusqu'à 25 pts, ou pénalité si écart fort)
    duration_score = 0.0
    if entry_duration is not None and entry_duration > 0 and cand_duration is not None and cand_duration > 0:
        diff = abs(entry_duration - cand_duration)
        if diff <= 1.5:
            duration_score = 25.0
        elif diff <= 3.0:
            duration_score = 18.0
        elif diff <= 6.0:
            duration_score = 8.0
        elif diff > 15.0:
            duration_score = -15.0
    else:
        # Si la durée n'est pas connue des deux côtés, on repondère le titre
        title_score = max(sim_stem, sim_tag) * 62.0

    # 4. Artiste (jusqu'à 10 pts)
    artist_score = 0.0
    if entry_artist_norm:
        sim_artist_tag = _text_similarity(entry_artist_norm, cand_artist_norm) if cand_artist_norm else 0.0
        sim_artist_stem = 1.0 if entry_artist_norm in cand_stem_norm else 0.0
        sim_artist_dir = max(
            _text_similarity(entry_artist_norm, cand_parent_norm),
            _text_similarity(entry_artist_norm, cand_grandparent_norm),
        )
        artist_score = max(sim_artist_tag, sim_artist_stem, sim_artist_dir) * 10.0

    # 5. Proximité de dossier & extension (jusqu'à 11 pts)
    proximity_score = 0.0
    if playlist_dir_norm and os.path.normcase(str(cand_path.parent)) == playlist_dir_norm:
        proximity_score += 10.0
    if entry_ext and cand_path.suffix.lower() == entry_ext:
        proximity_score += 1.0

    # 6. Numéro de piste entier (+8 pts si identique, -5 pts si différent)
    track_num_score = 0.0
    if entry_track_num is not None:
        cand_num = (
            cand_track_number
            if (cand_track_number is not None and cand_track_number > 0)
            else _extract_track_number(cand_path.stem)
        )
        if cand_num is not None:
            track_num_score = 8.0 if cand_num == entry_track_num else -5.0

    raw = title_score + stem_score + duration_score + artist_score + proximity_score + track_num_score
    return max(0, min(100, int(round(raw))))


def _query_db_candidates(db: DatabaseManager, entry: PlaylistEntryRecord) -> list[TrackRecord]:
    """Interroge l'index FTS5 de la bibliothèque pour trouver des pistes candidates."""
    queries: list[str] = []
    if entry.title:
        clean_title = normalize_match_text(entry.title, strip_track_prefix=True)
        if clean_title:
            queries.append(clean_title)
    stem_clean = normalize_match_text(Path(entry.raw_path or entry.resolved_path).stem, strip_track_prefix=True)
    if stem_clean and stem_clean not in queries:
        queries.append(stem_clean)
    if entry.artist:
        clean_artist = normalize_match_text(entry.artist)
        if clean_artist and clean_artist not in queries:
            queries.append(clean_artist)

    seen_ids: set[int] = set()
    results: list[TrackRecord] = []
    for query in queries:
        # Limite à 4 mots significatifs pour éviter une requête FTS trop restrictive
        short_q = " ".join(w for w in query.split() if len(w) >= 2)[:80]
        if not short_q:
            continue
        tracks, _ = db.search_tracks(short_q, limit=40)
        for track in tracks:
            if track.id is not None and track.id in seen_ids:
                continue
            if not track.source_ref or not os.path.isfile(track.source_ref):
                continue
            if track.id is not None:
                seen_ids.add(track.id)
            results.append(track)
        if len(results) >= 60:
            break
    return results


def _entry_hints(entry: PlaylistEntryRecord) -> tuple[str, str, str, str]:
    """Extrait les formes normalisées (title, artist, stem, ext) d'une entrée."""
    orig_path = Path(entry.raw_path or entry.resolved_path or "")
    entry_ext = orig_path.suffix.lower()
    entry_stem_norm = normalize_match_text(orig_path.stem, strip_track_prefix=True)
    entry_title_norm = normalize_match_text(entry.title or "", strip_track_prefix=True) or entry_stem_norm
    entry_artist_norm = normalize_match_text(entry.artist or "")
    return entry_title_norm, entry_artist_norm, entry_stem_norm, entry_ext


def find_local_repair_proposals(
    playlist_file_path: str,
    entries: Sequence[PlaylistEntryRecord],
    *,
    cancel_check: Callable[[], bool] | None = None,
    progress_cb: Callable[[int, int], None] | None = None,
) -> list[EntryRepairProposal]:
    """Passe 1 : recherche les fichiers candidats dans le dossier de la playlist."""
    missing_indices = [idx for idx, e in enumerate(entries) if e.is_missing]
    if not missing_indices:
        return []

    pl_path = Path(playlist_file_path) if playlist_file_path else None
    playlist_dir = pl_path.parent if pl_path else Path()
    playlist_dir_norm = os.path.normcase(str(playlist_dir)) if pl_path else ""

    local_files = collect_local_audio_files(playlist_dir) if pl_path else []
    metadata_cache: dict[str, TrackRecord] = {}
    proposals: list[EntryRepairProposal] = []
    total = len(missing_indices)

    for step, entry_idx in enumerate(missing_indices):
        if cancel_check and cancel_check():
            break

        entry = entries[entry_idx]
        entry_title_norm, entry_artist_norm, entry_stem_norm, entry_ext = _entry_hints(entry)
        entry_track_num = _extract_track_number(Path(entry.raw_path or entry.resolved_path or "").stem)
        by_norm_path: dict[str, RepairCandidate] = {}

        prelim_local: list[tuple[int, Path]] = []
        for cand_path in local_files:
            prelim_score = _score_candidate(
                entry_title_norm=entry_title_norm,
                entry_artist_norm=entry_artist_norm,
                entry_stem_norm=entry_stem_norm,
                entry_duration=None,
                entry_ext=entry_ext,
                playlist_dir_norm=playlist_dir_norm,
                cand_path=cand_path,
                cand_title=None,
                cand_artist=None,
                cand_duration=None,
                entry_track_num=entry_track_num,
            )
            if prelim_score >= 35:
                prelim_local.append((prelim_score, cand_path))

        prelim_local.sort(key=lambda pair: pair[0], reverse=True)
        for rank, (_, cand_path) in enumerate(prelim_local[:8]):
            if cancel_check and cancel_check():
                break
            path_str = str(cand_path)
            meta: TrackRecord | None = None
            if rank < 3:
                if path_str not in metadata_cache:
                    metadata_cache[path_str] = extract_metadata(cand_path, compute_hash=False)
                meta = metadata_cache[path_str]

            score = _score_candidate(
                entry_title_norm=entry_title_norm,
                entry_artist_norm=entry_artist_norm,
                entry_stem_norm=entry_stem_norm,
                entry_duration=entry.duration_seconds,
                entry_ext=entry_ext,
                playlist_dir_norm=playlist_dir_norm,
                cand_path=cand_path,
                cand_title=meta.title if meta else None,
                cand_artist=meta.artist if meta else None,
                cand_duration=meta.duration_seconds if meta else None,
                entry_track_num=entry_track_num,
                cand_track_number=meta.track_number if meta else None,
            )
            if score >= MIN_PROPOSAL_SCORE:
                norm_key = os.path.normcase(os.path.abspath(path_str))
                by_norm_path[norm_key] = RepairCandidate(
                    path=path_str,
                    score=score,
                    source_kind="local_dir",
                    title=meta.title if meta else cand_path.stem,
                    artist=meta.artist if meta else None,
                    duration_seconds=meta.duration_seconds if meta else None,
                )

        sorted_candidates = sorted(
            by_norm_path.values(),
            key=lambda c: (-c.score, c.path.lower()),
        )[:5]
        proposals.append(EntryRepairProposal(entry_index=entry_idx, entry=entry, candidates=sorted_candidates))
        if progress_cb:
            progress_cb(step + 1, total)

    return proposals


def enrich_proposals_with_db(
    db: DatabaseManager,
    playlist_file_path: str,
    proposals: Sequence[EntryRepairProposal],
    *,
    cancel_check: Callable[[], bool] | None = None,
    progress_cb: Callable[[int, int], None] | None = None,
) -> list[EntryRepairProposal]:
    """Passe 2 : complète les propositions locales avec l'index SQLite de la bibliothèque."""
    pl_path = Path(playlist_file_path) if playlist_file_path else None
    playlist_dir_norm = os.path.normcase(str(pl_path.parent)) if pl_path else ""
    total = len(proposals)
    enriched: list[EntryRepairProposal] = []

    for step, prop in enumerate(proposals):
        if cancel_check and cancel_check():
            break
        entry = prop.entry
        entry_title_norm, entry_artist_norm, entry_stem_norm, entry_ext = _entry_hints(entry)
        entry_track_num = _extract_track_number(Path(entry.raw_path or entry.resolved_path or "").stem)

        by_norm_path: dict[str, RepairCandidate] = {
            os.path.normcase(os.path.abspath(c.path)): c for c in prop.candidates
        }
        for track in _query_db_candidates(db, entry):
            if cancel_check and cancel_check():
                break
            cand_path = Path(track.source_ref)
            score = _score_candidate(
                entry_title_norm=entry_title_norm,
                entry_artist_norm=entry_artist_norm,
                entry_stem_norm=entry_stem_norm,
                entry_duration=entry.duration_seconds,
                entry_ext=entry_ext,
                playlist_dir_norm=playlist_dir_norm,
                cand_path=cand_path,
                cand_title=track.title,
                cand_artist=track.artist,
                cand_duration=track.duration_seconds,
                entry_track_num=entry_track_num,
                cand_track_number=track.track_number,
            )
            if score >= MIN_PROPOSAL_SCORE:
                norm_key = os.path.normcase(os.path.abspath(track.source_ref))
                existing = by_norm_path.get(norm_key)
                if existing is None or score > existing.score:
                    by_norm_path[norm_key] = RepairCandidate(
                        path=track.source_ref,
                        score=score,
                        source_kind="library_db",
                        title=track.title or cand_path.stem,
                        artist=track.artist,
                        duration_seconds=track.duration_seconds,
                    )

        sorted_candidates = sorted(
            by_norm_path.values(),
            key=lambda c: (-c.score, c.path.lower()),
        )[:5]
        enriched.append(EntryRepairProposal(entry_index=prop.entry_index, entry=entry, candidates=sorted_candidates))
        if progress_cb:
            progress_cb(step + 1, total)

    return enriched


def find_playlist_repair_proposals(
    db: DatabaseManager,
    playlist_file_path: str,
    entries: Sequence[PlaylistEntryRecord],
    *,
    cancel_check: Callable[[], bool] | None = None,
    progress_cb: Callable[[int, int], None] | None = None,
) -> list[EntryRepairProposal]:
    """Recherche des fichiers candidats (dossier de la playlist puis bibliothèque indexée)."""
    local_proposals = find_local_repair_proposals(
        playlist_file_path,
        entries,
        cancel_check=cancel_check,
        progress_cb=progress_cb,
    )
    if cancel_check and cancel_check():
        return local_proposals
    return enrich_proposals_with_db(
        db,
        playlist_file_path,
        local_proposals,
        cancel_check=cancel_check,
        progress_cb=progress_cb,
    )


def find_most_effective_folder(
    proposals: Sequence[EntryRepairProposal],
    playlist_dir: Path | None = None,
) -> tuple[str, int]:
    """Retourne (chemin_dossier, nb_anomalies_couvertes) du dossier couvrant le plus de pistes."""
    playlist_dir_norm = os.path.normcase(str(playlist_dir)) if playlist_dir else ""
    dir_entries: dict[str, set[int]] = {}
    dir_scores: dict[str, int] = {}
    dir_display: dict[str, str] = {}

    for prop in proposals:
        best_score_per_dir: dict[str, int] = {}
        for cand in prop.candidates:
            parent_str = str(Path(cand.path).parent)
            norm_dir = os.path.normcase(parent_str)
            dir_display.setdefault(norm_dir, parent_str)
            if norm_dir not in best_score_per_dir or cand.score > best_score_per_dir[norm_dir]:
                best_score_per_dir[norm_dir] = cand.score

        for norm_dir, best_s in best_score_per_dir.items():
            dir_entries.setdefault(norm_dir, set()).add(prop.entry_index)
            dir_scores[norm_dir] = dir_scores.get(norm_dir, 0) + best_s

    if not dir_entries:
        return "", 0

    best_norm = max(
        dir_entries,
        key=lambda d: (len(dir_entries[d]), dir_scores[d], 1 if d == playlist_dir_norm else 0),
    )
    return dir_display[best_norm], len(dir_entries[best_norm])
