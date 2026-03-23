"""
NBA 데이터 시각화 모듈

이 모듈은 전처리된 NBA 데이터를 시각화합니다.
"""

import os
from typing import Optional

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import platform
import seaborn as sns
import warnings
from matplotlib import font_manager
from pathlib import Path

import NBA_설정 as config
from NBA_시각화_경로 import viz_relpath

warnings.filterwarnings("ignore")


class NBADataVisualizer:
    """
    NBA 데이터 시각화 클래스

    주요 기능:
    - 한글 폰트 자동 설정
    - 다양한 시각화 생성
    - 고해상도 이미지 저장
    """

    def __init__(self, base_dir: Optional[str] = None):
        """
        초기화

        Args:
            base_dir: 작업 디렉토리 경로 (None이면 config에서 가져옴)
        """
        self.base_dir = base_dir or config.BASE_DIR
        self.df: Optional[pd.DataFrame] = None
        self.output_dir = config.VISUALIZATIONS_DIR
        os.makedirs(self.output_dir, exist_ok=True)

        self.setup_korean_font()

    def setup_korean_font(self):
        """한글 폰트 설정"""
        # 핵심: "폰트 이름만" 지정하면 환경에 따라 fallback이 발생할 수 있어
        # Windows의 경우 폰트 파일을 찾아 addfont()로 등록 후, 해당 폰트 이름으로 고정한다.
        # 주의: seaborn 스타일 설정(sns.set_style)이 matplotlib rcParams를 덮어쓸 수 있으므로,
        #       스타일을 먼저 적용한 뒤 폰트를 고정한다.
        sns.set_style("whitegrid")

        def _apply_font_family(font_name: str) -> None:
            plt.rcParams["font.family"] = font_name
            matplotlib.rcParams["font.family"] = font_name
            # sans-serif 후보에도 넣어 fallback 안정화
            matplotlib.rcParams["font.sans-serif"] = [font_name, "DejaVu Sans", "Arial"]

        def _try_add_font(path_str: str) -> Optional[str]:
            try:
                p = Path(path_str)
                if not p.exists():
                    return None
                font_manager.fontManager.addfont(str(p))
                name = font_manager.FontProperties(fname=str(p)).get_name()
                return name
            except Exception:
                return None

        # font cache rebuild (best-effort)
        try:
            font_manager._rebuild()
        except Exception:
            pass

        sys_name = platform.system()
        selected_font: Optional[str] = None

        if sys_name == "Windows":
            # 1) 설치된 폰트 이름 우선 탐색
            font_list = {f.name for f in font_manager.fontManager.ttflist}
            for f in config.KOREAN_FONTS_WINDOWS:
                if f in font_list:
                    selected_font = f
                    break

            # 2) 폰트 이름이 안 잡히면, Windows 폰트 파일을 직접 등록 시도
            if not selected_font:
                win_font_candidates = [
                    r"C:\Windows\Fonts\malgun.ttf",     # Malgun Gothic
                    r"C:\Windows\Fonts\malgunsl.ttf",   # Malgun Gothic Semilight
                    r"C:\Windows\Fonts\gulim.ttc",
                    r"C:\Windows\Fonts\batang.ttc",
                ]
                for fp in win_font_candidates:
                    name = _try_add_font(fp)
                    if name:
                        selected_font = name
                        break

            if selected_font:
                _apply_font_family(selected_font)
                print(f"[OK] 한글 폰트 설정: {selected_font}")
            else:
                # 마지막 fallback: 깨질 수 있으니 경고를 명확히 출력
                _apply_font_family("DejaVu Sans")
                print("[WARN] 한글 폰트를 찾지 못했습니다. 한글이 깨질 수 있습니다. (Windows: Malgun Gothic 설치/확인 필요)")
        else:
            # Mac/Linux: 지정 폰트가 없으면 역시 fallback될 수 있음
            font_name = config.KOREAN_FONT_MAC if sys_name == "Darwin" else config.KOREAN_FONT_LINUX
            _apply_font_family(font_name)
            print(f"[OK] 한글 폰트 설정: {font_name}")

        # 마이너스 기호 깨짐 방지
        plt.rcParams["axes.unicode_minus"] = False
        matplotlib.rcParams["axes.unicode_minus"] = False

    def load_data(self):
        """전처리된 데이터 로드"""
        print("\n" + "=" * 60)
        print("데이터 로드")
        print("=" * 60)

        if os.path.exists(config.MERGED_PKL):
            self.df = pd.read_pickle(config.MERGED_PKL)
            print(f"[OK] PKL 파일 로드 완료: {self.df.shape}")
        elif os.path.exists(config.FINAL_CSV):
            self.df = pd.read_csv(config.FINAL_CSV)
            if "GAME_DATE_EST" in self.df.columns:
                self.df["GAME_DATE_EST"] = pd.to_datetime(self.df["GAME_DATE_EST"])
            print(f"[OK] CSV 파일 로드 완료: {self.df.shape}")
        else:
            raise FileNotFoundError(
                "전처리된 데이터 파일을 찾을 수 없습니다. "
                f"다음 중 하나가 필요합니다: {config.MERGED_PKL} 또는 {config.FINAL_CSV}"
            )

    def _save_figure(self, fig: plt.Figure, filename: str) -> None:
        """
        시각화 결과를 '시각화 형태별 폴더' 규칙에 맞춰 저장.
        """
        out_path = Path(self.output_dir) / viz_relpath(filename)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(out_path, dpi=config.DPI, bbox_inches="tight")
        plt.close(fig)

    def visualize_correlation_heatmap(self):
        """상관관계 히트맵 생성"""
        print("\n[1/5] 상관관계 히트맵 생성 중...")

        corr_cols = [c for c in config.CORRELATION_COLS if c in self.df.columns]
        if len(corr_cols) < 2:
            print("[WARN] 상관관계 분석에 필요한 컬럼이 부족합니다.")
            return

        corr_matrix = self.df[corr_cols].corr()

        fig, ax = plt.subplots(figsize=(14, 12))
        sns.heatmap(
            corr_matrix,
            annot=True,
            fmt=".2f",
            cmap="RdBu_r",
            center=0,
            vmin=-1,
            vmax=1,
            square=True,
            linewidths=0.5,
            cbar_kws={"shrink": 0.8},
            ax=ax,
        )
        ax.set_title("주요 지표 간 상관관계 히트맵", fontsize=16, fontweight="bold", pad=20)
        plt.tight_layout()
        self._save_figure(fig, "NBA_01_상관관계_히트맵.png")
        print("[OK] 완료")

    def visualize_top_players(self):
        """선수별 평균 득점 Top 10 생성"""
        print("\n[2/5] 선수별 득점 Top 10 생성 중...")

        if "PLAYER_NAME" not in self.df.columns:
            print("[WARN] PLAYER_NAME 컬럼이 없어 선수별 집계가 불가합니다.")
            return

        player_stats = self.df.groupby("PLAYER_NAME").agg({"MIN": "sum", "PTS": "mean"}).reset_index()

        qualified_players = player_stats[player_stats["MIN"] >= config.MIN_MINUTES_THRESHOLD].copy()
        if qualified_players.empty:
            print("[WARN] 최소 출전 시간 조건을 만족하는 선수가 없습니다.")
            return

        top_players = qualified_players.nlargest(config.TOP_PLAYERS_COUNT, "PTS")

        fig, ax = plt.subplots(figsize=(12, 8))
        palette = sns.color_palette("Blues", n_colors=len(top_players))

        bars = ax.barh(
            range(len(top_players)),
            top_players["PTS"].values,
            color=palette,
            alpha=0.6,
            edgecolor="white",
            linewidth=1.2,
        )
        ax.set_yticks(range(len(top_players)))
        ax.set_yticklabels(top_players["PLAYER_NAME"].values, fontsize=10)
        ax.set_xlabel("평균 득점", fontsize=12)
        ax.set_title(
            f"선수별 평균 득점 Top {config.TOP_PLAYERS_COUNT} (최소 {config.MIN_MINUTES_THRESHOLD}분 출전)",
            fontsize=14,
            fontweight="bold",
        )
        ax.invert_yaxis()
        ax.grid(True, alpha=0.25, axis="x", color="#DDDDDD")
        ax.set_facecolor("#FFFFFF")

        for i, val in enumerate(top_players["PTS"].values):
            ax.text(
                val,
                i,
                f"{val:.2f}",
                va="center",
                ha="left",
                fontsize=9,
                fontweight="bold",
                color="#333333",
            )

        plt.tight_layout()
        self._save_figure(fig, "NBA_02_선수별_득점_Top10.png")
        print("[OK] 완료")

    def visualize_seasonal_trends(self):
        """시즌별 평균 기록 추이 생성"""
        print("\n[3/5] 시즌별 기록 추이 생성 중...")

        if "SEASON_STR" not in self.df.columns:
            print("[WARN] 시즌 정보가 없습니다. (SEASON_STR 컬럼 없음)")
            return

        season_stats = (
            self.df.groupby("SEASON_STR")
            .agg({"PTS": "mean", "AST": "mean", "REB": "mean"})
            .reset_index()
            .sort_values("SEASON_STR")
        )

        y_min = season_stats[["PTS", "AST", "REB"]].min().min()
        y_max = season_stats[["PTS", "AST", "REB"]].max().max()
        margin = (y_max - y_min) * 0.1 if y_max > y_min else 1

        fig, ax = plt.subplots(figsize=(12, 5))
        ax.plot(
            season_stats["SEASON_STR"],
            season_stats["PTS"],
            marker="o",
            label="평균 득점",
            linewidth=2.8,
            color="tab:red",
            markersize=6,
        )
        ax.plot(
            season_stats["SEASON_STR"],
            season_stats["AST"],
            marker="s",
            label="평균 어시스트",
            linewidth=2.8,
            color="tab:blue",
            markersize=6,
        )
        ax.plot(
            season_stats["SEASON_STR"],
            season_stats["REB"],
            marker="^",
            label="평균 리바운드",
            linewidth=2.8,
            color="tab:green",
            markersize=6,
        )

        ax.set_ylim(y_min - margin, y_max + margin)
        ax.set_title("시즌별 평균 기록 추이", fontsize=14, fontweight="bold")
        ax.set_xlabel("시즌", fontsize=12)
        ax.set_ylabel("기록", fontsize=12)
        ax.legend(fontsize=10, framealpha=0.9, facecolor="white")
        ax.grid(True, alpha=0.3, color="#E0E0E0")
        ax.set_facecolor("#FFFFFF")
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha="right")

        plt.tight_layout()
        self._save_figure(fig, "NBA_03_시즌별_기록_추이.png")
        print("[OK] 완료")

    def visualize_win_loss_comparison(self):
        """홈팀 승/패 비교 생성"""
        print("\n[4/5] 승/패 비교 생성 중...")

        required_cols = {"HOME_TEAM_ID", "TEAM_ID", "PLUS_MINUS"}
        if not required_cols.issubset(set(self.df.columns)):
            print(f"[WARN] 승/패 비교에 필요한 컬럼이 부족합니다: {sorted(required_cols)}")
            return

        home_df = self.df[self.df["HOME_TEAM_ID"] == self.df["TEAM_ID"]].copy()
        win_df = home_df[home_df["PLUS_MINUS"] > 0]
        loss_df = home_df[home_df["PLUS_MINUS"] <= 0]

        comparison_metrics = [c for c in config.COMPARISON_METRICS if c in self.df.columns]
        if not comparison_metrics:
            print("[WARN] 비교 지표가 없습니다.")
            return

        win_avg = win_df[comparison_metrics].mean()
        loss_avg = loss_df[comparison_metrics].mean()
        comparison_df = pd.DataFrame({"승리": win_avg, "패배": loss_avg})

        fig, ax = plt.subplots(figsize=(12, 6))
        x = np.arange(len(comparison_metrics))
        width = 0.35
        base_colors = sns.color_palette("Set2", n_colors=len(comparison_metrics))

        for i, metric in enumerate(comparison_metrics):
            win_val = comparison_df.loc[metric, "승리"]
            loss_val = comparison_df.loc[metric, "패배"]
            color = base_colors[i]
            ax.bar(
                i - width / 2,
                win_val,
                width,
                label="승리" if i == 0 else "",
                color=color,
                alpha=0.9,
                edgecolor="white",
                linewidth=1.2,
            )
            ax.bar(
                i + width / 2,
                loss_val,
                width,
                label="패배" if i == 0 else "",
                color=color,
                alpha=0.4,
                edgecolor="white",
                linewidth=1.2,
            )

        ax.set_xlabel("지표", fontsize=12)
        ax.set_ylabel("평균값", fontsize=12)
        ax.set_title("홈팀 승/패 핵심 지표 비교", fontsize=14, fontweight="bold")
        ax.set_xticks(x)
        ax.set_xticklabels(comparison_metrics, rotation=45, ha="right")
        ax.legend(fontsize=11, framealpha=0.9, facecolor="white")
        ax.grid(True, alpha=0.3, axis="y", color="#E0E0E0")
        ax.set_facecolor("#FFFFFF")

        plt.tight_layout()
        self._save_figure(fig, "NBA_04_승패_비교.png")
        print("[OK] 완료")

    def visualize_dashboard(self):
        """종합 대시보드 생성"""
        print("\n[5/5] 종합 대시보드 생성 중...")

        # KPI 요약
        kpi_metrics = [c for c in config.KPI_METRICS if c in self.df.columns]
        kpi_summary = self.df[kpi_metrics].mean() if kpi_metrics else pd.Series(dtype=float)

        # 홈 승률
        home_mask = (self.df["HOME_TEAM_ID"] == self.df["TEAM_ID"]) if {"HOME_TEAM_ID", "TEAM_ID"}.issubset(self.df.columns) else None
        if home_mask is not None:
            home_df = self.df[home_mask].copy()
            win_rate = (home_df["PLUS_MINUS"] > 0).mean() * 100 if "PLUS_MINUS" in home_df.columns else np.nan
        else:
            home_df = self.df.copy()
            win_rate = np.nan

        # 시즌별 평균 득점
        season_summary = None
        if "SEASON_STR" in self.df.columns and "PTS" in self.df.columns:
            season_summary = (
                self.df.groupby("SEASON_STR")["PTS"]
                .mean()
                .reset_index()
                .sort_values("SEASON_STR")
            )

        # 팀별 PLUS_MINUS 상위 팀
        team_col = "TEAM_ABBREVIATION" if "TEAM_ABBREVIATION" in self.df.columns else "TEAM_ID"
        top_teams = None
        if team_col in self.df.columns and "PLUS_MINUS" in self.df.columns:
            team_plus = self.df.groupby(team_col)["PLUS_MINUS"].mean().reset_index()
            top_teams = team_plus.sort_values("PLUS_MINUS", ascending=False).head(config.TOP_TEAMS_COUNT)

        # 승/패 비교 요약
        comparison_metrics = [c for c in config.COMPARISON_METRICS if c in self.df.columns]
        if "PLUS_MINUS" in home_df.columns and comparison_metrics:
            win_df = home_df[home_df["PLUS_MINUS"] > 0]
            loss_df = home_df[home_df["PLUS_MINUS"] <= 0]
            diff = (win_df[comparison_metrics].mean() - loss_df[comparison_metrics].mean()).sort_values(ascending=False)
        else:
            diff = pd.Series(dtype=float)

        # 선수 임팩트 (Top 20)
        top_players_dash = None
        if {"PLAYER_NAME", "MIN", "PTS", "PLUS_MINUS"}.issubset(self.df.columns):
            player_impact_dash = (
                self.df.groupby("PLAYER_NAME")
                .agg({"MIN": "sum", "PTS": "mean", "PLUS_MINUS": "mean"})
                .reset_index()
            )
            qualified_players_dash = player_impact_dash[player_impact_dash["MIN"] >= config.MIN_MINUTES_THRESHOLD].copy()
            if not qualified_players_dash.empty:
                top_players_dash = qualified_players_dash.nlargest(config.TOP_PLAYERS_DASHBOARD, "PTS")

        # 승/패 PLUS_MINUS 분포
        plus_df_dash = None
        if "PLUS_MINUS" in self.df.columns:
            plus_df_dash = self.df[["PLUS_MINUS"]].copy()
            plus_df_dash["결과"] = np.where(plus_df_dash["PLUS_MINUS"] > 0, "승리", "패배")
            if len(plus_df_dash) > config.MAX_ROWS_FOR_DASHBOARD:
                plus_df_dash = plus_df_dash.sample(n=config.MAX_ROWS_FOR_DASHBOARD, random_state=42)

        # Figure 레이아웃
        fig = plt.figure(figsize=(20, 10))
        gs = fig.add_gridspec(2, 3, height_ratios=[1, 1], width_ratios=[1.2, 1, 1])

        # (1) KPI 패널
        ax1 = fig.add_subplot(gs[0, 0])
        ax1.axis("off")
        ax1.set_title("리그 전체 핵심 지표 요약", fontsize=16, fontweight="bold", pad=15)

        kpi_labels_map = {
            "PTS": "평균 득점",
            "AST": "평균 어시스트",
            "REB": "평균 리바운드",
            "FG_PCT": "FG%",
            "EFG_PCT": "eFG%",
            "TS_PCT": "TS%",
            "PLUS_MINUS": "평균 PLUS_MINUS",
        }

        kpi_items = []
        for col in kpi_metrics:
            label = kpi_labels_map.get(col, col)
            val = float(kpi_summary[col]) if col in kpi_summary.index else np.nan
            if "PCT" in col:
                val = val * 100
                suffix = "%"
            else:
                suffix = ""
            kpi_items.append((label, val, suffix))

        if not np.isnan(win_rate):
            kpi_items.append(("홈 승률", win_rate, "%"))

        for i, (label, val, suffix) in enumerate(kpi_items):
            row = i // 2
            col = i % 2
            x = 0.05 + col * 0.45
            y = 0.85 - row * 0.18
            ax1.text(x, y, label, transform=ax1.transAxes, fontsize=11, color="#555555")
            ax1.text(
                x,
                y - 0.09,
                f"{val:,.1f}{suffix}" if not np.isnan(val) else "N/A",
                transform=ax1.transAxes,
                fontsize=20,
                fontweight="bold",
                color="#222222",
            )

        # (2) 팀별 PLUS_MINUS 상위 팀
        ax2 = fig.add_subplot(gs[0, 1])
        if top_teams is not None and not top_teams.empty:
            colors = sns.color_palette("Blues", n_colors=len(top_teams))[::-1]
            bars = ax2.barh(
                top_teams[team_col],
                top_teams["PLUS_MINUS"],
                color=colors,
                edgecolor="white",
                linewidth=1.2,
            )
            ax2.set_title(f"팀별 PLUS_MINUS 상위 {config.TOP_TEAMS_COUNT}팀", fontsize=14, fontweight="bold")
            ax2.set_xlabel("평균 PLUS_MINUS")
            ax2.invert_yaxis()
            ax2.grid(axis="x", alpha=0.25, color="#E0E0E0")
            for bar, val in zip(bars, top_teams["PLUS_MINUS"]):
                ax2.text(
                    val,
                    bar.get_y() + bar.get_height() / 2,
                    f"{val:.1f}",
                    va="center",
                    ha="left",
                    fontsize=9,
                    color="#333333",
                )
        else:
            ax2.axis("off")
            ax2.text(0.5, 0.5, "팀/PLUS_MINUS 정보 없음", ha="center", va="center", fontsize=12, color="#555555")

        # (3) 시즌별 평균 득점 추이
        ax3 = fig.add_subplot(gs[1, 0])
        if season_summary is not None and not season_summary.empty:
            ax3.plot(season_summary["SEASON_STR"], season_summary["PTS"], marker="o", color="tab:red", linewidth=2.5)
            ax3.set_title("시즌별 평균 득점 추이", fontsize=14, fontweight="bold")
            ax3.set_xlabel("시즌")
            ax3.set_ylabel("평균 득점")
            plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45, ha="right")
            ax3.grid(True, alpha=0.3, color="#E0E0E0")
        else:
            ax3.axis("off")
            ax3.text(0.5, 0.5, "시즌 정보 없음", ha="center", va="center", fontsize=12, color="#555555")

        # (4) 홈 승/패 지표 차이
        ax4 = fig.add_subplot(gs[1, 1])
        if not diff.empty:
            palette = sns.color_palette("Purples", n_colors=len(diff))[::-1]
            bars = ax4.barh(diff.index, diff.values, color=palette, edgecolor="white", linewidth=1.2)
            ax4.axvline(0, color="#333333", linewidth=1)
            ax4.set_title("홈 승리 vs 패배 지표 차이", fontsize=14, fontweight="bold")
            ax4.set_xlabel("승리 - 패배 (평균값 차이)")
            ax4.grid(axis="x", alpha=0.3, color="#E0E0E0")
            ax4.invert_yaxis()
            for bar, val in zip(bars, diff.values):
                ha = "left" if val > 0 else "right"
                offset = 0.01 if val > 0 else -0.01
                ax4.text(
                    val + offset,
                    bar.get_y() + bar.get_height() / 2,
                    f"{val:.2f}",
                    va="center",
                    ha=ha,
                    fontsize=8,
                    color="#222222",
                )
        else:
            ax4.axis("off")
            ax4.text(0.5, 0.5, "승/패 비교 정보 없음", ha="center", va="center", fontsize=12, color="#555555")

        # (5) 선수 득점 vs PLUS_MINUS
        ax5 = fig.add_subplot(gs[0, 2])
        if top_players_dash is not None and not top_players_dash.empty:
            ax5.scatter(
                top_players_dash["PTS"],
                top_players_dash["PLUS_MINUS"],
                c=top_players_dash["PTS"],
                cmap="Blues",
                alpha=0.7,
                edgecolors="white",
                linewidth=0.5,
            )
            ax5.set_title(
                f"Top {config.TOP_PLAYERS_DASHBOARD} 선수 득점 vs PLUS_MINUS",
                fontsize=12,
                fontweight="bold",
            )
            ax5.set_xlabel("평균 득점", fontsize=10)
            ax5.set_ylabel("평균 PLUS_MINUS", fontsize=10)
            ax5.grid(True, alpha=0.3, color="#E0E0E0")
            ax5.set_facecolor("#FFFFFF")
            for _, row in top_players_dash.nlargest(3, "PTS").iterrows():
                ax5.text(row["PTS"], row["PLUS_MINUS"], row["PLAYER_NAME"], fontsize=7, ha="left", va="bottom", color="#333333")
        else:
            ax5.axis("off")
            ax5.text(0.5, 0.5, "선수 정보 없음", ha="center", va="center", fontsize=12, color="#555555")

        # (6) 승/패 PLUS_MINUS 분포
        ax6 = fig.add_subplot(gs[1, 2])
        if plus_df_dash is not None and not plus_df_dash.empty:
            sns.kdeplot(
                data=plus_df_dash,
                x="PLUS_MINUS",
                hue="결과",
                common_norm=False,
                fill=True,
                alpha=0.4,
                palette={"승리": "#B5E5CF", "패배": "#FFB6C1"},
                ax=ax6,
            )
            ax6.set_title("승리 vs 패배 PLUS_MINUS 분포", fontsize=12, fontweight="bold")
            ax6.set_xlabel("PLUS_MINUS", fontsize=10)
            ax6.set_ylabel("밀도", fontsize=10)
            ax6.grid(True, alpha=0.3, color="#E0E0E0")
            ax6.set_facecolor("#FFFFFF")
        else:
            ax6.axis("off")
            ax6.text(0.5, 0.5, "PLUS_MINUS 정보 없음", ha="center", va="center", fontsize=12, color="#555555")

        plt.suptitle("NBA 핵심 인사이트 종합 대시보드", fontsize=18, fontweight="bold", y=0.98)
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        self._save_figure(fig, "NBA_05_종합_대시보드.png")
        print("[OK] 완료")

    def visualize_ml_results(self):
        """머신러닝 결과 시각화"""
        print("\n" + "=" * 60)
        print("머신러닝 결과 시각화")
        print("=" * 60)
        
        try:
            import pickle
            ml_results_dir = os.path.join(config.OUTPUT_DIR, 'NBA_머신러닝_결과')
            
            # 머신러닝 결과 파일 확인
            if not os.path.exists(ml_results_dir):
                print("[WARN] 머신러닝 결과 디렉토리가 없습니다.")
                print("  먼저 NBA_머신러닝_모듈.py를 실행하거나 통합 파이프라인을 실행하세요.")
                return
            
            results_files = os.listdir(ml_results_dir)
            if not results_files:
                print("[WARN] 머신러닝 결과 파일이 없습니다.")
                return
            
            # 결과 파일 로드
            results = {}
            if 'win_loss_results.pkl' in results_files:
                with open(os.path.join(ml_results_dir, 'win_loss_results.pkl'), 'rb') as f:
                    results['win_loss'] = pickle.load(f)
            
            for target in ['PLUS_MINUS', 'PTS']:
                filename = f'player_{target}_results.pkl'
                if filename in results_files:
                    with open(os.path.join(ml_results_dir, filename), 'rb') as f:
                        results[f'player_{target}'] = pickle.load(f)
            
            if 'player_clustering.csv' in results_files:
                clustering_df = pd.read_csv(os.path.join(ml_results_dir, 'player_clustering.csv'))
                # 클러스터링 결과 재구성
                n_clusters = clustering_df['Cluster'].nunique()
                cluster_summary = clustering_df.groupby('Cluster').agg({
                    'PTS': 'mean', 'AST': 'mean', 'REB': 'mean',
                    'STL': 'mean', 'BLK': 'mean', 'EFG_PCT': 'mean', 'TS_PCT': 'mean'
                })
                results['clustering'] = {
                    'player_stats': clustering_df,
                    'cluster_summary': cluster_summary,
                    'cluster_counts': clustering_df['Cluster'].value_counts().sort_index(),
                    'n_clusters': n_clusters
                }
            
            # 1. 승/패 예측 모델 성능 시각화
            if 'win_loss' in results:
                self._visualize_win_loss_model(results['win_loss'])
            
            # 2. 선수 성과 예측 모델 시각화
            for target in ['PLUS_MINUS', 'PTS']:
                key = f'player_{target}'
                if key in results:
                    self._visualize_performance_model(results[key], target)
            
            # 3. 클러스터링 결과 시각화
            if 'clustering' in results:
                self._visualize_clustering(results['clustering'])
            
            print("\n[OK] 머신러닝 결과 시각화 완료!")
            
        except Exception as e:
            print(f"[WARN] 머신러닝 결과 시각화 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()
    
    def visualize_statistical_tests(self):
        """통계 검정 결과 시각화"""
        print("\n" + "=" * 60)
        print("통계 검정 결과 시각화")
        print("=" * 60)
        
        try:
            import pandas as pd
            stat_results_dir = os.path.join(config.OUTPUT_DIR, 'NBA_통계검정_결과')
            
            if not os.path.exists(stat_results_dir):
                print("[WARN] 통계 검정 결과 디렉토리가 없습니다.")
                print("  먼저 NBA_통계검정_모듈.py를 실행하거나 통합 파이프라인을 실행하세요.")
                return
            
            # 승/패 검정 결과 로드
            win_loss_file = os.path.join(stat_results_dir, 'win_loss_statistical_test.csv')
            if os.path.exists(win_loss_file):
                win_loss_df = pd.read_csv(win_loss_file)
                self._visualize_win_loss_statistics(win_loss_df)
            
            # 클러스터링 검정 결과 로드
            clustering_file = os.path.join(stat_results_dir, 'clustering_statistical_test.csv')
            if os.path.exists(clustering_file):
                clustering_df = pd.read_csv(clustering_file)
                self._visualize_clustering_statistics(clustering_df)
            
            print("\n[OK] 통계 검정 결과 시각화 완료!")
            
        except Exception as e:
            print(f"[WARN] 통계 검정 결과 시각화 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()
    
    def _visualize_win_loss_statistics(self, results_df):
        """승/패 통계 검정 결과 시각화"""
        print("\n[승/패 통계 검정 결과 시각화]")
        
        # 유의한 결과만 필터링
        significant = results_df[results_df['significant']].head(10)
        
        if len(significant) == 0:
            print("[WARN] 유의한 결과가 없습니다.")
            return
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        # (1) p-value 막대그래프
        axes[0].barh(range(len(significant)), -np.log10(significant['p_value'].values), 
                     color='steelblue', alpha=0.7)
        axes[0].axvline(-np.log10(0.05), color='red', linestyle='--', linewidth=2, 
                       label='p=0.05 기준선')
        axes[0].set_yticks(range(len(significant)))
        axes[0].set_yticklabels(significant['metric'].values)
        axes[0].set_xlabel('-log10(p-value)', fontsize=10)
        axes[0].set_title('승/패 그룹 간 차이 검정 (p-value)', fontsize=12, fontweight='bold')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3, axis='x')
        axes[0].invert_yaxis()
        
        # (2) 효과 크기 (Cohen's d)
        colors = ['green' if d > 0 else 'red' for d in significant['cohens_d'].values]
        axes[1].barh(range(len(significant)), significant['cohens_d'].values, 
                     color=colors, alpha=0.7)
        axes[1].axvline(0, color='black', linestyle='-', linewidth=1)
        axes[1].axvline(0.2, color='orange', linestyle='--', linewidth=1, alpha=0.5)
        axes[1].axvline(0.8, color='orange', linestyle='--', linewidth=1, alpha=0.5)
        axes[1].set_yticks(range(len(significant)))
        axes[1].set_yticklabels(significant['metric'].values)
        axes[1].set_xlabel("Cohen's d (효과 크기)", fontsize=10)
        axes[1].set_title('효과 크기 (Cohen\'s d)', fontsize=12, fontweight='bold')
        axes[1].grid(True, alpha=0.3, axis='x')
        axes[1].invert_yaxis()
        
        plt.tight_layout()
        self._save_figure(fig, "NBA_09_승패_통계검정_결과.png")
        print("[OK] 완료")
    
    def _visualize_clustering_statistics(self, results_df):
        """클러스터링 통계 검정 결과 시각화"""
        print("\n[클러스터링 통계 검정 결과 시각화]")
        
        # 유의한 결과만 필터링
        significant = results_df[results_df['significant']]
        
        if len(significant) == 0:
            print("[WARN] 유의한 결과가 없습니다.")
            return
        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # p-value 막대그래프
        ax.barh(range(len(significant)), -np.log10(significant['p_value'].values), 
               color='coral', alpha=0.7)
        ax.axvline(-np.log10(0.05), color='red', linestyle='--', linewidth=2, 
                  label='p=0.05 기준선')
        ax.set_yticks(range(len(significant)))
        ax.set_yticklabels(significant['metric'].values)
        ax.set_xlabel('-log10(p-value)', fontsize=10)
        ax.set_title('클러스터 간 차이 검정 (p-value)', fontsize=12, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='x')
        ax.invert_yaxis()
        
        plt.tight_layout()
        self._save_figure(fig, "NBA_10_클러스터링_통계검정_결과.png")
        print("[OK] 완료")
    
    def _visualize_win_loss_model(self, results):
        """승/패 예측 모델 결과 시각화"""
        print("\n[승/패 예측 모델 시각화]")
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # (1) 혼동 행렬
        cm = results['confusion_matrix']
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes[0],
                   xticklabels=['패배', '승리'], yticklabels=['패배', '승리'])
        axes[0].set_title(f'혼동 행렬\n(정확도: {results["accuracy"]:.3f})', 
                         fontsize=12, fontweight='bold')
        axes[0].set_ylabel('실제', fontsize=10)
        axes[0].set_xlabel('예측', fontsize=10)
        
        # (2) 특성 중요도
        top_features = results['feature_importance'].head(10)
        axes[1].barh(range(len(top_features)), top_features['importance'].values, color='steelblue')
        axes[1].set_yticks(range(len(top_features)))
        axes[1].set_yticklabels(top_features['feature'].values)
        axes[1].set_xlabel('중요도', fontsize=10)
        axes[1].set_title('특성 중요도 Top 10', fontsize=12, fontweight='bold')
        axes[1].invert_yaxis()
        axes[1].grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        self._save_figure(fig, "NBA_06_승패예측_모델_성능.png")
        print("[OK] 완료")
    
    def _visualize_performance_model(self, results, target):
        """선수 성과 예측 모델 결과 시각화"""
        print(f"\n[선수 {target} 예측 모델 시각화]")
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # (1) 실제 vs 예측 산점도
        y_test = results['y_test']
        y_pred = results['y_pred']
        
        axes[0].scatter(y_test, y_pred, alpha=0.5, s=20, color='steelblue')
        min_val = min(y_test.min(), y_pred.min())
        max_val = max(y_test.max(), y_pred.max())
        axes[0].plot([min_val, max_val], [min_val, max_val], 'r--', lw=2, label='완벽한 예측')
        axes[0].set_xlabel(f'실제 {target}', fontsize=10)
        axes[0].set_ylabel(f'예측 {target}', fontsize=10)
        axes[0].set_title(f'실제 vs 예측\n(R²: {results["r2"]:.3f}, RMSE: {results["rmse"]:.2f})',
                         fontsize=12, fontweight='bold')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # (2) 특성 중요도
        top_features = results['feature_importance'].head(10)
        axes[1].barh(range(len(top_features)), top_features['importance'].values, color='coral')
        axes[1].set_yticks(range(len(top_features)))
        axes[1].set_yticklabels(top_features['feature'].values)
        axes[1].set_xlabel('중요도', fontsize=10)
        axes[1].set_title(f'{target} 예측 특성 중요도 Top 10', fontsize=12, fontweight='bold')
        axes[1].invert_yaxis()
        axes[1].grid(True, alpha=0.3, axis='x')
        
        plt.tight_layout()
        self._save_figure(fig, f"NBA_07_선수{target}예측_모델_성능.png")
        print("[OK] 완료")
    
    def _visualize_clustering(self, results):
        """클러스터링 결과 시각화"""
        print("\n[선수 클러스터링 결과 시각화]")
        
        player_stats = results['player_stats']
        n_clusters = results['n_clusters']
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # (1) 클러스터별 선수 수
        cluster_counts = results['cluster_counts']
        axes[0, 0].bar(range(n_clusters), cluster_counts.values, color='steelblue', alpha=0.7)
        axes[0, 0].set_xlabel('클러스터', fontsize=10)
        axes[0, 0].set_ylabel('선수 수', fontsize=10)
        axes[0, 0].set_title('클러스터별 선수 수', fontsize=12, fontweight='bold')
        axes[0, 0].set_xticks(range(n_clusters))
        axes[0, 0].grid(True, alpha=0.3, axis='y')
        
        # (2) 클러스터별 평균 득점 vs 어시스트
        for cluster_id in range(n_clusters):
            cluster_data = player_stats[player_stats['Cluster'] == cluster_id]
            axes[0, 1].scatter(cluster_data['PTS'].mean(), cluster_data['AST'].mean(),
                            s=200, alpha=0.7, label=f'클러스터 {cluster_id}')
        axes[0, 1].set_xlabel('평균 득점', fontsize=10)
        axes[0, 1].set_ylabel('평균 어시스트', fontsize=10)
        axes[0, 1].set_title('클러스터별 평균 득점 vs 어시스트', fontsize=12, fontweight='bold')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        
        # (3) 클러스터별 주요 지표 비교
        cluster_summary = results['cluster_summary']
        metrics = ['PTS', 'AST', 'REB', 'STL', 'BLK']
        metrics = [m for m in metrics if m in cluster_summary.columns]
        
        x = np.arange(len(metrics))
        width = 0.15
        colors = plt.cm.Set3(np.linspace(0, 1, n_clusters))
        
        for i in range(n_clusters):
            values = [cluster_summary.loc[i, m] for m in metrics]
            axes[1, 0].bar(x + i * width, values, width, label=f'클러스터 {i}', color=colors[i])
        
        axes[1, 0].set_xlabel('지표', fontsize=10)
        axes[1, 0].set_ylabel('평균값', fontsize=10)
        axes[1, 0].set_title('클러스터별 주요 지표 비교', fontsize=12, fontweight='bold')
        axes[1, 0].set_xticks(x + width * (n_clusters - 1) / 2)
        axes[1, 0].set_xticklabels(metrics)
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3, axis='y')
        
        # (4) 클러스터별 효율성 (EFG_PCT vs TS_PCT)
        for cluster_id in range(n_clusters):
            cluster_data = player_stats[player_stats['Cluster'] == cluster_id]
            axes[1, 1].scatter(cluster_data['EFG_PCT'].mean(), cluster_data['TS_PCT'].mean(),
                            s=200, alpha=0.7, label=f'클러스터 {cluster_id}')
        axes[1, 1].set_xlabel('평균 EFG%', fontsize=10)
        axes[1, 1].set_ylabel('평균 TS%', fontsize=10)
        axes[1, 1].set_title('클러스터별 슛 효율성', fontsize=12, fontweight='bold')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        self._save_figure(fig, "NBA_08_선수_클러스터링_결과.png")
        print("[OK] 완료")

    def visualize_all(self):
        """모든 시각화 생성"""
        if self.df is None:
            self.load_data()

        print("\n" + "=" * 60)
        print("시각화 생성 시작")
        print("=" * 60)

        self.visualize_correlation_heatmap()
        self.visualize_top_players()
        self.visualize_seasonal_trends()
        self.visualize_win_loss_comparison()
        self.visualize_dashboard()
        
        # 통계 검정 결과 시각화 (검정이 수행된 경우)
        self.visualize_statistical_tests()
        
        # 머신러닝 결과 시각화 (모델이 학습된 경우)
        self.visualize_ml_results()

        print("\n" + "=" * 60)
        print("모든 시각화 생성 완료!")
        print(f"결과 저장 위치: {self.output_dir}")
        print("=" * 60)


if __name__ == "__main__":
    visualizer = NBADataVisualizer()
    visualizer.visualize_all()


