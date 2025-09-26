#!/usr/bin/env python3
"""
Script para treinar modelo de previsão de nível de rio
Autor: Sistema de ML para Dados Temporais
"""

import json
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import matplotlib.pyplot as plt
from datetime import datetime
import os
import argparse

class RiverLevelPredictor:
    def __init__(self):
        self.model = RandomForestRegressor(
            n_estimators=200,
            max_depth=20,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        
    def load_data(self, json_file):
        """Carrega e processa os dados do JSON"""
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        features = []
        targets = []
        
        for entry in data:
            ano = entry['ano']
            mes = entry['mes']
            dados = entry['data']
            
            for dia_idx, nivel in enumerate(dados):
                dia = dia_idx + 1  # Dia começa em 1
                
                # Features: ano, mês, dia, dia do ano
                dia_do_ano = self._get_day_of_year(ano, mes, dia)
                
                features.append([
                    ano, 
                    mes, 
                    dia,
                    dia_do_ano,
                    np.sin(2 * np.pi * dia_do_ano / 365.25),  # Componente sazonal
                    np.cos(2 * np.pi * dia_do_ano / 365.25),  # Componente sazonal
                    np.sin(2 * np.pi * mes / 12),  # Sazonalidade mensal
                    np.cos(2 * np.pi * mes / 12)   # Sazonalidade mensal
                ])
                targets.append(nivel)
        
        return np.array(features), np.array(targets)
    
    def _get_day_of_year(self, ano, mes, dia):
        """Calcula o dia do ano"""
        try:
            date = datetime(ano, mes, dia)
            return date.timetuple().tm_yday
        except:
            # Para datas inválidas, aproximar
            dias_por_mes = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
            if ano % 4 == 0 and (ano % 100 != 0 or ano % 400 == 0):
                dias_por_mes[1] = 29
            
            return sum(dias_por_mes[:mes-1]) + dia
    
    def train(self, X, y):
        """Treina o modelo"""
        print("Iniciando treinamento do modelo...")
        
        # Dividir dados em treino e teste
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Treinar modelo
        self.model.fit(X_train, y_train)
        
        # Fazer previsões no conjunto de teste
        y_pred = self.model.predict(X_test)
        
        # Calcular métricas
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)
        
        print(f"Métricas do modelo:")
        print(f"MAE (Erro Absoluto Médio): {mae:.3f} metros")
        print(f"RMSE (Raiz do Erro Quadrático Médio): {rmse:.3f} metros")
        print(f"R² (Coeficiente de Determinação): {r2:.3f}")
        
        # Importância das features
        feature_names = ['ano', 'mes', 'dia', 'dia_do_ano', 'sin_anual', 'cos_anual', 'sin_mensal', 'cos_mensal']
        importances = self.model.feature_importances_
        
        print(f"\nImportância das features:")
        for name, importance in zip(feature_names, importances):
            print(f"{name}: {importance:.3f}")
        
        # Plotar resultados
        self._plot_results(y_test, y_pred, mae, rmse, r2)
        
        return mae, rmse, r2
    
    def _plot_results(self, y_true, y_pred, mae, rmse, r2):
        """Plota gráficos de avaliação do modelo"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # Gráfico 1: Valores reais vs preditos
        axes[0, 0].scatter(y_true, y_pred, alpha=0.5)
        axes[0, 0].plot([y_true.min(), y_true.max()], [y_true.min(), y_true.max()], 'r--', lw=2)
        axes[0, 0].set_xlabel('Nível Real (m)')
        axes[0, 0].set_ylabel('Nível Predito (m)')
        axes[0, 0].set_title('Valores Reais vs Preditos')
        axes[0, 0].grid(True, alpha=0.3)
        
        # Gráfico 2: Resíduos
        residuals = y_true - y_pred
        axes[0, 1].scatter(y_pred, residuals, alpha=0.5)
        axes[0, 1].axhline(y=0, color='r', linestyle='--')
        axes[0, 1].set_xlabel('Nível Predito (m)')
        axes[0, 1].set_ylabel('Resíduos (m)')
        axes[0, 1].set_title('Gráfico de Resíduos')
        axes[0, 1].grid(True, alpha=0.3)
        
        # Gráfico 3: Histograma dos resíduos
        axes[1, 0].hist(residuals, bins=50, alpha=0.7, edgecolor='black')
        axes[1, 0].set_xlabel('Resíduos (m)')
        axes[1, 0].set_ylabel('Frequência')
        axes[1, 0].set_title('Distribuição dos Resíduos')
        axes[1, 0].grid(True, alpha=0.3)
        
        # Gráfico 4: Métricas
        axes[1, 1].text(0.1, 0.8, f'MAE: {mae:.3f} m', fontsize=14, transform=axes[1, 1].transAxes)
        axes[1, 1].text(0.1, 0.6, f'RMSE: {rmse:.3f} m', fontsize=14, transform=axes[1, 1].transAxes)
        axes[1, 1].text(0.1, 0.4, f'R²: {r2:.3f}', fontsize=14, transform=axes[1, 1].transAxes)
        axes[1, 1].set_xlim(0, 1)
        axes[1, 1].set_ylim(0, 1)
        axes[1, 1].set_title('Métricas do Modelo')
        axes[1, 1].axis('off')
        
        plt.tight_layout()
        plt.savefig('model_evaluation.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"\nGráfico de avaliação salvo como 'model_evaluation.png'")
    
    def save_model(self, filename='river_level_model.pkl'):
        """Salva o modelo treinado"""
        joblib.dump(self, filename)
        print(f"Modelo salvo como '{filename}'")

def parse_arguments():
    """Processa os argumentos da linha de comando"""
    parser = argparse.ArgumentParser(description='Treina modelo de previsão de nível de rio')
    parser.add_argument('--input', '-i', type=str, default='dados_nivel_rios_itacoatiara.json',
                        help='Arquivo JSON com os dados de nível do rio (padrão: dados_nivel_rios_itacoatiara.json)')
    parser.add_argument('--output', '-o', type=str, default='river_level_model.pkl',
                        help='Nome do arquivo para salvar o modelo treinado (padrão: river_level_model.pkl)')
    
    return parser.parse_args()

def main():
    # Processar argumentos da linha de comando
    args = parse_arguments()
    json_file = args.input
    model_file = args.output
    
    # Verificar se o arquivo de dados existe
    if not os.path.exists(json_file):
        print(f"Erro: Arquivo '{json_file}' não encontrado!")
        print(f"Certifique-se de que o arquivo existe ou especifique outro com --input")
        return
    
    # Criar e treinar o modelo
    predictor = RiverLevelPredictor()
    
    print(f"Carregando dados do arquivo: {json_file}")
    X, y = predictor.load_data(json_file)
    
    print(f"Dados carregados: {len(X)} amostras")
    print(f"Período dos dados: {int(X[:, 0].min())} - {int(X[:, 0].max())}")
    print(f"Nível mínimo: {y.min():.2f} metros")
    print(f"Nível máximo: {y.max():.2f} metros")
    print(f"Nível médio: {y.mean():.2f} metros")
    
    # Treinar modelo
    mae, rmse, r2 = predictor.train(X, y)
    
    # Salvar modelo
    predictor.save_model(model_file)
    
    print(f"\nTreinamento concluído!")
    print(f"Use o script 'predict.py' para fazer previsões.")

if __name__ == "__main__":
    main()