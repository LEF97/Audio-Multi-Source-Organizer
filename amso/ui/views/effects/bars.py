"""Barres spectrales : mise à jour et peinture."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (
    QBrush,
    QColor,
    QLinearGradient,
    QPainter,
    QPen,
)
from PySide6.QtWidgets import QWidget

if TYPE_CHECKING:
    _MixinBase = QWidget
else:
    _MixinBase = object


class SpectrumBarsMixin(_MixinBase):
    """Barres spectrales : mise à jour et peinture."""

    if TYPE_CHECKING:
        # Attributs de VisualEffectWidget résolus dynamiquement (typage uniquement)
        _bar_levels: list[float]

        def __getattr__(self, name: str) -> Any: ...

    def _update_bars_tick(self, dt: float, w: float, h: float) -> None:
        """Anime les barres de spectre rétro et la dynamique des pics de crête."""
        if self._bars_align_left:
            target_count = max(20, min(56, int(w / 18.0))) if w > 50 else 24
        elif self._effect_type == self.EFFECT_BARS_FULL:
            target_count = max(32, min(64, int(w / 18.0))) if w > 100 else 40
        else:
            target_count = max(24, min(48, int(w / 24.0))) if w > 100 else 32
        if len(self._bar_levels) != target_count:
            self._bar_count = target_count
            self._bar_levels = [0.0] * target_count
            self._bar_targets = [0.0] * target_count
            self._bar_peaks = [0.0] * target_count
            self._bar_peak_holds = [0] * target_count
            self._bar_peak_speeds = [0.0] * target_count

        n = len(self._bar_levels)
        is_demo = getattr(self, "_demo_mode", False)
        is_playing = self._playback_state == "playing" or is_demo

        # 1. Tentative d'obtention du spectre audio réel en direct (WASAPI Loopback)
        real_levels = None
        if is_playing and self._audio_volume > 0.0 and not is_demo:
            try:
                from amso.services.audio_spectrum import get_audio_spectrum_service

                real_levels = get_audio_spectrum_service().get_spectrum(n)
            except Exception:
                real_levels = None

        if real_levels is not None:
            # Mode réel actif : les barres réagissent à 100% au son physique joué
            for i in range(n):
                self._bar_targets[i] = real_levels[i] * self._audio_volume
        else:
            # Mode repli procédural si capture système indisponible ou mode démo
            t = self._time
            t_sec = t if is_demo else ((self._audio_time_ms / 1000.0) if self._audio_time_ms > 0 else t)
            tempo = 2.4
            kick = max(0.0, math.sin(t_sec * tempo * math.pi * 2.0)) ** 4
            snare = max(0.0, math.sin((t_sec * tempo + 0.5) * math.pi * 2.0)) ** 6
            hihat = max(0.0, math.sin((t_sec * tempo * 2.0) * math.pi * 2.0)) ** 8
            macro = 0.72 + 0.28 * math.sin(t_sec * 0.35 + (self._track_seed % 100) * 0.1)
            vol = 0.85 if is_demo else self._audio_volume

            for i in range(n):
                if not is_playing or vol <= 0.0:
                    self._bar_targets[i] = 0.0
                else:
                    rel = i / max(1, n - 1)  # 0.0 = Bass, 1.0 = Treble
                    if rel < 0.28:
                        b_rel = rel / 0.28
                        wave = math.sin(t * 4.5 + i * 0.4) ** 2
                        amp = (kick * 0.72 + wave * 0.28) * (1.15 - b_rel * 0.4)
                        amp += 0.12 * math.sin(t * 8.0 + i)
                    elif rel < 0.70:
                        m_rel = (rel - 0.28) / 0.42
                        vocal = math.sin(t * 3.8 + i * 0.7 + self._track_seed * 0.05) ** 2
                        amp = snare * (0.52 - m_rel * 0.1) + vocal * 0.38 + 0.14 * math.sin(t * 9.5 + i)
                    else:
                        shimmer = (math.sin(t * 16.0 + i * 1.8) ** 4) * (0.6 + 0.4 * math.sin(t * 3.0))
                        amp = hihat * 0.58 + shimmer * 0.32 + 0.12 * math.sin(t * 24.0 + i * 2.0)

                    target = max(0.0, min(1.0, amp * macro * vol))
                    self._bar_targets[i] = target

        # Interpolation des niveaux : attaque très vive (0.65), relâchement analogique (0.20)
        for i in range(n):
            cur = self._bar_levels[i]
            tar = self._bar_targets[i]
            if tar > cur:
                self._bar_levels[i] = cur + (tar - cur) * 0.65
            else:
                self._bar_levels[i] = max(0.0, cur - (cur - tar) * 0.20)

            # Physique des crêtes (Peak hold & descente gravitationnelle)
            lvl = self._bar_levels[i]
            if lvl >= self._bar_peaks[i]:
                self._bar_peaks[i] = lvl
                self._bar_peak_holds[i] = 10
                self._bar_peak_speeds[i] = 0.0
            else:
                if self._bar_peak_holds[i] > 0:
                    self._bar_peak_holds[i] -= 1
                else:
                    self._bar_peak_speeds[i] += 0.0042
                    self._bar_peaks[i] = max(lvl, self._bar_peaks[i] - self._bar_peak_speeds[i])

    def _paint_bars(self, painter: QPainter, w: float, h: float) -> None:
        """Dessine un égaliseur de spectre rétro à barres LED segmentées avec maintien de crête."""
        n = len(self._bar_levels)
        if n == 0 or w <= 50 or h <= 50:
            return

        is_demo = getattr(self, "_demo_mode", False)
        if is_demo:
            painter.setOpacity(0.35)

        baseline_y = h - 12.0
        if self._bars_align_left:
            available_h = max(24.0, baseline_y - 2.0)
            max_bar_h = min(available_h, max(28.0, h * 0.72))
            seg_h = max(2.2, min(3.0, max_bar_h / 13.0))
            seg_gap = 1.0
            step_h = seg_h + seg_gap
            total_segs = max(8, int(max_bar_h / step_h))

            spacing = max(2.5, min(4.5, w / 200.0))
            total_spacing = (n - 1) * spacing
            total_span = max(10.0, w - 2.0)
            bar_w = max(4.0, (total_span - total_spacing) / n)
            actual_total_w = total_span
            start_x = 0.0
        else:
            max_bar_h = min(170.0, max(55.0, h * 0.42))
            seg_h = 3.2
            seg_gap = 1.2
            step_h = seg_h + seg_gap
            total_segs = max(10, int(max_bar_h / step_h))

            spacing = max(2.5, min(5.0, w / 260.0))
            total_spacing = (n - 1) * spacing
            total_span = min(w * 0.92, n * 24.0)
            bar_w = max(6.0, min(16.0, (total_span - total_spacing) / n))
            actual_total_w = n * bar_w + total_spacing
            start_x = (w - actual_total_w) / 2.0

        painter.setPen(Qt.PenStyle.NoPen)

        # 1. Dessin des barres segmentées (Matrice LED active + fond sombre inactif)
        for i in range(n):
            bx = start_x + i * (bar_w + spacing)
            lvl = max(0.0, min(1.0, self._bar_levels[i]))
            lit_segs = int(round(lvl * total_segs))
            peak_lvl = max(0.0, min(1.0, self._bar_peaks[i]))
            peak_seg = int(round(peak_lvl * total_segs))

            for s in range(total_segs):
                sy = baseline_y - (s + 1) * step_h
                ratio = s / float(total_segs)

                # Couleurs étagées style matériel Hi-Fi vintage :
                # - Vert fluo / Lime pour les niveaux usuels (0-60%)
                # - Ambre doré / Jaune pour les niveaux médians (60-82%)
                # - Rouge corail éclatant pour les crêtes (82-100%)
                if ratio < 0.60:
                    lit_color = QColor(34, 197, 94)  # #22C55E
                    dim_color = QColor(20, 50, 30, 40)
                elif ratio < 0.82:
                    lit_color = QColor(234, 179, 8)  # #EAB308
                    dim_color = QColor(50, 40, 12, 40)
                else:
                    lit_color = QColor(239, 68, 68)  # #EF4444
                    dim_color = QColor(55, 18, 18, 40)

                seg_rect = QRectF(bx, sy, bar_w, seg_h)
                if s < lit_segs:
                    painter.setBrush(QBrush(lit_color))
                    painter.drawRoundedRect(seg_rect, 1.0, 1.0)
                else:
                    painter.setBrush(QBrush(dim_color))
                    painter.drawRoundedRect(seg_rect, 1.0, 1.0)

            # Capuchon flottant de maintien de crête (Peak Cap)
            if peak_seg > 0 and peak_seg < total_segs:
                py = baseline_y - (peak_seg + 1) * step_h
                p_ratio = peak_seg / float(total_segs)
                if p_ratio < 0.60:
                    peak_color = QColor(134, 239, 172)
                elif p_ratio < 0.82:
                    peak_color = QColor(254, 240, 138)
                else:
                    peak_color = QColor(254, 202, 202)
                painter.setBrush(QBrush(peak_color))
                painter.drawRoundedRect(QRectF(bx, py, bar_w, seg_h), 1.0, 1.0)

            # 2. Reflet miroir en dessous du socle (verre acrylique fumé)
            if not self._bars_align_left:
                ref_segs = min(4, lit_segs)
                for r in range(ref_segs):
                    ry = baseline_y + (r + 1) * step_h - 2.0
                    alpha = 0.16 * (1.0 - r / 4.0)
                    ref_c = QColor(34, 197, 94) if r < 2 else QColor(56, 189, 248)
                    ref_c.setAlphaF(alpha)
                    painter.setBrush(QBrush(ref_c))
                    painter.drawRoundedRect(QRectF(bx, ry, bar_w, seg_h), 1.0, 1.0)

        # 3. Ligne de socle lumineuse et repères rétro
        line_y = baseline_y + 1.0
        x_left = start_x if self._bars_align_left else (start_x - 15.0)
        x_right = (start_x + actual_total_w) if self._bars_align_left else (start_x + actual_total_w + 15.0)
        grad = QLinearGradient(x_left, line_y, x_right, line_y)
        grad.setColorAt(0.0, QColor(56, 189, 248, 60 if self._bars_align_left else 0))
        grad.setColorAt(0.15, QColor(56, 189, 248, 120))
        grad.setColorAt(0.5, QColor(56, 189, 248, 140))
        grad.setColorAt(0.85, QColor(56, 189, 248, 120))
        grad.setColorAt(1.0, QColor(56, 189, 248, 60 if self._bars_align_left else 0))

        painter.setPen(QPen(QBrush(grad), 1.2))
        painter.drawLine(QPointF(x_left, line_y), QPointF(x_right, line_y))

        # Repères typographiques subtils (BASS / MID / TREBLE)
        painter.setPen(QColor(148, 163, 184, 120))
        font = painter.font()
        font.setPointSize(7 if self._bars_align_left else 8)
        font.setBold(True)
        painter.setFont(font)

        lbl_y = min(h - 2.0, baseline_y + 10.0)
        # Bass à 12%
        x_bass = start_x + (actual_total_w * 0.08 if self._bars_align_left else (actual_total_w * 0.12 - 12.0))
        painter.drawText(QPointF(x_bass, lbl_y), "BASS")
        # Mid à 50%
        x_mid = start_x + actual_total_w * 0.50 - 10.0
        painter.drawText(QPointF(x_mid, lbl_y), "MID")
        # Treble à 88%
        x_treb = start_x + (actual_total_w * 0.90 if self._bars_align_left else (actual_total_w * 0.88 - 18.0))
        painter.drawText(QPointF(x_treb, lbl_y), "TREBLE")

    def _paint_bars_full(self, painter: QPainter, w: float, h: float) -> None:
        """Dessine un égaliseur de spectre rétro géant couvrant toute la surface de l'écran avec matrice LED et repères studio."""
        n = len(self._bar_levels)
        if n == 0 or w <= 50 or h <= 50:
            return

        baseline_y = h - 26.0
        top_y = 20.0
        max_bar_h = max(80.0, baseline_y - top_y)

        # Hauteur des segments et espacement vertical
        step_h = max(4.6, min(7.5, max_bar_h / 52.0))
        seg_gap = 1.4
        seg_h = step_h - seg_gap
        total_segs = max(16, int(max_bar_h / step_h))

        # Disposition horizontale sur l'ensemble de la largeur disponible
        side_margin = max(16.0, min(36.0, w * 0.03))
        total_span = w - 2.0 * side_margin
        spacing = max(2.5, min(5.0, total_span / (n * 5.0)))
        bar_w = (total_span - (n - 1) * spacing) / n
        start_x = side_margin

        # 1. Grille d'alignement dB subtile façon rack de mastering vintage
        db_levels = [
            (0.88, "0 dB", QColor(239, 68, 68, 85)),  # Seuil rouge critique
            (0.72, "-6 dB", QColor(245, 158, 11, 45)),  # Seuil ambre
            (0.52, "-12 dB", QColor(6, 182, 212, 35)),  # Seuil cyan
            (0.24, "-24 dB", QColor(16, 185, 129, 25)),  # Seuil vert
        ]

        font_orig = painter.font()
        font_db = painter.font()
        font_db.setPointSize(7)
        font_db.setBold(True)
        painter.setFont(font_db)

        for ratio_lvl, db_txt, db_color in db_levels:
            ref_y = baseline_y - ratio_lvl * (total_segs * step_h)
            pen_db = QPen(db_color, 1.0, Qt.PenStyle.DotLine)
            painter.setPen(pen_db)
            painter.drawLine(QPointF(start_x, ref_y), QPointF(start_x + total_span, ref_y))
            # Repères texte sur les côtés
            painter.setPen(db_color)
            painter.drawText(QPointF(max(2.0, start_x - 30.0), ref_y + 3.0), db_txt)

        painter.setPen(Qt.PenStyle.NoPen)

        # 2. Dessin de chaque barre LED segmentée
        for i in range(n):
            bx = start_x + i * (bar_w + spacing)
            lvl = max(0.0, min(1.0, self._bar_levels[i]))
            lit_segs = int(round(lvl * total_segs))
            peak_lvl = max(0.0, min(1.0, self._bar_peaks[i]))
            peak_seg = int(round(peak_lvl * total_segs))

            for s in range(total_segs):
                sy = baseline_y - (s + 1) * step_h
                ratio = s / float(total_segs)

                # Échelonnage colorimétrique studio 4 zones :
                # - Vert émeraude électrique (0 - 52%)
                # - Cyan / Turquoise dynamique (52 - 72%)
                # - Ambre doré chaud (72 - 88%)
                # - Rouge corail éclatant (88 - 100%)
                if ratio < 0.52:
                    lit_color = QColor(16, 185, 129)  # #10B981
                    dim_color = QColor(16, 185, 129, 28)
                elif ratio < 0.72:
                    lit_color = QColor(6, 182, 212)  # #06B6D4
                    dim_color = QColor(6, 182, 212, 28)
                elif ratio < 0.88:
                    lit_color = QColor(245, 158, 11)  # #F59E0B
                    dim_color = QColor(245, 158, 11, 30)
                else:
                    lit_color = QColor(239, 68, 68)  # #EF4444
                    dim_color = QColor(239, 68, 68, 35)

                seg_rect = QRectF(bx, sy, bar_w, seg_h)
                if s < lit_segs:
                    painter.setBrush(QBrush(lit_color))
                    painter.drawRoundedRect(seg_rect, 1.2, 1.2)
                else:
                    painter.setBrush(QBrush(dim_color))
                    painter.drawRoundedRect(seg_rect, 1.2, 1.2)

            # Capuchon de maintien de pic flottant
            if peak_seg > 0 and peak_seg < total_segs:
                py = baseline_y - (peak_seg + 1) * step_h
                p_ratio = peak_seg / float(total_segs)
                if p_ratio < 0.52:
                    peak_color = QColor(167, 243, 208)
                elif p_ratio < 0.72:
                    peak_color = QColor(165, 243, 252)
                elif p_ratio < 0.88:
                    peak_color = QColor(254, 240, 138)
                else:
                    peak_color = QColor(254, 202, 202)

                painter.setBrush(QBrush(peak_color))
                painter.drawRoundedRect(QRectF(bx - 0.5, py, bar_w + 1.0, seg_h), 1.2, 1.2)

        # 3. Ligne de socle lumineuse et repères de fréquences ISO
        line_y = baseline_y + 1.0
        grad = QLinearGradient(start_x, line_y, start_x + total_span, line_y)
        grad.setColorAt(0.0, QColor(56, 189, 248, 20))
        grad.setColorAt(0.15, QColor(56, 189, 248, 90))
        grad.setColorAt(0.5, QColor(56, 189, 248, 160))
        grad.setColorAt(0.85, QColor(56, 189, 248, 90))
        grad.setColorAt(1.0, QColor(56, 189, 248, 20))

        painter.setPen(QPen(QBrush(grad), 1.4))
        painter.drawLine(QPointF(start_x, line_y), QPointF(start_x + total_span, line_y))

        # Repères de fréquences standards (style égaliseur 10 bandes Technics / Pioneer)
        painter.setPen(QColor(148, 163, 184, 130))
        font_freq = painter.font()
        font_freq.setPointSize(8)
        font_freq.setBold(True)
        painter.setFont(font_freq)

        freq_labels = ["31Hz", "63Hz", "125Hz", "250Hz", "500Hz", "1kHz", "2kHz", "4kHz", "8kHz", "16kHz"]
        lbl_y = baseline_y + 16.0
        k = len(freq_labels)
        for idx, lbl in enumerate(freq_labels):
            pos_x = start_x + (idx / float(k - 1)) * (total_span - 32.0)
            painter.drawText(QPointF(pos_x, lbl_y), lbl)

        painter.setFont(font_orig)
