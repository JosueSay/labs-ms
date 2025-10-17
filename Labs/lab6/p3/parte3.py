import random
import numpy as np
import matplotlib.pyplot as plt
import yaml
import subprocess
import os
import re
import argparse

def ejecutar_simulacion(script_simulacion, config_path, semilla, repeticion):

    print(f"  Repeticion {repeticion} con semilla {semilla}...")
    
    try:
        #jejc sim 1  o 2
        result = subprocess.run(
            ['python', script_simulacion, '--config', config_path],
            capture_output=True, text=True
        )
        
        #output
        output = result.stdout + result.stderr   
        #datos curvas
        S_hist, I_hist, R_hist = extraer_datos_del_output(output)
        
        if S_hist is not None:
            print(f"    Datos capturados: {len(S_hist)} puntos temporales")
            return S_hist, I_hist, R_hist
        else:
            print(f"    No se pudieron capturar datos")
            return None
            
    except Exception as e:
        print(f"    Error: {e}")
        return None

def extraer_datos_del_output(output):
    #extraer SIR
    S_hist, I_hist, R_hist = [], [], []
    
    lineas = output.split('\n')
    
    for linea in lineas:
        if '[STEP' in linea and '| S=' in linea:
            patron = r'S=(\d+)\s+I=(\d+)\s+R=(\d+)'
            match = re.search(patron, linea)
            if match:
                S, I, R = map(int, match.groups())
                S_hist.append(S)
                I_hist.append(I)
                R_hist.append(R)
    
    if S_hist:
        return np.array(S_hist), np.array(I_hist), np.array(R_hist)
    
    patron_final = r"\[RESUMEN\] Último paso:.*?S=(\d+) I=(\d+) R=(\d+)"
    match_final = re.search(patron_final, output)
    if match_final:
        S, I, R = map(int, match_final.groups())
        return np.array([S]), np.array([I]), np.array([R])
    
    return None, None, None

def main():
    parser = argparse.ArgumentParser(description='Multiples repeticiones de simulacion SIR')
    parser.add_argument('--simulacion', choices=['sim1', 'sim2'], default='sim1',
                       help='Que simulación ejecutar: sim1 (partículas moviles) o sim2 (grid celular)')
    parser.add_argument('--repeticiones', type=int, default=10, help='Numero de repeticiones') #si no da, 10 default
    args = parser.parse_args()
    
    if args.simulacion == 'sim1':
        script_simulacion = 'p1/sim1.py'
        carpeta_imagenes = 'images/promedio_sim1'
        nombre_simulacion = 'Simulacion 1 (Particulas moviles)'
    else:
        script_simulacion = 'p2/sim2.py'
        carpeta_imagenes = 'images/promedio_sim2'
        nombre_simulacion = 'Simulacion 2 (Grid celular)'
    
    Nexp = args.repeticiones
    config_path = 'config.yaml'
    
    print("=" * 60)
    print(f"EJECUTANDO {Nexp} REPETICIONES DE {args.simulacion.upper()}")
    print(f"{nombre_simulacion}")
    print("=" * 60)
    
    if not os.path.exists(script_simulacion):
        print(f"Error: No se encuentra {script_simulacion}")
        return
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    if args.simulacion == 'sim1' and 'sim1' in config:
        config_sim = config['sim1']
        print("Parametros simulacion 1:")
    elif args.simulacion == 'sim2' and 'sim2' in config:
        config_sim = config['sim2']
        print("Parametros simulacion 2:")
    else:
        config_sim = config.get('sim1', {})
        print("Parametros simulacion:")
    
    parametros = ['L', 'N_total', 'I0', 'beta', 'gamma', 'steps']
    for param in parametros:
        if param in config_sim:
            print(f"  {param}: {config_sim[param]}")
    print()
    
    semilla_fija = 150
    #gen semmillas para cada repeticion
    semillas = [semilla_fija]*Nexp
    all_S, all_I, all_R = [], [], []
    repeticiones_exitosas = 0

    semilla_original = config.get('seed', 12345)
    
    for i, semilla in enumerate(semillas):
        config['seed'] = semilla_fija
        with open(config_path, 'w') as f:
            yaml.dump(config, f)
        
        resultados = ejecutar_simulacion(script_simulacion, config_path, semilla, i+1)
        
        if resultados is not None:
            S, I, R = resultados
            all_S.append(S)
            all_I.append(I)
            all_R.append(R)
            repeticiones_exitosas += 1
    
    #semilla og
    config['seed'] = semilla_original
    with open(config_path, 'w') as f:
        yaml.dump(config, f)
    
    print(f"\nRepeticiones exitosas: {repeticiones_exitosas}/{Nexp}")
    
    if repeticiones_exitosas > 1:
        process_results(all_S, all_I, all_R, repeticiones_exitosas, nombre_simulacion, carpeta_imagenes)
    else:
        print("Se necesitan al menos 2 repeticiones exitosas para calcular promedios")

def process_results(all_S, all_I, all_R, Nexp, nombre_simulacion, carpeta_imagenes):
    min_len = min(len(S) for S in all_S)
    print(f"Longitud temporal de datos: {min_len} pasos")
    
    all_S_trunc = [S[:min_len] for S in all_S]
    all_I_trunc = [I[:min_len] for I in all_I] 
    all_R_trunc = [R[:min_len] for R in all_R]
    
    all_S_arr = np.array(all_S_trunc)
    all_I_arr = np.array(all_I_trunc)
    all_R_arr = np.array(all_R_trunc)
    
    #promedios y desv
    S_promedio = np.mean(all_S_arr, axis=0)
    I_promedio = np.mean(all_I_arr, axis=0)
    R_promedio = np.mean(all_R_arr, axis=0)
    
    S_std = np.std(all_S_arr, axis=0)
    I_std = np.std(all_I_arr, axis=0)
    R_std = np.std(all_R_arr, axis=0)
    
    plt.figure(figsize=(12, 8))
    timesteps = range(len(S_promedio))
    
    #promedio curvas
    plt.plot(timesteps, S_promedio, 'b-', label='Suscetibles (S) Promedio', linewidth=2)
    plt.fill_between(timesteps, S_promedio - S_std, S_promedio + S_std, alpha=0.3, color='blue')
    
    plt.plot(timesteps, I_promedio, 'r-', label='Infectados (I) Promedio', linewidth=2)
    plt.fill_between(timesteps, I_promedio - I_std, I_promedio + I_std, alpha=0.3, color='red')
    
    plt.plot(timesteps, R_promedio, 'g-', label='Recuperados (R) Promedio', linewidth=2)
    plt.fill_between(timesteps, R_promedio - R_std, R_promedio + R_std, alpha=0.3, color='green')
    
    plt.xlabel('Tiempo (pasos)')
    plt.ylabel('Numero Individuos')
    plt.title(f'{nombre_simulacion}\nDinamica Promedio de Modelo SIR ({Nexp} repeticiones)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    os.makedirs(carpeta_imagenes, exist_ok=True)
    nombre_archivo = f'{carpeta_imagenes}/curvas_promediadas.png'
    plt.savefig(nombre_archivo, dpi=300, bbox_inches='tight')
    plt.show()
    
    print("\n" + "="*50)
    print("RESULTADOS PROMEDIADOS")
    print("="*50)
    print(f"Valores finales (promedio ± desviacion estándar):")
    print(f"  S(t_final) = {S_promedio[-1]:.1f} ± {S_std[-1]:.1f}")
    print(f"  I(t_final) = {I_promedio[-1]:.1f} ± {I_std[-1]:.1f}") 
    print(f"  R(t_final) = {R_promedio[-1]:.1f} ± {R_std[-1]:.1f}")
    
    #Snapshots
    if min_len > 5:
        tiempos = [0, min_len//4, min_len//2, 3*min_len//4, min_len-1]
        print(f"\nEvolucion temporal:")
        for t in tiempos:
            print(f"  Paso {t:3d}: S={S_promedio[t]:6.1f} ± {S_std[t]:4.1f}, "
                  f"I={I_promedio[t]:6.1f} ± {I_std[t]:4.1f}, "
                  f"R={R_promedio[t]:6.1f} ± {R_std[t]:4.1f}")
    
    #Guardar datos
    nombre_archivo_datos = f'resultados_promedio_{nombre_simulacion.split()[1].lower()}.npz'
    np.savez(nombre_archivo_datos,
             S_promedio=S_promedio, I_promedio=I_promedio, R_promedio=R_promedio,
             S_std=S_std, I_std=I_std, R_std=R_std,
             all_S=all_S_arr, all_I=all_I_arr, all_R=all_R_arr)
    
    print(f"\nDatos guardados en '{nombre_archivo_datos}'")
    print(f"Grafica guardada en '{nombre_archivo}'")

if __name__ == "__main__":
    main()