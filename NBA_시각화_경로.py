"""
NBA 시각화 PNG 파일의 저장 경로(폴더) 규칙.

목표:
- outputs/NBA_시각화_결과/ 아래를 '시각화 형태' 기준으로 폴더링
- 파일명(베이스네임)만 주면 항상 동일한 하위 폴더로 정해지도록 규칙화

주의:
- Windows 한글 경로/파일명 지원 전제
- 규칙은 '파일명에 포함된 키워드' 기반으로 분류 (가독성/유지보수 우선)
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class VizCategory:
    key: str
    folder: str


# 상위 우선순위부터 매칭 (가장 먼저 매칭되는 폴더로 분류)
_CATEGORIES: list[VizCategory] = [
    VizCategory("PPT", "99_PPT"),
    VizCategory("선수분석", "08_선수분석"),
    VizCategory("팀분석", "09_팀분석"),
    VizCategory("대시보드", "07_대시보드"),
    VizCategory("스캐터", "05_스캐터_관계"),
    VizCategory("박스플롯", "06_박스플롯"),
    VizCategory("승패_비교", "03_랭킹_바차트"),
    VizCategory("시즌별_비교", "02_히트맵_상관_비교"),
    VizCategory("히트맵", "02_히트맵_상관_비교"),
    VizCategory("상관관계", "02_히트맵_상관_비교"),
    VizCategory("분포", "01_분포_히스토그램_KDE"),
    VizCategory("Top", "03_랭킹_바차트"),
    VizCategory("성과", "03_랭킹_바차트"),
    VizCategory("기록_추이", "04_추이_라인차트"),
    VizCategory("트렌드", "04_추이_라인차트"),
    VizCategory("월별", "04_추이_라인차트"),
    VizCategory("고급", "11_고급분석"),
    VizCategory("포지션", "10_포지션분석"),
]


def categorize_png_name(png_name: str) -> str:
    """
    PNG 파일명(베이스네임)을 받아 저장 폴더(하위 폴더명)를 반환.
    """
    name = png_name
    for cat in _CATEGORIES:
        if cat.key in name:
            return cat.folder
    # fallback
    return "00_기타"


def viz_relpath(png_name: str) -> Path:
    """
    PNG 파일명(베이스네임) -> outputs/NBA_시각화_결과/ 아래 상대 경로(Path)
    """
    folder = categorize_png_name(png_name)
    return Path(folder) / png_name


def iter_pngs(root: Path) -> list[Path]:
    """
    root 아래의 모든 PNG를 재귀적으로 수집.
    """
    return sorted([p for p in root.rglob("*.png") if p.is_file()])


def organize_pngs(
    vis_root: Path,
    *,
    move: bool = True,
    keep_root_copy: bool = False,
) -> list[tuple[Path, Path]]:
    """
    vis_root 아래(재귀 포함)의 PNG를 규칙에 맞게 정리.

    - move=True: 원본을 이동
    - keep_root_copy=True: (move 후) 루트에 원본명으로 복사본을 남겨 호환성 유지

    반환: (src, dst) 변경 목록
    """
    changes: list[tuple[Path, Path]] = []
    for src in iter_pngs(vis_root):
        # 이미 분류된 폴더에 있으면 스킵
        try:
            rel = src.relative_to(vis_root)
        except Exception:
            continue

        # 베이스네임 기준으로 목적지 결정
        dst_rel = viz_relpath(src.name)
        dst = vis_root / dst_rel

        if rel == dst_rel:
            continue

        dst.parent.mkdir(parents=True, exist_ok=True)

        if move:
            src.replace(dst)
            if keep_root_copy:
                # 루트(Flat) 호환을 위해 복사본 남김
                flat = vis_root / dst.name
                if not flat.exists():
                    flat.write_bytes(dst.read_bytes())
            changes.append((src, dst))
        else:
            if not dst.exists():
                dst.write_bytes(src.read_bytes())
                changes.append((src, dst))

    return changes


