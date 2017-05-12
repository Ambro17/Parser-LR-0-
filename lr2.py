import re

import sys

"""
 ____ ____ _________ ____ _________ ____ ____ ____ ____ ____ ____
||l |||r |||       |||0 |||       |||p |||a |||r |||s |||e |||r ||
||__|||__|||_______|||__|||_______|||__|||__|||__|||__|||__|||__||
|/__\|/__\|/_______\|/__\|/_______\|/__\|/__\|/__\|/__\|/__\|/__\|

"""

""" Sinonimos de ERROR"""
__ERROR__CaracterInvalido = "ERROR: Cadena no aceptada, se ingresó un caracter inválido"
__ERROR__Sintaxis = "ERROR: Cadena no aceptada, no respeta la sintaxis de la gramática"

""" DATOS INMUTABLES"""
global terminales
global no_terminales
global producciones
global simboloInicial
""" ******************* Funciones Acessorias ************************  """

""" :: Incorporar datos de archivo :: """


# (1) retorna una lista de elementos que no son '{' '}' ni ','
def leer_linea(file):
    linea = file.readline().strip()  # leo linea y saco \n
    limpiar = re.compile('[^{},]')
    return limpiar.findall(linea)


def borrar_espacios(linea):
    return linea.replace(" ", "")


def prod(produc):  # en formato ('A','Bb')
    return produc[1]


def nt(produc):
    return produc[0]


def leer_producciones(file):
    lista_producciones = []
    for line in file:
        line = borrar_espacios(line)
        line = line.strip()  # quita \n
        nt_produccion = line.split('->')
        noterm = nt(nt_produccion)
        produccion = prod(nt_produccion)
        lista_producciones.append((noterm, produccion))
    return lista_producciones


def incorporar_datos_iniciales(file):
    # Seteo las variables globales para su posterior uso en el programa
    global no_terminales
    global terminales
    global simboloInicial
    global producciones
    no_terminales, terminales, simboloInicial, producciones = [], [], [], []
    no_terminales.extend(leer_linea(file))
    terminales.extend(leer_linea(file))
    simboloInicial.extend(leer_linea(file)[0])
    producciones.extend(leer_producciones(file))


def get_nt(item_tupla):  # en formato (A,(A)Ba,0)
    return item_tupla[0]


def get_prod(item_tupla):
    return item_tupla[1]


def get_indice(item_tupla):
    return item_tupla[2]


""" :::::::: Crear Diccionario ::::::::"""


def crear_diccionario(lista_prods):  # [['A', '(A)Ba'], ['A', 'Bb'], ['B', 'a'], ['B', 'b'], ['B', 'ccc']]
    dicc = {}
    i = 1
    for produccion in lista_prods:
        dicc[i] = produccion
        i += 1
    return dicc


def producciones_nt(no_terminal, list_prods):
    las_prods = []
    for produccion in list_prods:
        if produccion[0] == no_terminal:
            las_prods.append(produccion)
    return las_prods


def prod_to_item(una_prod):
    item_indexado = (una_prod[0], una_prod[1], 0)
    return item_indexado


def prods_to_item_list(prods):
    item_list = []
    for produccion in prods:
        item_list.append(prod_to_item(produccion))
    return item_list


def itemCompleto(item):
    return get_indice(item) == len(get_prod(item))


def estan(items, item_list):
    return all(item in item_list for item in items)


""" ::::: Clausura :::::"""


def clausura(item_list):
    clausura = item_list
    agrego = True
    while agrego and item_list != []:
        for item in item_list:
            indice = get_indice(item)
            if not itemCompleto(item):
                caracter_inicial = get_prod(item)[indice]
                if caracter_inicial in no_terminales:
                    prods_to_items = prods_to_item_list(producciones_nt(caracter_inicial, producciones))
                    if not estan(prods_to_items, item_list):
                        clausura.extend(prods_to_items)
                    agrego = True
                else:
                    agrego = False
            else:
                agrego = False  # llegue a item completo
        item_list = clausura  # asi como esta vuelve a iterar en 0 y aniade de nuevo las producciones ya creadas
        # linea de codigo que compara la lista_actualizada con la clausura
    return clausura


def agregar_produccion_inicial(lista_producciones):
    prod = ('Z', simboloInicial[0])
    lista_producciones.insert(0, prod)
    # agrego al dicc la nueva produccion
    DPs[0] = prod


def clausura_estado_cero(no_terms, prods):
    agregar_produccion_inicial(prods)
    pnt = producciones_nt(prods[0][0], prods)  # get_nt funciona para items_tupla (nt,prod, indice) y acá recibe (Z,A)
    item_list = prods_to_item_list(
        pnt)  # toma solo el primero de lis prods <class 'list'>: [('Z', 'A'), ('A', '(A)Ba'), ('A', 'Bb'), ('B', 'a'), ('B', 'b'), ('B', 'ccc')]
    return clausura(item_list)


def avanzarPunto(item):
    return (get_nt(item), get_prod(item), get_indice(item) + 1)


""" ::: GOTO ::: """


def goto(items, feed):  # <class 'list'>: [('S', 'aAc', 1), ('A', 'Abb', 0), ('A', 'b', 0)] caso doble A
    new_items = []
    for item in items:
        indice = get_indice(item)
        if not itemCompleto(item) and get_prod(item)[indice] == feed:
            new_items.append(avanzarPunto(item))
    return clausura(new_items)  # agrega la produccion pero no vuelve a ver si hay una segunda que transiciona con a tambien. No contempla el caso que dos items transicionen con el mismo feed


def union(lista, otralista):
    return lista + otralista


def esValido(new_estado, estados):
    return new_estado != [] and new_estado not in estados


""" ::::::::::: Generar Estados ;:::::::::::: """


def generar_estados(t, nt, ps):
    estados = []
    estados.append(clausura_estado_cero(nt, ps))
    transiciones = []  # de la forma (estado{items},feed,nuevoEstado)
    los_feeds = union(t, nt)
    for estado in estados:
        for feed in los_feeds:
            new_estado = goto(estado, feed)
            if esValido(new_estado, estados):
                estados.append(new_estado)
                transiciones.append((estado, feed, new_estado))
    resultado = (estados, transiciones)
    return resultado


def numeroDeEstado(estado_num):
    return estado_num[1]


def state(estado_num):  # estado equivale a items
    return estado_num[0]


def buscar(estado, estadosNumerados):
    lista_res = [item for item in estadosNumerados if state(item) == estado]
    return lista_res[0]


def numerarEstados(estados):
    estados_numerados = []
    for estado in estados:
        estados_numerados.append((estado, estados.index(estado)))
    return estados_numerados


def indexarTransiciones(_transiciones, estadosNumerados):  # retorna (num_estado_incial,feed,num_estado_final)
    transiciones_numeradas = []
    for (estado, feed, estado_destino) in _transiciones:
        num_estado_inicial = numeroDeEstado(buscar(estado, estadosNumerados))
        num_estado_final = numeroDeEstado(buscar(estado_destino, estadosNumerados))
        transiciones_numeradas.append((num_estado_inicial, feed, num_estado_final))
    return transiciones_numeradas


def estadosTransicionesNumeradas(estados, transiciones):
    estadosNumerados = numerarEstados(estados)
    trans_numeradas = indexarTransiciones(transiciones, estadosNumerados)
    return (estadosNumerados, trans_numeradas)


def numAEstado(num):  # dado el numero de un estado devuelve sus items
    pass


def build_matriz(filas, columnas):
    return [['0' for i in range(columnas)] for j in range(filas)]  # inicalizo en 0 una matriz e filasXcolumnas


def hayTransicion(_state, _simb):
    return goto(_state, _simb) != []


def simboloACol(simbolo, simbolos):  # dado un simbolo devuelve su posicion en la columna de simbolos -0 based
    if simbolo in simbolos:
        ind_col = simbolos.index(simbolo)
    else:
        ind_col = "El caracter %s no pertenece al alfabeto" % simbolo  # la cadena contiene un simbolo que no se encuentra en el alfabeto de la gramatica.
    return ind_col


def findMyNumState(estado_item, num_states):
    coincidencia = [item for item in num_states if state(item) == estado_item]
    return coincidencia[0]


def estadoDeUnItem(items_de_estado):  # dado un item, devuelve la clave en el diccionario.
    return len(items_de_estado) == 1


def item_to_num_prod(item, estados_num):  # state: ('B', 'a', 1) --> quiero produccion 2
    for key, produ in DPs.items():
        if produ == (get_nt(item), get_prod(item)):
            num_prod = key
    return num_prod


def esProduccionInicial(num_prod):
    return num_prod == 0


def matriz_de_accion(estados_nums, trans_num):
    nro_filas = len(estados_nums)
    nro_cols = len(no_terminales + terminales) + 1  # 1 para cadena aceptada.
    simbolos = terminales + ['#'] + no_terminales
    maccion = build_matriz(nro_filas, nro_cols)
    for estado_n in estados_nums:
        for simbolo in simbolos:
            num_estado = numeroDeEstado(estado_n)
            num_simbolo = simbolos.index(simbolo)
            estado = state(estado_n)
            if hayTransicion(estado, simbolo):
                estado_destino = goto(estado, simbolo)
                new_estado_n = findMyNumState(estado_destino, estados_nums)
                if simbolo in terminales + ['#']:
                    maccion[num_estado][num_simbolo] = "d" + str(numeroDeEstado(new_estado_n))
                    # estado_destino tiene la forma de item (nt,prod,indice) pero yo necesito la forma (estado,n)
                if simbolo in no_terminales:
                    maccion[num_estado][num_simbolo] = "Q" + str(numeroDeEstado(new_estado_n))
            elif estadoDeUnItem(estado):  # dado que es una gramatica LR(0), los estados de reduccion SOLO contienen un item, el que está listo para reducir.
                item_interior = estado[0]
                if itemCompleto(item_interior):
                    if simbolo in terminales + ['#']:  # los no terminales no reducen.
                        num_prod = item_to_num_prod(item_interior,estados_nums)  # DEBERIA darme el numeroDeProduccion dado un item
                        if not esProduccionInicial(num_prod):
                            maccion[num_estado][num_simbolo] = "r" + str(
                                num_prod)  # el problema es que cae acá tambien cuando no solo tiene un estado final, sino un estado de varios items sin transicion
                        else:
                            if simbolo == '#':
                                maccion[num_estado][num_simbolo] = '17'  # 17 equivale a Aceptada (1)

    return maccion


def numero_de_accion(accion):  # accion tiene formato "d3" o "r3"
    if accion != '0':
        w = int(accion[1:])
    else:
        w = -1  # se quiso buscar numero de accion de goto inexistente
    return w  # tod'o menos el primer caracter del string


def idAccion(accion):
    return accion[0]


def esDeplazamiento(accion):
    id_acc = idAccion(accion)
    return id_acc == 'd'


def esReduccion(accion):
    id_acc = idAccion(accion)
    return id_acc == 'r'


def esTransicion(accion):
    id_acc = idAccion(accion)
    return id_acc == 'Q'


def caracterValido(caracter, simbolos):
    return caracter in simbolos


""" :::: ANALIZAR CADENA :::: """


def analizar_cadena(cadena, matriz):
    fin_de_analisis = False
    cars_leidos = 0
    estado_tope = 0  # Q0
    pila = [0]
    derivaciones = []
    caracter_apuntado = cadena[cars_leidos]
    cadena = cadena + '#'
    simbolos = terminales + ['#'] + no_terminales
    if caracterValido(caracter_apuntado,simbolos):  # necesario chequear que el primer caracter de la cadena pertenece a la gramática
        columna_simb = simboloACol(caracter_apuntado, simbolos)
    else:
        resultado = __ERROR__CaracterInvalido
        fin_de_analisis = True
    # def analizarCadena por errores obvios. tiene caracteres que no estan en el alfabeto, ..., ..add reasons
    while not fin_de_analisis:
        accion = matriz[estado_tope][columna_simb]
        numero_ref = numero_de_accion(accion)  # (1) si dejo 'Acc' falla acá
        if accion == '0':
            resultado = __ERROR__Sintaxis
            fin_de_analisis = True
        elif esDeplazamiento(accion):
            # apilo el estado
            pila.append(numero_ref)
            estado_tope = numero_ref
            # avanzo en la cadena
            cars_leidos += 1  # un nombre mas apropiado sería avanzar caracter y que sea una funcion
            caracter_apuntado = cadena[cars_leidos]
            if caracterValido(caracter_apuntado, simbolos):
                columna_simb = simboloACol(caracter_apuntado, simbolos)
            else:
                resultado = __ERROR__CaracterInvalido
                fin_de_analisis = True
        elif esReduccion(accion):
            # desapilo
            (nt, prod) = DPs[numero_ref]
            derivaciones.insert(0, (nt, prod))
            cant_simbolos = len(prod)
            pila = pila[:-cant_simbolos]  # saca los ultimos cant_simbolos de la pila
            # tomo el estado que me quedó  y lo transiciono con el nt de la reduccion
            estado_tope = last(pila)
            columna_nt = simboloACol(nt, simbolos)
            temp_accion = matriz[estado_tope][columna_nt]
            pila.append(numero_de_accion(temp_accion))
            estado_tope = last(pila)
        elif accion == '17':
            resultado = "Cadena Aceptada"
            fin_de_analisis = True
    return (resultado, derivaciones)


def desapilar_n(stack, cant):
    return stack[:-cant]


def last(lista):
    return lista[-1]


""" :::::::: Matriz :::::::: """


def armarMatriz(terms, noterms, prods):
    (estados, transiciones) = generar_estados(terminales, no_terminales, producciones)  # perfecto
    (estadosNums, transNum) = estadosTransicionesNumeradas(estados, transiciones)
    matriz = matriz_de_accion(estadosNums, transNum)
    return matriz


def presentarDatos():
    print("Los datos de la gramática son: ")
    print("No terminales: ", no_terminales)
    print("Terminales: ", terminales)
    print("Simbolo Inicial: ", simboloInicial)
    print("Producciones: ")
    imprimirDerivaciones(producciones)


def derivacionUserFriendly(_deriv):
    noterm = nt(_deriv)
    produccion = prod(_deriv)
    return noterm + " --> " + produccion

def imprimirDerivaciones(derivaciones):
    num_prod = 1
    for deriv in derivaciones:  # [('A', 'Bb'), ('B', 'b')]
        print(num_prod, ". ", derivacionUserFriendly(deriv))
        num_prod += 1

def replace_last(cad, reemp_car, new_cars):
    cad = cad.rsplit(reemp_car,1) # separo en ocurrencia de reemp_car en dos listas
    return new_cars.join(cad)

def imprimirProduccionUtilizada(noterm,prod):
    return print("La produccion utilizada fue: " + derivacionUserFriendly((noterm, prod)))

def imprimirSeguimientoDerivaciones(derivaciones_de_cadena):
    print("\nLa cadena se formo siguiendo las siguientes derivaciones: \n")
    expansionCompleta = False
    i = 0
    num_prod = 1
    first_deriv = derivaciones_de_cadena[i]
    cadena_madre = prod(first_deriv)  # dela primera produccion luego se expanden los no terminales a sus respectivproducciones.
    print('1.',end=' ')
    print(derivacionUserFriendly(first_deriv), end='. ')
    imprimirProduccionUtilizada(nt(first_deriv),cadena_madre)
    while not expansionCompleta:
        # obtengo el NT a expandir y su expansion
        i+=1
        if i <= len(derivaciones_de_cadena)- 1:
            (car_a_expandir, a_que_expandir) = derivaciones_de_cadena[i]
            cad_mad_aux = cadena_madre
            cadena_madre = replace_last(cadena_madre, car_a_expandir, a_que_expandir)
            num_prod+=1
            print(str(num_prod)+". "+ cad_mad_aux + " --> " + str(cadena_madre), end='. ')
            imprimirProduccionUtilizada(car_a_expandir,a_que_expandir)
        else:
            print("Resultado: "+str(cadena_madre))
            expansionCompleta = True
    return cadena_madre

""" ******************* CODIGO PRINCIPAL ************************  """
with open(sys.argv[1], 'r+') as file:
    incorporar_datos_iniciales(file)
    DPs = crear_diccionario(producciones)
    print(':::::::::::::::::: Analizador LR(0) ::::::::::::::::::')
    presentarDatos()
    matriz = armarMatriz(terminales, no_terminales, producciones)
    continua = True
    while continua:
        continua = False
        cadena = input("\nIngrese la cadena a analizar: ")
        (resultado, derivaciones) = analizar_cadena(cadena, matriz)
        print("\n::::::::::::::::::::::::::::::::::::::::::::::::::::::\n")
        print("La evaluación de la cadena '%s'" % cadena,"arrojó:\n", resultado)
        if resultado == "Cadena Aceptada":
            print("Las derivaciones (criterio derivación más a la derecha o rightmost derivation) son las siguientes")
            imprimirDerivaciones(derivaciones)
            if input("Ingrese 'Y' si desea ver en detalle el seguimiento de la cadena: ").upper() == 'Y':
                imprimirSeguimientoDerivaciones(derivaciones)
        if input("\nIngrese 'Y' para probar con otra cadena. O cualquier otra tecla para salir del programa: ").upper() == 'Y':
            continua = True
    print("\n:::::::::::::::::::::::: Fin :::::::::::::::::::::::::")
