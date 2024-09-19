# -*- coding: utf-8 -*-
import numpy as np
import datetime as dt
import pandas as pd
import sys
import openpyxl
import os
from colorama import init, Fore, Style, Back


init(autoreset=True)

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_current_date_time():
    current_date_time = dt.datetime.now()
    return current_date_time

def get_info_from_user():
    plate_number = input("Coloque a placa do veículo: ").upper()
    type_vehicle = input("Coloque o tipo do veículo: A para carro, B para moto, C para outros tipos de veículos: ").upper()
    if type_vehicle not in ["A", "B", "C"]:
        print(f"{Fore.RED}Tipo de veículo inválido. Por favor, escolha A, B ou C.{Style.RESET_ALL}")
        return None, None, None
    vehicle_types = {"A": "carro", "B": "moto", "C": "outro"}
    type_vehicle_full = vehicle_types.get(type_vehicle)
    entry_time = get_current_date_time()
    entry_time_str = entry_time.strftime("%d/%m/%Y %H:%M:%S")
    return plate_number, type_vehicle, entry_time

def value_per_type(type_vehicle):
    if type_vehicle == "A":
        return 0.10
    elif type_vehicle == "B":
        return 0.05
    elif type_vehicle == "C":
        return 0.20

def calculate_value_to_pay(total_time_parked, type_vehicle, entry_time, exit_time):
    total_time_parked_minutes = total_time_parked.total_seconds() / 60
    if total_time_parked_minutes <= 15:
        value_to_pay = 0
    else:
        value_to_pay = total_time_parked_minutes * value_per_type(type_vehicle)
    return value_to_pay

def calculate_total_time_parked(entry_time, exit_time):
    total_time_parked = (exit_time - entry_time)
    return total_time_parked

def vehicles_still_parked(parked):
    if parked:
        vehicle_types = {"A": "carro", "B": "moto", "C": "outro"}
        for i in parked:
            tipo_veiculo = vehicle_types.get(i[1], "desconhecido")
            print(f"{Fore.BLUE}Placa: {i[0]} - Tipo: {tipo_veiculo} - Hora da entrada: {i[2].strftime('%H:%M:%S %d/%m/%Y')}{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}Não há veículos estacionados no momento.{Style.RESET_ALL}")

def exit_info(entry_time, type_vehicle, parked, plate_number):
    exit_time = get_current_date_time()
    total_time_parked = calculate_total_time_parked(entry_time, exit_time)
    value_to_pay = calculate_value_to_pay(total_time_parked, type_vehicle, entry_time, exit_time)
    car_to_remove = None
    for car in parked:
        if car[0] == plate_number:
            car_to_remove = car
            break
    if car_to_remove is None:
        print(f"{Fore.RED}Veículo não encontrado no estacionamento.{Style.RESET_ALL}")
        return None
    parked.remove(car_to_remove)
    exit_time_str = exit_time.strftime("%d/%m/%Y %H:%M:%S")
    print(f"O veículo de placa {Fore.YELLOW}{car_to_remove[0]}{Style.RESET_ALL}"
          f" de tipo {Fore.GREEN}{car_to_remove[1]}{Style.RESET_ALL} saiu do estacionamento "
          f"às {Fore.CYAN}{exit_time_str}{Style.RESET_ALL}. "
          f"Totalizando {Fore.MAGENTA}{str(total_time_parked).split('.')[0]}{Style.RESET_ALL} de permanência. "
          f" Valor a ser pago: {Fore.RED}R$ {value_to_pay:.2f}{Style.RESET_ALL}")
    return plate_number, type_vehicle, entry_time, exit_time, total_time_parked, value_to_pay

def historic_info(plate_number, type_vehicle, entry_time, exit_time, total_time_parked, value_to_pay):
    vehicle_types = {"A": "carro", "B": "moto", "C": "outro"}
    type_vehicle_full = vehicle_types.get(type_vehicle, "desconhecido")
    
    historic_info = pd.DataFrame({
        "Placa": [plate_number],
        "Tipo de Veículo": [type_vehicle_full],
        "Horário de Entrada": [entry_time.strftime("%H:%M:%S %d/%m/%Y")],
        "Horário de Saída": [exit_time.strftime("%H:%M:%S %d/%m/%Y")],    
        "Tempo de permanência": [str(total_time_parked).split('.')[0]],
        "Valor a ser pago": [f"R$ {value_to_pay:.2f}"]
    })
    return historic_info

def save_historic_info(historic_info):
    file_path = 'historic_info.xlsx'
    
    try:
        if os.path.exists(file_path):
            df_existing = pd.read_excel(file_path)
            df_updated = pd.concat([df_existing, historic_info], ignore_index=True)
        else:
            df_updated = historic_info
        
        df_updated.to_excel(file_path, index=False)
        print(f"{Fore.GREEN}Informações históricas salvas com sucesso em {file_path}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Erro ao salvar informações históricas: {str(e)}{Style.RESET_ALL}")

def show_vehicles_from_day(parked):
    file_path = 'historic_info.xlsx'
    try:
        if not os.path.exists(file_path):
            print(f"{Fore.RED}O arquivo {file_path} não existe ainda.{Style.RESET_ALL}")
            return

        df = pd.read_excel(file_path)
        today = dt.datetime.now().date()
        
        # Convertendo a coluna 'Horário de Entrada' para datetime
        df['Horário de Entrada'] = pd.to_datetime(df['Horário de Entrada'], format='%H:%M:%S %d/%m/%Y')
        
        vehicles_from_day = df[df['Horário de Entrada'].dt.date == today]
        
        if not vehicles_from_day.empty:
            print(f"{Fore.GREEN}Veículos do dia:{Style.RESET_ALL}")
            print(vehicles_from_day.to_string(index=False))
        else:
            print(f"{Fore.YELLOW}Não houve veículos registrados hoje.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Erro ao ler o arquivo: {str(e)}{Style.RESET_ALL}")

def main(parked):
    while True:
        menu = [
            f"{Fore.YELLOW}1 - Entrada de veículo{Style.RESET_ALL}",
            f"{Fore.GREEN}2 - Saída de veículo{Style.RESET_ALL}",
            f"{Fore.BLUE}3 - Veículos do dia{Style.RESET_ALL}",
            f"{Fore.MAGENTA}4 - Veículos estacionados{Style.RESET_ALL}",
            f"{Fore.RED}5 - Sair{Style.RESET_ALL}"
        ]
        for item in menu:
            print(item)
        option = input(f"{Fore.CYAN}Escolha uma opção: {Style.RESET_ALL}")
        if option == "1":
            info = get_info_from_user()
            if info is not None:
                plate_number, type_vehicle, entry_time = info
                for i in parked:
                    if i[0] == plate_number:
                        print(f"{Fore.RED}Veículo já está no estacionamento.{Style.RESET_ALL}")
                        break
                else:
                    parked.append((plate_number, type_vehicle, entry_time))
                    vehicle_types = {"A": "carro", "B": "moto", "C": "outro"}
                    type_vehicle_full = vehicle_types.get(type_vehicle, "desconhecido")
                    entry_time_str = entry_time.strftime("%d/%m/%Y %H:%M:%S")
                    print(f"O veículo de placa {Fore.YELLOW}{plate_number}{Style.RESET_ALL}"
                          f" de tipo {Fore.GREEN}{type_vehicle_full}{Style.RESET_ALL} entrou no estacionamento"
                          f" às {Fore.CYAN}{entry_time_str}{Style.RESET_ALL}. "
                          f"Caro cliente, guarde seu comprovante de entrada. "
                          f"Até 15 minutos de graça.")
        elif option == "2":
            if not parked:
                print("Não há veículos estacionados.")
            else:
                plate_number = input("Digite a placa do veículo: ").upper()
                for vehicle in parked:
                    if vehicle[0] == plate_number:
                        type_vehicle = vehicle[1]
                        entry_time = vehicle[2]
                        result = exit_info(entry_time, type_vehicle, parked, plate_number)
                        hist_info = historic_info(*result)
                        save_historic_info(hist_info)
        elif option == "3":
            show_vehicles_from_day(parked)
        elif option == "4":
            vehicles_still_parked(parked)
        elif option == "5":
            print(f"{Fore.RED}Saindo do programa. Até logo!{Style.RESET_ALL}")
            sys.exit()
        else:
            print(f"{Fore.RED}Opção inválida. Por favor, escolha uma opção válida.{Style.RESET_ALL}")

if __name__ == "__main__":
    parked = []
    main(parked)