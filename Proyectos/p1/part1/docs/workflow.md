# Flujo algoritmo genético

```mermaid
flowchart TD
    A[Inicio<br>Población N=10] --> B[Ordenar por costo #40;fitness#41;]
    B --> C[Calcular tamaños<br>S=2, C=6, M=2<br>élites=1, k=5, pc=0.95, pm=0.30]

    %% Elitismo
    C --> D[(Copiar S: S sobrevivientes)]
    C --> D0{¿gen > 0?}
    D0 -->|Sí| E[(Inyectar élites<br>#40;mejor de gen-1#41;)]
    D0 -->|No| E2[Sin élite en gen 0]
    E --> V

    %% Selección y emparejamiento
    C --> F[Selección por torneo<br>C*2 torneos, cada uno con k=5]
    F --> G{--assortative ON?}
    G -->|Sí| H[Emparejar maximizando<br>distancia #40;aristas#41;]
    G -->|No| H2[Emparejar secuencial/circular]
    H --> I
    H2 --> I

    %% Cruce + mutación ligera
    subgraph J[ Cruce y mutación ligera]
        I[Padres emparejados #40;C parejas#41;]
        I --> K{¿cruza? #40;pc=0.95#41;}

        K -->|Sí| L[Elegir operador de cruce]
        K -->|No| M[Copia padre1]

        %% Detalle de operadores
        L -->|OX| L_ox
        L -->|1- #40;--eaxFrac #41;| L_scx
        L -->|--eaxFrac| L_eax

        %% Mutación ligera
        L --> N{¿mutación ligera? #40;pm#41;}
        M --> N
        N -->|Sí| O{Tipo de mutación ligera}
        N -->|No| P[Hijo queda igual]
        O -->|70%| Q[Insertion #40;1 vez máx#41;]
        O -->|30%| R[Swap #40;1 vez máx#41;]
        
        Q --> S[(childrenC: C hijos)]
        OPT2[2-opt]
        S --> OPT2
        U --> OPT2
        OPT2 --> V

        R --> S
        P --> S
    end

    %% Mutación pura
    C --> T[M mutación pura = 2<br>Base aleatoria de la población<br>+ 1 mutación]
    T --> U1{Tipo de mutación pura}
    U1 -->|50%| U2[Insertion #40; 1 vez #41;]
    U1 -->|50%| U3[Swap #40; 1 vez #41;]
    U2 --> U[(childrenM: M individuos)]
    U3 --> U

    %% Recomposición y limpieza
    V[Recomponer: S + C + M]
    D --> V
    V --> W[Anticlones #40;deduplicar#41;]
    W --> X{¿Tamaño != N?}
    X -->|Sobran| Y[Recortar peores hasta N]
    X -->|Faltan| Z[Crear aleatorios y deduplicar]
    Y --> AA[Ordenar por costo]
    Z --> AA

    %% Especies
    SP_IMP -->|Sí| AB[Nueva población N=10<br>#40;siguiente generación#41;]
    SP_IMP -->|No| SP0{¿gen % speciesPeriod == 0#63;}

    SP0 -->|No| AB
    SP0 -->|Sí| SP_CNT{¿#35;especies ≥ 2#63;}
    SP_CNT -->|No| AB

    SP_CNT -->|Sí| SP1[Formar especies<br>#40;clustering por Jaccard de aristas<br>con speciesThresh#41;]
    SP1 --> SP2[Identificar PEOR especie<br>#40;peor “mejor miembro”#41;]
    SP2 --> SP3[Calcular cullCount = max#40;1, #8970;speciesCullFrac #183; #124;especie#124;#8971;#41;]
    SP3 --> SP4[Eliminar cullCount peores de esa especie]
    SP4 --> SP5[Reponer con inmigrantes:<br>makeRandomTour + 2-opt]
    SP5 --> SP6[Anticlones + Ordenar por costo]
    SP6 --> AB


    %% --- Catástrofe (si estancado) ---
    AA --> CT_IMP{¿Hubo NUEVO mejor en esta gen#63;}
    CT_IMP -->|Sí| CT_SKIP[Omitir catástrofe]
    
    CT_IMP -->|No| CT0{¿noImprove % catPeriod == 0 y catastropheFrac > 0#63;}

    CT0 -->|No| CT_SKIP
    CT0 -->|Sí| CT1[replaceK = #8970;catastropheFrac #183; N#8971;]
    CT1 --> CT2[Tomar los replaceK peores de la población<br>#40;salvando élites#41;]
    CT2 --> CT3[Generar inmigrantes:<br>double-bridge#40;best#41; + 2-opt]
    CT3 --> CT4[Reemplazar, Anticlones y Ordenar]
    CT4 --> CT_SKIP

    CT_SKIP --> SP_IMP{¿Hubo NUEVO mejor en esta gen#63;}





    %% ------------------ OX (Order Crossover) ------------------
    subgraph L_ox [OX]
        direction TB
        OX1[Elegir corte #91;a..b#93; en p1] --> OX2[Copiar p1#91;a..b#93; al hijo]
        OX2 --> OX3[Recorrer p2 en orden]
        OX3 --> OX4[Añadir los genes<br>no presentes #40;sin duplicar#41;]
        OX4 --> OX5[Hijo completo]
    end

    %% ------------------ SCX (Secuencial Constructivo) ------------------
    subgraph L_scx [SCX]
        direction TB

        %% Histograma de frecuencias
        SCX0{{¿Toca refrescar histograma#63;<br>#40;gen % edgeFreqPeriod == 0#41;}}
        SCX0 -->|Sí| SCX_FREQ_RECALC[Recalcular freq de aristas<br>con top K = ⌊N · edgeTopFrac⌋]
        SCX0 -->|No| SCX_FREQ_USAR[Usar freq vigente]
        SCX_FREQ_RECALC --> SCX_FREQ_USAR

        %% Inicio SCX
        SCX_FREQ_USAR --> SCX1[Inicio en p1#91;0#93;<br>#40;hijo = #91;p1#91;0#93;#93;#41;]
        SCX1 --> SCX2[Desde 'actual':<br>proponer next#40;p1#41; y next#40;p2#41;<br>si no usados]
        SCX2 --> SCX3[Scoring:<br>score#40;u,v#41; = dist#40;u,v#41; − edgeLambda · freq#123;u,v#125;]
        SCX3 --> SCX4[Elegir el mejor candidato]
        SCX4 --> SCX5{¿Ambos usados#63;}
        SCX5 -->|Sí| SCX6[Usar KNN del 'actual'<br>#40;no usados#41;]
        SCX5 -->|No| SCX7[Tomar elegido]
        SCX6 --> SCX7
        SCX7 --> SCX8{¿Faltan nodos#63;}
        SCX8 -->|Sí| SCX2
        SCX8 -->|No| SCX9[Hijo completo]
    end

    %% ------------------ EAX-lite (Mezcla de adyacencias) ------------------
    subgraph L_eax [EAX-lite]
        direction TB
        EAX1[Inicio en p1#91;0#93;<br>#40;hijo=#91;p1#91;0#93;#93;;<br>activo = p1#41;] --> EAX2[Generar candidatos:<br>prev/next del padre ACTIVO<br>que no estén usados]
        EAX2 --> EAX3{¿Hay candidatos#63;}
        EAX3 -->|No| EAX4[Probar prev/next<br>DEL OTRO padre]
        EAX4 --> EAX5{¿Sigue vacío#63;}
        EAX3 -->|Sí| EAX6
        EAX5 -->|Sí| EAX7[Tomar KNN del 'actual'<br>#40;no usados#41;]
        EAX5 -->|No| EAX6
        EAX7 --> EAX6[Elegir el más cercano<br>#40;getDistance#41;;<br>empates por índice]
        EAX6[Agregar elegido al hijo] --> EAX8[Alternar ACTIVO<br>#40;p1 #8657; p2#41;]
        EAX8 --> EAX9{¿Faltan nodos#63;}
        EAX9 -->|Sí| EAX2
        EAX9 -->|No| EAX10[Hijo completo]
    end
```
