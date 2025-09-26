#!/usr/bin/env python3
"""
Script para detectar outliers nos dados de nível do rio
"""

import json
import numpy as np
from scipy import stats

def main():
    # Carregar dados
    json_file = 'dados_nivel_rios_itacoatiara.json'
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    print(f"Analisando dados de nível do rio em {json_file}...")
    
    # Preparar os dados para análise
    all_values = []
    value_info = []  # Para armazenar ano, mês e valor
    
    for entry in data:
        ano = entry['ano']
        mes = entry['mes']
        valores = entry['data']
        
        for dia, valor in enumerate(valores, 1):
            all_values.append(valor)
            value_info.append((ano, mes, dia, valor))
    
    # Converter para array numpy para cálculos estatísticos
    all_values = np.array(all_values)
    
    # Calcular Z-score para identificar outliers
    z_scores = np.abs(stats.zscore(all_values))
    
    # Considerar outliers valores com Z-score > 3
    threshold = 3.0
    outlier_indices = np.where(z_scores > threshold)[0]
    
    # Obter informações dos outliers
    outliers = [value_info[i] for i in outlier_indices]
    
    # Ordenar outliers pelo Z-score (do maior para o menor)
    outliers_with_z = [(ano, mes, dia, valor, z_scores[i]) 
                      for i, (ano, mes, dia, valor) in zip(outlier_indices, outliers)]
    outliers_with_z.sort(key=lambda x: x[4], reverse=True)
    
    # Estatísticas básicas
    print(f"\nEstatísticas gerais:")
    print(f"Total de medições: {len(all_values)}")
    print(f"Valor mínimo: {np.min(all_values):.2f} metros")
    print(f"Valor máximo: {np.max(all_values):.2f} metros")
    print(f"Média: {np.mean(all_values):.2f} metros")
    print(f"Mediana: {np.median(all_values):.2f} metros")
    print(f"Desvio padrão: {np.std(all_values):.2f} metros")
    
    # Exibir outliers
    print(f"\nOutliers detectados (Z-score > 3):")
    print(f"Total de outliers: {len(outliers_with_z)}")
    
    if outliers_with_z:
        print("\nTop 10 outliers mais significativos:")
        print("Ano  | Mês | Dia | Valor (m) | Z-score")
        print("-" * 45)
        
        for i, (ano, mes, dia, valor, z_score) in enumerate(outliers_with_z[:10], 1):
            print(f"{ano} | {mes:2d}  | {dia:2d}  | {valor:8.2f} | {z_score:8.2f}")

if __name__ == "__main__":
    main()