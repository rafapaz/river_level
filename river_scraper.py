import requests
import json
import re
import time
import argparse
from typing import List, Dict, Optional

def extract_river_data(html_content: str, river_name: str) -> Optional[List[float]]:
    """
    Extrai os dados da série do rio especificado do HTML
    
    Args:
        html_content (str): Conteúdo HTML da resposta
        river_name (str): Nome do rio para extrair os dados
        
    Returns:
        Optional[List[float]]: Lista com os dados ou None se não encontrar
    """
    try:
        # Procura pelo padrão da série com o nome do rio fornecido
        pattern = fr"name:\s*['\"]({river_name})['\"],\s*data:\s*\[([\d\.,\s]+)\]"
        match = re.search(pattern, html_content, re.IGNORECASE)
        
        if match:
            data_string = match.group(2)
            # Converte a string de números separados por vírgula em lista de floats
            data_list = [float(x.strip()) for x in data_string.split(',') if x.strip()]
            return data_list
        else:
            print(f"Padrão '{river_name}' não encontrado no HTML")
            return None
            
    except Exception as e:
        print(f"Erro ao extrair dados: {e}")
        return None

def scrape_river_data(ano: int, mes: int, river_name: str) -> Optional[List[float]]:
    """
    Faz a requisição POST para obter dados de um mês específico
    
    Args:
        ano (int): Ano (2005-2025)
        mes (int): Mês (1-12)
        river_name (str): Nome do rio para extrair os dados
        
    Returns:
        Optional[List[float]]: Dados extraídos ou None em caso de erro
    """
    url = "https://proamanaus.com.br/nivel-dos-rios"
    
    # Dados do formulário
    form_data = {
        'ano': str(ano),
        'mes': f"{mes:02d}"  # Formata mês com 2 dígitos (01, 02, etc.)
    }
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        print(f"Fazendo requisição para {ano}/{mes:02d}...")
        response = requests.post(url, data=form_data, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Extrai os dados da resposta HTML
        data = extract_river_data(response.text, river_name)
        return data
        
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição para {ano}/{mes:02d}: {e}")
        return None
    except Exception as e:
        print(f"Erro inesperado para {ano}/{mes:02d}: {e}")
        return None

def main():
    """
    Função principal que executa o scraping completo
    """
    # Configurar o parser de argumentos
    parser = argparse.ArgumentParser(description='Scraper de dados de nível de rios')
    parser.add_argument('river_name', type=str, help='Nome do rio para extrair os dados (ex: Itacoatiara, Manaus)')
    parser.add_argument('--ano-inicio', type=int, default=2005, help='Ano inicial para coleta (padrão: 2005)')
    parser.add_argument('--ano-fim', type=int, default=2025, help='Ano final para coleta (padrão: 2025)')
    
    args = parser.parse_args()
    river_name = args.river_name
    
    print(f"Iniciando scraping dos dados de nível do rio {river_name}...")
    
    all_data = []
    ano_inicio = args.ano_inicio
    ano_fim = args.ano_fim
    total_requests = (ano_fim - ano_inicio + 1) * 12  # Anos × 12 meses
    current_request = 0
    
    # Validação do nome do rio
    if not river_name or len(river_name) < 2:
        print("Erro: Nome do rio inválido. Forneça um nome válido.")
        return
    
    # Loop pelos anos
    for ano in range(ano_inicio, ano_fim + 1):
        # Loop pelos meses (1 a 12)
        for mes in range(1, 13):
            current_request += 1
            print(f"Progresso: {current_request}/{total_requests}")
            
            # Faz a requisição e extrai os dados
            data = scrape_river_data(ano, mes, river_name)
            
            if data is not None:
                # Adiciona os dados à lista principal
                entry = {
                    'ano': ano,
                    'mes': mes,
                    'data': data
                }
                all_data.append(entry)
                print(f"✓ Dados obtidos para {ano}/{mes:02d}: {len(data)} valores")
            else:
                print(f"✗ Falha ao obter dados para {ano}/{mes:02d}")
            
            # Pausa entre requisições para não sobrecarregar o servidor
            time.sleep(1)
    
    # Salva todos os dados em um arquivo JSON
    output_filename = f"dados_nivel_rio_{river_name.lower()}.json"
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Scraping concluído!")
        print(f"✓ Total de registros obtidos: {len(all_data)}")
        print(f"✓ Dados salvos em: {output_filename}")
        
        # Estatísticas resumidas
        if all_data:
            anos_unicos = set(entry['ano'] for entry in all_data)
            meses_unicos = set(entry['mes'] for entry in all_data)
            print(f"✓ Anos processados: {sorted(anos_unicos)}")
            print(f"✓ Meses processados: {sorted(meses_unicos)}")
            
            # Exemplo de alguns dados
            print(f"\nExemplo dos primeiros registros:")
            for entry in all_data[:3]:
                print(f"  {entry['ano']}/{entry['mes']:02d}: {len(entry['data'])} valores")
                
    except Exception as e:
        print(f"Erro ao salvar arquivo JSON: {e}")

if __name__ == "__main__":
    main()
