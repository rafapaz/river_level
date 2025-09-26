#!/usr/bin/env python3
"""
Script para fazer previsões de nível de rio usando modelo treinado
Uso: python predict.py <ano> <mes> <dia>
Exemplo: python predict.py 2025 8 15

Autor: Sistema de ML para Dados Temporais
"""

import argparse
import joblib
import numpy as np
import sys
from datetime import datetime, timedelta
import os
# Importando a classe RiverLevelPredictor do script de treinamento
from train_script import RiverLevelPredictor

def validate_date(ano, mes, dia):
    """Valida se a data é válida"""
    try:
        datetime(ano, mes, dia)
        return True
    except ValueError:
        return False

def get_day_of_year(ano, mes, dia):
    """Calcula o dia do ano"""
    try:
        date = datetime(ano, mes, dia)
        return date.timetuple().tm_yday
    except ValueError:
        # Para datas inválidas, aproximar
        dias_por_mes = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        if ano % 4 == 0 and (ano % 100 != 0 or ano % 400 == 0):
            dias_por_mes[1] = 29
        
        return sum(dias_por_mes[:mes-1]) + dia

def create_features(ano, mes, dia):
    """Cria as features para o modelo"""
    dia_do_ano = get_day_of_year(ano, mes, dia)
    
    features = np.array([[
        ano,
        mes,
        dia,
        dia_do_ano,
        np.sin(2 * np.pi * dia_do_ano / 365.25),  # Componente sazonal anual
        np.cos(2 * np.pi * dia_do_ano / 365.25),  # Componente sazonal anual
        np.sin(2 * np.pi * mes / 12),             # Sazonalidade mensal
        np.cos(2 * np.pi * mes / 12)              # Sazonalidade mensal
    ]])
    
    return features

def load_model(model_path='river_level_model.pkl'):
    """Carrega o modelo treinado"""
    if not os.path.exists(model_path):
        print(f"Erro: Modelo '{model_path}' não encontrado!")
        print("Execute primeiro 'train_model.py' para treinar o modelo.")
        sys.exit(1)
    
    try:
        # Garantir que a classe RiverLevelPredictor esteja disponível antes de carregar
        # Isso é necessário porque o joblib precisa da classe para deserializar o objeto
        model = joblib.load(model_path)
        return model
    except Exception as e:
        print(f"Erro ao carregar o modelo: {e}")
        sys.exit(1)

def get_season(mes):
    """Retorna a estação do ano baseada no mês (hemisfério sul)"""
    if mes in [12, 1, 2]:
        return "Verão"
    elif mes in [3, 4, 5]:
        return "Outono"
    elif mes in [6, 7, 8]:
        return "Inverno"
    else:
        return "Primavera"

def interpret_level(nivel):
    """Interpreta o nível do rio"""
    if nivel < 2:
        return "Muito Baixo", "⚠️"
    elif nivel < 5:
        return "Baixo", "📉"
    elif nivel < 8:
        return "Normal", "✅"
    elif nivel < 12:
        return "Alto", "📈"
    else:
        return "Muito Alto", "🚨"

def main():
    parser = argparse.ArgumentParser(
        description='Prevê o nível de um rio para uma data específica ou para todo um mês',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python predict.py 2025 8 15     # Prevê nível para 15 de agosto de 2025
  python predict.py 2024 12 31    # Prevê nível para 31 de dezembro de 2024
  python predict.py 2025 8        # Prevê níveis para todos os dias de agosto de 2025
  python predict.py 2023 6        # Prevê níveis para todos os dias de junho de 2023

Notas:
  - O modelo foi treinado com dados históricos de níveis de rio
  - As previsões são baseadas em padrões sazonais e temporais
  - Datas inválidas serão rejeitadas automaticamente
  - Se apenas ano e mês forem informados, serão feitas previsões para todos os dias do mês
        """
    )
    
    parser.add_argument('ano', type=int, 
                       help='Ano para previsão (ex: 2025)')
    parser.add_argument('mes', type=int, 
                       help='Mês para previsão (1-12)')
    parser.add_argument('dia', type=int, nargs='?', default=None,
                       help='Dia para previsão (1-31). Se não informado, faz previsão para todos os dias do mês')
    parser.add_argument('--model', '-m', default='river_level_model.pkl',
                       help='Caminho para o arquivo do modelo (padrão: river_level_model.pkl)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Mostra informações detalhadas')
    
    args = parser.parse_args()
    
    # Validar inputs
    ano, mes = args.ano, args.mes
    dia = args.dia  # Pode ser None
    
    # Verificar limites básicos
    if not (1 <= mes <= 12):
        print(f"Erro: Mês deve estar entre 1 e 12 (fornecido: {mes})")
        sys.exit(1)
    
    if dia is not None and not (1 <= dia <= 31):
        print(f"Erro: Dia deve estar entre 1 e 31 (fornecido: {dia})")
        sys.exit(1)
    
    if ano < 1900 or ano > 2100:
        print(f"Aviso: Ano {ano} está fora do range típico (1900-2100)")
    
    # Determinar o intervalo de dias para previsão
    dias_para_prever = []
    
    if dia is not None:
        # Validar data específica
        if not validate_date(ano, mes, dia):
            print(f"Erro: Data {dia:02d}/{mes:02d}/{ano} não é válida!")
            sys.exit(1)
        dias_para_prever = [dia]
    else:
        # Determinar dias para o mês inteiro ou parte dele
        hoje = datetime.now()
        
        # Se for o mês atual, começar do dia atual
        if ano == hoje.year and mes == hoje.month:
            dia_inicial = hoje.day
        else:
            dia_inicial = 1
            
        # Determinar o último dia do mês
        if mes == 12:
            proximo_mes = datetime(ano + 1, 1, 1)
        else:
            proximo_mes = datetime(ano, mes + 1, 1)
        
        ultimo_dia = (proximo_mes - timedelta(days=1)).day
        
        dias_para_prever = list(range(dia_inicial, ultimo_dia + 1))
    
    # Carregar modelo
    if args.verbose:
        print("Carregando modelo...")
    
    model = load_model(args.model)
    
    # Traduzir dias da semana
    dias_pt = {
        'Monday': 'Segunda-feira',
        'Tuesday': 'Terça-feira', 
        'Wednesday': 'Quarta-feira',
        'Thursday': 'Quinta-feira',
        'Friday': 'Sexta-feira',
        'Saturday': 'Sábado',
        'Sunday': 'Domingo'
    }
    
    # Exibir cabeçalho
    if len(dias_para_prever) > 1:
        print("\n" + "="*60)
        print(f"PREVISÕES DO NÍVEL DO RIO PARA {mes:02d}/{ano}")
        print("="*60)
    
    # Loop pelos dias para fazer previsões
    for dia_atual in dias_para_prever:
        # Criar features para o dia atual
        features = create_features(ano, mes, dia_atual)
        
        # Fazer previsão
        if args.verbose and len(dias_para_prever) == 1:
            print("Fazendo previsão...")
        
        nivel_previsto = model.model.predict(features)[0]
        
        # Obter informações adicionais
        estacao = get_season(mes)
        interpretacao, emoji = interpret_level(nivel_previsto)
        data_formatada = f"{dia_atual:02d}/{mes:02d}/{ano}"
        dia_semana = datetime(ano, mes, dia_atual).strftime("%A")
        dia_semana_pt = dias_pt.get(dia_semana, dia_semana)
        
        # Exibir resultado
        if len(dias_para_prever) == 1:
            # Formato detalhado para um único dia
            print("\n" + "="*50)
            print("PREVISÃO DO NÍVEL DO RIO")
            print("="*50)
            print(f"Data: {data_formatada} ({dia_semana_pt})")
            print(f"Estação: {estacao}")
            print(f"Nível previsto: {nivel_previsto:.2f} metros")
            print(f"Classificação: {interpretacao} {emoji}")
            
            if args.verbose:
                print("\nInformações detalhadas:")
                print(f"  - Dia do ano: {get_day_of_year(ano, mes, dia_atual)}")
                print(f"  - Features utilizadas:")
                feature_names = ['ano', 'mes', 'dia', 'dia_do_ano', 'sin_anual', 'cos_anual', 'sin_mensal', 'cos_mensal']
                for i, (name, value) in enumerate(zip(feature_names, features[0])):
                    print(f"    {name}: {value:.3f}")
                
                # Estatísticas do modelo (se disponível)
                if hasattr(model.model, 'feature_importances_'):
                    print(f"  - Modelo: Random Forest com {model.model.n_estimators} árvores")
            
            print("="*50)
            
            # Aviso sobre limitações
            if nivel_previsto < 0:
                print("⚠️  Aviso: Nível negativo pode indicar limitação do modelo")
            
            if ano > 2030:
                print("⚠️  Aviso: Previsões para anos distantes podem ter menor precisão")
        else:
            # Formato compacto para múltiplos dias
            print(f"{data_formatada} ({dia_semana_pt}): {nivel_previsto:.2f}m - {interpretacao} {emoji}")
    
    # Exibir rodapé para múltiplos dias
    if len(dias_para_prever) > 1:
        print("="*60)
        if ano > 2030:
            print("⚠️  Aviso: Previsões para anos distantes podem ter menor precisão")

if __name__ == "__main__":
    main()