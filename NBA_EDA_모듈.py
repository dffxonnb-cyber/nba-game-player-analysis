"""
NBA 데이터 탐색적 데이터 분석 (EDA) 모듈

이 모듈은 NBA 데이터에 대한 심화 EDA를 수행합니다.
- 분포 분석
- 이상치 탐지
- 다변량 분석
"""

import os
import warnings
from typing import Optional, Dict, List
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

import NBA_설정 as config

warnings.filterwarnings("ignore")


class NBAEDA:
    """
    NBA 데이터 EDA 클래스
    
    주요 기능:
    - 분포 분석
    - 이상치 탐지
    - 다변량 분석
    """
    
    def __init__(self, base_dir: Optional[str] = None):
        """
        초기화
        
        Args:
            base_dir: 작업 디렉토리 경로 (None이면 config에서 가져옴)
        """
        self.base_dir = base_dir or config.BASE_DIR
        self.df: Optional[pd.DataFrame] = None
        self.output_dir = os.path.join(config.OUTPUT_DIR, 'NBA_EDA_결과')
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 한글 폰트 설정
        self._setup_korean_font()
    
    def _setup_korean_font(self):
        """한글 폰트 설정"""
        import platform
        if platform.system() == "Windows":
            plt.rcParams["font.family"] = "Malgun Gothic"
        elif platform.system() == "Darwin":
            plt.rcParams["font.family"] = "AppleGothic"
        else:
            plt.rcParams["font.family"] = "NanumGothic"
        plt.rcParams["axes.unicode_minus"] = False
        sns.set_style("whitegrid")
    
    def load_data(self):
        """전처리된 데이터 로드"""
        print("\n" + "=" * 60)
        print("EDA용 데이터 로드")
        print("=" * 60)
        
        if os.path.exists(config.MERGED_PKL):
            self.df = pd.read_pickle(config.MERGED_PKL)
            print(f"✓ PKL 파일 로드 완료: {self.df.shape}")
        elif os.path.exists(config.FINAL_CSV):
            self.df = pd.read_csv(config.FINAL_CSV)
            if "GAME_DATE_EST" in self.df.columns:
                self.df["GAME_DATE_EST"] = pd.to_datetime(self.df["GAME_DATE_EST"])
            print(f"✓ CSV 파일 로드 완료: {self.df.shape}")
        else:
            raise FileNotFoundError(
                "전처리된 데이터 파일을 찾을 수 없습니다. "
                "먼저 전처리를 실행해주세요."
            )
    
    def analyze_distribution(self, metrics: Optional[List[str]] = None):
        """
        지표별 분포 분석
        
        Args:
            metrics: 분석할 지표 리스트
        """
        print("\n" + "=" * 60)
        print("지표별 분포 분석")
        print("=" * 60)
        
        if metrics is None:
            metrics = ['PTS', 'AST', 'REB', 'FG_PCT', 'PLUS_MINUS', 'EFG_PCT', 'TS_PCT']
            metrics = [m for m in metrics if m in self.df.columns]
        
        n_metrics = len(metrics)
        n_cols = 3
        n_rows = (n_metrics + n_cols - 1) // n_cols
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 5 * n_rows))
        axes = axes.flatten() if n_metrics > 1 else [axes]
        
        for idx, metric in enumerate(metrics):
            if metric not in self.df.columns:
                continue
            
            ax = axes[idx]
            data = self.df[metric].dropna()
            
            # 히스토그램
            ax.hist(data, bins=50, alpha=0.7, color='steelblue', edgecolor='black')
            ax.axvline(data.mean(), color='red', linestyle='--', linewidth=2, label=f'평균: {data.mean():.2f}')
            ax.axvline(data.median(), color='green', linestyle='--', linewidth=2, label=f'중앙값: {data.median():.2f}')
            
            ax.set_title(f'{metric} 분포', fontsize=12, fontweight='bold')
            ax.set_xlabel(metric, fontsize=10)
            ax.set_ylabel('빈도', fontsize=10)
            ax.legend()
            ax.grid(True, alpha=0.3)
        
        # 빈 subplot 제거
        for idx in range(n_metrics, len(axes)):
            axes[idx].axis('off')
        
        plt.tight_layout()
        output_path = os.path.join(self.output_dir, '지표별_분포_분석.png')
        plt.savefig(output_path, dpi=config.DPI, bbox_inches='tight')
        print(f"✓ 분포 분석 저장: {output_path}")
        plt.close()
    
    def detect_outliers(self, metrics: Optional[List[str]] = None, method: str = 'iqr'):
        """
        이상치 탐지
        
        Args:
            metrics: 분석할 지표 리스트
            method: 이상치 탐지 방법 ('iqr' 또는 'zscore')
        """
        print("\n" + "=" * 60)
        print("이상치 탐지")
        print("=" * 60)
        
        if metrics is None:
            metrics = ['PTS', 'AST', 'REB', 'MIN', 'PLUS_MINUS']
            metrics = [m for m in metrics if m in self.df.columns]
        
        outlier_summary = []
        
        for metric in metrics:
            if metric not in self.df.columns:
                continue
            
            data = self.df[metric].dropna()
            
            if method == 'iqr':
                Q1 = data.quantile(0.25)
                Q3 = data.quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                outliers = data[(data < lower_bound) | (data > upper_bound)]
            else:  # zscore
                z_scores = np.abs(stats.zscore(data))
                outliers = data[z_scores > 3]
            
            outlier_summary.append({
                'metric': metric,
                'total_count': len(data),
                'outlier_count': len(outliers),
                'outlier_percentage': len(outliers) / len(data) * 100,
                'lower_bound': lower_bound if method == 'iqr' else data.mean() - 3 * data.std(),
                'upper_bound': upper_bound if method == 'iqr' else data.mean() + 3 * data.std()
            })
        
        summary_df = pd.DataFrame(outlier_summary)
        print("\n[이상치 요약]")
        print(summary_df.to_string(index=False))
        
        # 박스플롯으로 시각화
        n_metrics = len(metrics)
        n_cols = 3
        n_rows = (n_metrics + n_cols - 1) // n_cols
        
        fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 5 * n_rows))
        axes = axes.flatten() if n_metrics > 1 else [axes]
        
        for idx, metric in enumerate(metrics):
            if metric not in self.df.columns:
                continue
            
            ax = axes[idx]
            data = self.df[metric].dropna()
            
            bp = ax.boxplot(data, vert=True, patch_artist=True)
            bp['boxes'][0].set_facecolor('lightblue')
            
            ax.set_title(f'{metric} 박스플롯 (이상치 탐지)', fontsize=12, fontweight='bold')
            ax.set_ylabel(metric, fontsize=10)
            ax.grid(True, alpha=0.3, axis='y')
        
        # 빈 subplot 제거
        for idx in range(n_metrics, len(axes)):
            axes[idx].axis('off')
        
        plt.tight_layout()
        output_path = os.path.join(self.output_dir, '이상치_탐지_박스플롯.png')
        plt.savefig(output_path, dpi=config.DPI, bbox_inches='tight')
        print(f"✓ 이상치 탐지 결과 저장: {output_path}")
        plt.close()
        
        # 요약 저장
        summary_path = os.path.join(self.output_dir, '이상치_요약.csv')
        summary_df.to_csv(summary_path, index=False, encoding='utf-8')
        print(f"✓ 이상치 요약 저장: {summary_path}")
    
    def analyze_multivariate(self, x_metric: str, y_metric: str, 
                            hue_metric: Optional[str] = None):
        """
        다변량 분석
        
        Args:
            x_metric: X축 지표
            y_metric: Y축 지표
            hue_metric: 색상 구분 지표 (선택)
        """
        print("\n" + "=" * 60)
        print(f"다변량 분석: {x_metric} vs {y_metric}")
        print("=" * 60)
        
        if x_metric not in self.df.columns or y_metric not in self.df.columns:
            print("⚠ 지정한 지표가 데이터에 없습니다.")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 12))
        
        # 데이터 준비
        plot_df = self.df[[x_metric, y_metric]].dropna()
        if hue_metric and hue_metric in self.df.columns:
            plot_df[hue_metric] = self.df[hue_metric]
            plot_df = plot_df.dropna()
        
        # 1. 산점도
        if hue_metric and hue_metric in plot_df.columns:
            sns.scatterplot(data=plot_df, x=x_metric, y=y_metric, 
                          hue=hue_metric, alpha=0.6, ax=axes[0, 0])
        else:
            axes[0, 0].scatter(plot_df[x_metric], plot_df[y_metric], alpha=0.5, s=10)
        axes[0, 0].set_title(f'{x_metric} vs {y_metric} 산점도', fontsize=12, fontweight='bold')
        axes[0, 0].set_xlabel(x_metric, fontsize=10)
        axes[0, 0].set_ylabel(y_metric, fontsize=10)
        axes[0, 0].grid(True, alpha=0.3)
        
        # 2. 상관관계
        corr = plot_df[x_metric].corr(plot_df[y_metric])
        axes[0, 1].text(0.5, 0.5, f'상관계수: {corr:.3f}', 
                       ha='center', va='center', fontsize=14, fontweight='bold')
        axes[0, 1].set_title('피어슨 상관계수', fontsize=12, fontweight='bold')
        axes[0, 1].axis('off')
        
        # 3. X축 지표 분포
        axes[1, 0].hist(plot_df[x_metric], bins=50, alpha=0.7, color='steelblue', edgecolor='black')
        axes[1, 0].set_title(f'{x_metric} 분포', fontsize=12, fontweight='bold')
        axes[1, 0].set_xlabel(x_metric, fontsize=10)
        axes[1, 0].set_ylabel('빈도', fontsize=10)
        axes[1, 0].grid(True, alpha=0.3)
        
        # 4. Y축 지표 분포
        axes[1, 1].hist(plot_df[y_metric], bins=50, alpha=0.7, color='coral', edgecolor='black')
        axes[1, 1].set_title(f'{y_metric} 분포', fontsize=12, fontweight='bold')
        axes[1, 1].set_xlabel(y_metric, fontsize=10)
        axes[1, 1].set_ylabel('빈도', fontsize=10)
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        output_path = os.path.join(self.output_dir, f'다변량분석_{x_metric}_vs_{y_metric}.png')
        plt.savefig(output_path, dpi=config.DPI, bbox_inches='tight')
        print(f"✓ 다변량 분석 저장: {output_path}")
        print(f"  상관계수: {corr:.3f}")
        plt.close()
    
    def perform_all_eda(self):
        """모든 EDA 수행"""
        if self.df is None:
            self.load_data()
        
        # 분포 분석
        self.analyze_distribution()
        
        # 이상치 탐지
        self.detect_outliers()
        
        # 주요 다변량 분석
        self.analyze_multivariate('PTS', 'PLUS_MINUS')
        self.analyze_multivariate('AST', 'PLUS_MINUS')
        self.analyze_multivariate('EFG_PCT', 'TS_PCT')
        
        print("\n" + "=" * 60)
        print("모든 EDA 완료!")
        print("=" * 60)


if __name__ == "__main__":
    # 직접 실행 시 모든 EDA 수행
    eda = NBAEDA()
    eda.perform_all_eda()

