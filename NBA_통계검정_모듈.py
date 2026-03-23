"""
NBA 데이터 통계 검정 모듈

이 모듈은 NBA 데이터에 대한 통계 검정을 수행합니다.
- 승/패 그룹 간 지표 차이 검정
- 클러스터 간 차이 검정
- 효과 크기 계산
"""

import os
import warnings
from typing import Optional, Dict, List, Tuple
import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import (
    ttest_ind, mannwhitneyu, f_oneway, kruskal,
    shapiro, normaltest, levene
)
import matplotlib.pyplot as plt
import seaborn as sns

import NBA_설정 as config

warnings.filterwarnings("ignore")


class NBAStatisticalTest:
    """
    NBA 데이터 통계 검정 클래스
    
    주요 기능:
    - 승/패 그룹 간 지표 차이 검정
    - 클러스터 간 차이 검정
    - 효과 크기 계산
    - 정규성 검정
    """
    
    def __init__(self, base_dir: Optional[str] = None):
        """
        초기화
        
        Args:
            base_dir: 작업 디렉토리 경로 (None이면 config에서 가져옴)
        """
        self.base_dir = base_dir or config.BASE_DIR
        self.df: Optional[pd.DataFrame] = None
        self.results: Dict = {}
        
        # 결과 저장 경로
        self.results_dir = os.path.join(config.OUTPUT_DIR, 'NBA_통계검정_결과')
        os.makedirs(self.results_dir, exist_ok=True)
    
    def load_data(self):
        """전처리된 데이터 로드"""
        print("\n" + "=" * 60)
        print("통계 검정용 데이터 로드")
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
    
    def check_normality(self, data: pd.Series, alpha: float = 0.05) -> Dict:
        """
        정규성 검정
        
        Args:
            data: 검정할 데이터
            alpha: 유의수준
            
        Returns:
            검정 결과 딕셔너리
        """
        # Shapiro-Wilk 검정 (샘플 크기가 작을 때)
        if len(data) <= 5000:
            stat_sw, p_sw = shapiro(data.dropna())
            test_name_sw = "Shapiro-Wilk"
        else:
            # 샘플이 크면 D'Agostino's normality test 사용
            stat_sw, p_sw = normaltest(data.dropna())
            test_name_sw = "D'Agostino"
        
        is_normal = p_sw > alpha
        
        return {
            'test_name': test_name_sw,
            'statistic': stat_sw,
            'p_value': p_sw,
            'is_normal': is_normal,
            'alpha': alpha
        }
    
    def calculate_effect_size(self, group1: pd.Series, group2: pd.Series) -> Dict:
        """
        효과 크기 계산 (Cohen's d)
        
        Args:
            group1: 첫 번째 그룹
            group2: 두 번째 그룹
            
        Returns:
            효과 크기 정보
        """
        n1, n2 = len(group1), len(group2)
        mean1, mean2 = group1.mean(), group2.mean()
        std1, std2 = group1.std(ddof=1), group2.std(ddof=1)
        
        # Pooled standard deviation
        pooled_std = np.sqrt(((n1 - 1) * std1**2 + (n2 - 1) * std2**2) / (n1 + n2 - 2))
        
        # Cohen's d
        cohens_d = (mean1 - mean2) / pooled_std if pooled_std > 0 else 0
        
        # 효과 크기 해석
        if abs(cohens_d) < 0.2:
            effect_size = "negligible"
        elif abs(cohens_d) < 0.5:
            effect_size = "small"
        elif abs(cohens_d) < 0.8:
            effect_size = "medium"
        else:
            effect_size = "large"
        
        return {
            'cohens_d': cohens_d,
            'effect_size': effect_size,
            'mean_diff': mean1 - mean2,
            'mean1': mean1,
            'mean2': mean2,
            'std1': std1,
            'std2': std2
        }
    
    def test_win_loss_difference(self, metrics: Optional[List[str]] = None, 
                                 alpha: float = 0.05) -> pd.DataFrame:
        """
        승/패 그룹 간 지표 차이 검정
        
        Args:
            metrics: 검정할 지표 리스트 (None이면 config.COMPARISON_METRICS 사용)
            alpha: 유의수준
            
        Returns:
            검정 결과 DataFrame
        """
        print("\n" + "=" * 60)
        print("승/패 그룹 간 지표 차이 검정")
        print("=" * 60)
        
        if metrics is None:
            metrics = [m for m in config.COMPARISON_METRICS if m in self.df.columns]
        
        # 홈팀 데이터만 사용
        home_df = self.df[self.df['HOME_TEAM_ID'] == self.df['TEAM_ID']].copy()
        
        # 승/패 그룹 분리
        win_group = home_df[home_df['PLUS_MINUS'] > 0]
        loss_group = home_df[home_df['PLUS_MINUS'] <= 0]
        
        print(f"\n승리 그룹: {len(win_group):,}행")
        print(f"패배 그룹: {len(loss_group):,}행")
        
        results = []
        
        for metric in metrics:
            if metric not in home_df.columns:
                continue
            
            win_data = win_group[metric].dropna()
            loss_data = loss_group[metric].dropna()
            
            if len(win_data) == 0 or len(loss_data) == 0:
                continue
            
            # 정규성 검정
            norm_win = self.check_normality(win_data, alpha)
            norm_loss = self.check_normality(loss_data, alpha)
            
            # 등분산성 검정 (Levene's test)
            levene_stat, levene_p = levene(win_data, loss_data)
            equal_var = levene_p > alpha
            
            # t-test 또는 Mann-Whitney U 검정
            if norm_win['is_normal'] and norm_loss['is_normal']:
                # 정규성 충족 → t-test
                t_stat, p_value = ttest_ind(win_data, loss_data, equal_var=equal_var)
                test_name = "t-test"
                test_stat = t_stat
            else:
                # 정규성 미충족 → Mann-Whitney U
                u_stat, p_value = mannwhitneyu(win_data, loss_data, alternative='two-sided')
                test_name = "Mann-Whitney U"
                test_stat = u_stat
            
            # 효과 크기
            effect = self.calculate_effect_size(win_data, loss_data)
            
            # 결과 저장
            results.append({
                'metric': metric,
                'test_name': test_name,
                'test_statistic': test_stat,
                'p_value': p_value,
                'significant': p_value < alpha,
                'win_mean': win_data.mean(),
                'loss_mean': loss_data.mean(),
                'mean_diff': win_data.mean() - loss_data.mean(),
                'cohens_d': effect['cohens_d'],
                'effect_size': effect['effect_size'],
                'win_normality': norm_win['is_normal'],
                'loss_normality': norm_loss['is_normal'],
                'equal_variance': equal_var
            })
        
        results_df = pd.DataFrame(results)
        results_df = results_df.sort_values('p_value')
        
        print("\n[검정 결과]")
        print(results_df.to_string(index=False))
        
        # 유의한 결과 요약
        significant = results_df[results_df['significant']]
        if len(significant) > 0:
            print(f"\n✓ {len(significant)}개 지표에서 유의한 차이 발견 (p < {alpha})")
            print("\n[유의한 지표 Top 5]")
            print(significant.head(5)[['metric', 'test_name', 'p_value', 'cohens_d', 'effect_size']].to_string(index=False))
        else:
            print(f"\n⚠ 유의한 차이를 발견한 지표가 없습니다.")
        
        self.results['win_loss'] = results_df
        
        # 결과 저장
        result_path = os.path.join(self.results_dir, 'win_loss_statistical_test.csv')
        results_df.to_csv(result_path, index=False, encoding='utf-8')
        print(f"\n✓ 결과 저장 완료: {result_path}")
        
        return results_df
    
    def test_cluster_difference(self, n_clusters: int = 5, 
                                metrics: Optional[List[str]] = None,
                                alpha: float = 0.05) -> pd.DataFrame:
        """
        클러스터 간 지표 차이 검정
        
        Args:
            n_clusters: 클러스터 개수
            metrics: 검정할 지표 리스트
            alpha: 유의수준
            
        Returns:
            검정 결과 DataFrame
        """
        print("\n" + "=" * 60)
        print("클러스터 간 지표 차이 검정")
        print("=" * 60)
        
        # 클러스터링 결과 로드
        clustering_file = os.path.join(config.OUTPUT_DIR, 'NBA_머신러닝_결과', 'player_clustering.csv')
        if not os.path.exists(clustering_file):
            print("⚠ 클러스터링 결과 파일이 없습니다. 먼저 클러스터링을 실행하세요.")
            return pd.DataFrame()
        
        cluster_df = pd.read_csv(clustering_file)
        
        if metrics is None:
            metrics = ['PTS', 'AST', 'REB', 'STL', 'BLK', 'EFG_PCT', 'TS_PCT', 'PPM']
            metrics = [m for m in metrics if m in cluster_df.columns]
        
        results = []
        
        for metric in metrics:
            if metric not in cluster_df.columns:
                continue
            
            # 클러스터별 데이터
            cluster_data = [cluster_df[cluster_df['Cluster'] == i][metric].dropna() 
                          for i in range(n_clusters)]
            cluster_data = [data for data in cluster_data if len(data) > 0]
            
            if len(cluster_data) < 2:
                continue
            
            # 정규성 검정 (각 클러스터)
            normality_results = [self.check_normality(data, alpha) for data in cluster_data]
            all_normal = all([r['is_normal'] for r in normality_results])
            
            # ANOVA 또는 Kruskal-Wallis
            if all_normal:
                # 정규성 충족 → ANOVA
                f_stat, p_value = f_oneway(*cluster_data)
                test_name = "ANOVA"
                test_stat = f_stat
            else:
                # 정규성 미충족 → Kruskal-Wallis
                h_stat, p_value = kruskal(*cluster_data)
                test_name = "Kruskal-Wallis"
                test_stat = h_stat
            
            # 클러스터별 평균
            cluster_means = [data.mean() for data in cluster_data]
            cluster_stds = [data.std() for data in cluster_data]
            
            results.append({
                'metric': metric,
                'test_name': test_name,
                'test_statistic': test_stat,
                'p_value': p_value,
                'significant': p_value < alpha,
                'cluster_means': cluster_means,
                'cluster_stds': cluster_stds,
                'all_normal': all_normal
            })
        
        results_df = pd.DataFrame(results)
        results_df = results_df.sort_values('p_value')
        
        print("\n[검정 결과]")
        print(results_df[['metric', 'test_name', 'test_statistic', 'p_value', 'significant']].to_string(index=False))
        
        # 유의한 결과 요약
        significant = results_df[results_df['significant']]
        if len(significant) > 0:
            print(f"\n✓ {len(significant)}개 지표에서 클러스터 간 유의한 차이 발견 (p < {alpha})")
        else:
            print(f"\n⚠ 클러스터 간 유의한 차이를 발견한 지표가 없습니다.")
        
        self.results['clustering'] = results_df
        
        # 결과 저장
        result_path = os.path.join(self.results_dir, 'clustering_statistical_test.csv')
        results_df.to_csv(result_path, index=False, encoding='utf-8')
        print(f"\n✓ 결과 저장 완료: {result_path}")
        
        return results_df
    
    def perform_all_tests(self):
        """모든 통계 검정 수행"""
        if self.df is None:
            self.load_data()
        
        # 승/패 그룹 간 차이 검정
        self.test_win_loss_difference()
        
        # 클러스터 간 차이 검정
        self.test_cluster_difference()
        
        print("\n" + "=" * 60)
        print("모든 통계 검정 완료!")
        print("=" * 60)


if __name__ == "__main__":
    # 직접 실행 시 모든 통계 검정 수행
    stat_test = NBAStatisticalTest()
    stat_test.perform_all_tests()

