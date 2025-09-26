#!/usr/bin/env python3
"""
Script para detectar variações diárias maiores que um limiar nos dados de nível do rio
"""

import json
import numpy as np

def main():
    # Carregar dados
    json_file = 'dados_nivel_rios_itacoatiara.json'
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    print(f"Analisando variações diárias no arquivo {json_file}...")
    
    # Limiar de variação (em metros)
    limiar = 2.0
    
    # Lista para armazenar as variações significativas
    variacoes = []
    
    # Processar cada entrada (ano/mês)
    for entry in data:
        ano = entry['ano']
        mes = entry['mes']
        valores = entry['data']
        
        # Verificar variações dentro do mesmo mês
        for i in range(1, len(valores)):
            dia_anterior = i
            dia_atual = i + 1
            
            valor_anterior = valores[i-1]
            valor_atual = valores[i]
            
            # Calcular a variação absoluta
            variacao = abs(valor_atual - valor_anterior)
            
            # Se a variação for maior que o limiar, registrar
            if variacao > limiar:
                variacoes.append({
                    'ano': ano,
                    'mes': mes,
                    'dia_anterior': dia_anterior,
                    'dia_atual': dia_atual,
                    'valor_anterior': valor_anterior,
                    'valor_atual': valor_atual,
                    'variacao': variacao
                })
    
    # Ordenar as variações pela magnitude (da maior para a menor)
    variacoes_ordenadas = sorted(variacoes, key=lambda x: x['variacao'], reverse=True)
    
    # Exibir resultados
    print(f"\nVariações diárias maiores que {limiar} metros:")
    print(f"Total encontrado: {len(variacoes_ordenadas)}")
    
    if variacoes_ordenadas:
        print("\nTop variações (ordenadas por magnitude):")
        print("Ano  | Mês | Dia Ant | Dia Atual | Valor Ant (m) | Valor Atual (m) | Variação (m)")
        print("-" * 80)
        
        for v in variacoes_ordenadas[:30]:  # Mostrar as 30 maiores variações
            print(f"{v['ano']} | {v['mes']:2d}  | {v['dia_anterior']:7d} | {v['dia_atual']:9d} | {v['valor_anterior']:12.2f} | {v['valor_atual']:14.2f} | {v['variacao']:10.2f}")

if __name__ == "__main__":
    main()