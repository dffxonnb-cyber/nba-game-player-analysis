"""
NBA 데이터 머신러닝 모듈

이 모듈은 NBA 경기 데이터를 활용한 머신러닝 모델을 제공합니다.
- 경기 승/패 예측 (분류)
- 선수 성과 예측 (회귀)
- 선수 클러스터링
"""

import os
import pickle
import warnings
from typing import Optional, Tuple, Dict, List
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import (
    accuracy_score, classification_report, confusion_matrix,
    mean_squared_error, r2_score, mean_absolute_error
)
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns

import NBA_설정 as config

warnings.filterwarnings("ignore")


class NBAMachineLearning:
    """
    NBA 데이터 머신러닝 클래스
    
    주요 기능:
    - 경기 승/패 예측 (분류)
    - 선수 성과 예측 (회귀)
    - 선수 클러스터링
    """
    
    def __init__(self, base_dir: Optional[str] = None):
        """
        초기화
        
        Args:
            base_dir: 작업 디렉토리 경로 (None이면 config에서 가져옴)
        """
        self.base_dir = base_dir or config.BASE_DIR
        self.df: Optional[pd.DataFrame] = None
        self.models: Dict = {}
        self.scalers: Dict = {}
        self.label_encoders: Dict = {}
        self.results: Dict = {}
        
        # 모델 저장 경로
        self.models_dir = os.path.join(config.OUTPUT_DIR, 'NBA_머신러닝_모델')
        os.makedirs(self.models_dir, exist_ok=True)
        
        # 결과 저장 경로
        self.results_dir = os.path.join(config.OUTPUT_DIR, 'NBA_머신러닝_결과')
        os.makedirs(self.results_dir, exist_ok=True)
    
    def load_data(self):
        """전처리된 데이터 로드"""
        print("\n" + "=" * 60)
        print("머신러닝용 데이터 로드")
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
    
    def prepare_game_level_data(self) -> pd.DataFrame:
        """
        경기 단위 데이터 준비 (승/패 예측용)
        
        Returns:
            경기 단위로 집계된 DataFrame
        """
        print("\n[경기 단위 데이터 준비]")
        
        # 홈팀 데이터만 사용
        home_df = self.df[self.df['HOME_TEAM_ID'] == self.df['TEAM_ID']].copy()
        
        # 경기별 팀 통계 집계
        game_features = [
            'PTS', 'AST', 'REB', 'FG_PCT', 'FG3_PCT', 'FT_PCT',
            'STL', 'BLK', 'TO', 'PF', 'FGM', 'FGA', 'FG3M', 'FG3A',
            'EFG_PCT', 'TS_PCT', 'SEI', 'PPM'
        ]
        
        # 경기별 팀 평균 통계
        game_stats = home_df.groupby('GAME_ID').agg({
            **{col: 'mean' for col in game_features if col in home_df.columns},
            'PLUS_MINUS': 'sum'  # 팀 전체 PLUS_MINUS
        }).reset_index()
        
        # 경기 정보 병합
        game_info = home_df[['GAME_ID', 'SEASON', 'GAME_DATE_EST', 'HOME_TEAM_ID', 'VISITOR_TEAM_ID']].drop_duplicates()
        game_stats = game_stats.merge(game_info, on='GAME_ID', how='left')
        
        # 승/패 레이블 생성 (PLUS_MINUS > 0이면 승리)
        game_stats['WIN'] = (game_stats['PLUS_MINUS'] > 0).astype(int)
        
        print(f"✓ 경기 단위 데이터 준비 완료: {len(game_stats):,}경기")
        print(f"  - 승리: {game_stats['WIN'].sum():,}경기 ({game_stats['WIN'].mean()*100:.1f}%)")
        print(f"  - 패배: {(~game_stats['WIN'].astype(bool)).sum():,}경기 ({(1-game_stats['WIN'].mean())*100:.1f}%)")
        
        return game_stats
    
    def prepare_player_performance_data(self) -> pd.DataFrame:
        """
        선수 성과 예측용 데이터 준비
        
        Returns:
            선수별 경기 기록 DataFrame
        """
        print("\n[선수 성과 예측용 데이터 준비]")
        
        # 최소 출전 시간 필터링
        player_minutes = self.df.groupby('PLAYER_NAME')['MIN'].sum()
        qualified_players = player_minutes[player_minutes >= config.MIN_MINUTES_THRESHOLD].index
        
        player_df = self.df[self.df['PLAYER_NAME'].isin(qualified_players)].copy()
        
        # 선수별 최근 N경기 평균 통계 계산을 위한 정렬
        player_df = player_df.sort_values(['PLAYER_NAME', 'GAME_DATE_EST'])
        
        # 시계열 특성 생성 (최근 5경기 평균)
        features_for_avg = ['PTS', 'AST', 'REB', 'FG_PCT', 'STL', 'BLK', 'TO', 'PLUS_MINUS']
        
        for feature in features_for_avg:
            if feature in player_df.columns:
                player_df[f'{feature}_LAG5'] = player_df.groupby('PLAYER_NAME')[feature].transform(
                    lambda x: x.shift(1).rolling(window=5, min_periods=1).mean()
                )
        
        # 결측치 처리 (첫 경기 등)
        lag_cols = [col for col in player_df.columns if '_LAG5' in col]
        player_df[lag_cols] = player_df[lag_cols].fillna(0)
        
        print(f"✓ 선수 성과 예측용 데이터 준비 완료: {len(player_df):,}행")
        print(f"  - 선수 수: {player_df['PLAYER_NAME'].nunique():,}명")
        
        return player_df
    
    def train_win_loss_classifier(self, test_size: float = 0.2, random_state: int = 42):
        """
        경기 승/패 분류 모델 학습
        
        Args:
            test_size: 테스트 세트 비율
            random_state: 랜덤 시드
        """
        print("\n" + "=" * 60)
        print("1. 경기 승/패 예측 모델 학습")
        print("=" * 60)
        
        # 경기 단위 데이터 준비
        game_stats = self.prepare_game_level_data()
        
        # 특성 선택
        feature_cols = [
            'PTS', 'AST', 'REB', 'FG_PCT', 'FG3_PCT', 'FT_PCT',
            'STL', 'BLK', 'TO', 'PF', 'EFG_PCT', 'TS_PCT', 'SEI', 'PPM'
        ]
        feature_cols = [col for col in feature_cols if col in game_stats.columns]
        
        # 데이터 준비
        X = game_stats[feature_cols].fillna(0)
        y = game_stats['WIN']
        
        # 학습/테스트 분할
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        
        # 스케일링
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        self.scalers['win_loss'] = scaler
        
        # 모델 학습
        print("\n[모델 학습 중...]")
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=random_state,
            n_jobs=-1
        )
        model.fit(X_train_scaled, y_train)
        self.models['win_loss'] = model
        
        # 예측 및 평가
        y_pred = model.predict(X_test_scaled)
        y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
        
        accuracy = accuracy_score(y_test, y_pred)
        cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5, scoring='accuracy')
        
        print(f"\n[모델 성능]")
        print(f"  - 정확도 (Accuracy): {accuracy:.4f}")
        print(f"  - 교차 검증 평균 정확도: {cv_scores.mean():.4f} (±{cv_scores.std():.4f})")
        print(f"\n[분류 리포트]")
        print(classification_report(y_test, y_pred, target_names=['패배', '승리']))
        
        # 특성 중요도
        feature_importance = pd.DataFrame({
            'feature': feature_cols,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print(f"\n[특성 중요도 Top 10]")
        print(feature_importance.head(10).to_string(index=False))
        
        # 결과 저장
        self.results['win_loss'] = {
            'accuracy': accuracy,
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std(),
            'feature_importance': feature_importance,
            'confusion_matrix': confusion_matrix(y_test, y_pred),
            'y_test': y_test.values,
            'y_pred': y_pred,
            'y_pred_proba': y_pred_proba
        }
        
        # 결과를 파일로 저장 (시각화 모듈에서 사용)
        result_path = os.path.join(self.results_dir, 'win_loss_results.pkl')
        with open(result_path, 'wb') as f:
            pickle.dump(self.results['win_loss'], f)
        
        # 모델 저장
        model_path = os.path.join(self.models_dir, 'win_loss_classifier.pkl')
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        print(f"\n✓ 모델 저장 완료: {model_path}")
    
    def train_player_performance_regressor(self, target: str = 'PLUS_MINUS', 
                                          test_size: float = 0.2, random_state: int = 42):
        """
        선수 성과 예측 회귀 모델 학습
        
        Args:
            target: 예측 대상 ('PLUS_MINUS', 'PTS', 'AST', 'REB')
            test_size: 테스트 세트 비율
            random_state: 랜덤 시드
        """
        print("\n" + "=" * 60)
        print(f"2. 선수 {target} 예측 모델 학습")
        print("=" * 60)
        
        # 선수 성과 데이터 준비
        player_df = self.prepare_player_performance_data()
        
        # 특성 선택
        base_features = [
            'MIN', 'PTS', 'AST', 'REB', 'FG_PCT', 'FG3_PCT', 'FT_PCT',
            'STL', 'BLK', 'TO', 'PF', 'EFG_PCT', 'TS_PCT', 'SEI', 'PPM'
        ]
        
        # 시계열 특성 추가
        lag_features = [col for col in player_df.columns if '_LAG5' in col]
        
        feature_cols = [col for col in base_features if col in player_df.columns and col != target]
        feature_cols.extend(lag_features)
        
        # 데이터 준비
        X = player_df[feature_cols].fillna(0)
        y = player_df[target].fillna(0)
        
        # 학습/테스트 분할
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
        
        # 스케일링
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        self.scalers[f'player_{target}'] = scaler
        
        # 모델 학습
        print("\n[모델 학습 중...]")
        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=random_state,
            n_jobs=-1
        )
        model.fit(X_train_scaled, y_train)
        self.models[f'player_{target}'] = model
        
        # 예측 및 평가
        y_pred = model.predict(X_test_scaled)
        
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)
        
        cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5, scoring='r2')
        
        print(f"\n[모델 성능]")
        print(f"  - R² Score: {r2:.4f}")
        print(f"  - RMSE: {rmse:.4f}")
        print(f"  - MAE: {mae:.4f}")
        print(f"  - 교차 검증 평균 R²: {cv_scores.mean():.4f} (±{cv_scores.std():.4f})")
        
        # 특성 중요도
        feature_importance = pd.DataFrame({
            'feature': feature_cols,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print(f"\n[특성 중요도 Top 10]")
        print(feature_importance.head(10).to_string(index=False))
        
        # 결과 저장
        self.results[f'player_{target}'] = {
            'r2': r2,
            'rmse': rmse,
            'mae': mae,
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std(),
            'feature_importance': feature_importance,
            'y_test': y_test.values,
            'y_pred': y_pred
        }
        
        # 결과를 파일로 저장 (시각화 모듈에서 사용)
        result_path = os.path.join(self.results_dir, f'player_{target}_results.pkl')
        with open(result_path, 'wb') as f:
            pickle.dump(self.results[f'player_{target}'], f)
        
        # 모델 저장
        model_path = os.path.join(self.models_dir, f'player_{target}_regressor.pkl')
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
        print(f"\n✓ 모델 저장 완료: {model_path}")
    
    def perform_player_clustering(self, n_clusters: int = 5, random_state: int = 42):
        """
        선수 클러스터링 (플레이 스타일 분석)
        
        Args:
            n_clusters: 클러스터 개수
            random_state: 랜덤 시드
        """
        print("\n" + "=" * 60)
        print("3. 선수 클러스터링 (플레이 스타일 분석)")
        print("=" * 60)
        
        # 선수별 평균 통계 계산
        player_stats = self.df.groupby('PLAYER_NAME').agg({
            'MIN': 'sum',
            'PTS': 'mean',
            'AST': 'mean',
            'REB': 'mean',
            'STL': 'mean',
            'BLK': 'mean',
            'TO': 'mean',
            'FG_PCT': 'mean',
            'FG3_PCT': 'mean',
            'PLUS_MINUS': 'mean',
            'EFG_PCT': 'mean',
            'TS_PCT': 'mean',
            'SEI': 'mean',
            'PPM': 'mean'
        }).reset_index()
        
        # 최소 출전 시간 필터링
        player_stats = player_stats[player_stats['MIN'] >= config.MIN_MINUTES_THRESHOLD]
        
        # 클러스터링 특성 선택
        feature_cols = [
            'PTS', 'AST', 'REB', 'STL', 'BLK', 'TO',
            'FG_PCT', 'FG3_PCT', 'EFG_PCT', 'TS_PCT', 'PPM'
        ]
        feature_cols = [col for col in feature_cols if col in player_stats.columns]
        
        X = player_stats[feature_cols].fillna(0)
        
        # 스케일링
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        self.scalers['clustering'] = scaler
        
        # K-Means 클러스터링
        print("\n[클러스터링 수행 중...]")
        kmeans = KMeans(n_clusters=n_clusters, random_state=random_state, n_init=10)
        clusters = kmeans.fit_predict(X_scaled)
        
        player_stats['Cluster'] = clusters
        self.models['clustering'] = kmeans
        
        # 클러스터별 통계
        print(f"\n[클러스터별 통계]")
        cluster_summary = player_stats.groupby('Cluster')[feature_cols].mean()
        cluster_counts = player_stats['Cluster'].value_counts().sort_index()
        
        for cluster_id in range(n_clusters):
            count = cluster_counts[cluster_id]
            print(f"\n클러스터 {cluster_id} ({count}명):")
            cluster_data = cluster_summary.loc[cluster_id]
            top_features = cluster_data.nlargest(5)
            print(f"  주요 특징: {', '.join([f'{k}={v:.2f}' for k, v in top_features.items()])}")
        
        # 결과 저장
        self.results['clustering'] = {
            'player_stats': player_stats,
            'cluster_summary': cluster_summary,
            'cluster_counts': cluster_counts,
            'n_clusters': n_clusters
        }
        
        # 결과 저장
        result_path = os.path.join(self.results_dir, 'player_clustering.csv')
        player_stats.to_csv(result_path, index=False, encoding='utf-8')
        print(f"\n✓ 클러스터링 결과 저장 완료: {result_path}")
    
    def train_all_models(self):
        """모든 머신러닝 모델 학습"""
        if self.df is None:
            self.load_data()
        
        # 1. 경기 승/패 예측
        self.train_win_loss_classifier()
        
        # 2. 선수 성과 예측 (PLUS_MINUS, PTS)
        self.train_player_performance_regressor(target='PLUS_MINUS')
        self.train_player_performance_regressor(target='PTS')
        
        # 3. 선수 클러스터링
        self.perform_player_clustering()
        
        print("\n" + "=" * 60)
        print("모든 머신러닝 모델 학습 완료!")
        print("=" * 60)


if __name__ == "__main__":
    # 직접 실행 시 모든 모델 학습
    ml = NBAMachineLearning()
    ml.train_all_models()

