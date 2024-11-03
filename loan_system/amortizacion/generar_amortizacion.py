# loan_system/amortizacion/generar_amortizacion.py

def generar_tabla_amortizacion(monto, meses, interes):
    """
    Genera una tabla de amortización basada en interés fijo por periodo.

    Parámetros:
    - monto (float): Cantidad a prestar.
    - meses (int): Plazo en meses.
    - interes (float): Porcentaje de interés anual.

    Retorna:
    - lista de diccionarios con los detalles de cada periodo.
    """
    tabla = []
    P = monto
    R = interes
    I = P * R / 100  # Interés total anual
    T = P + I         # Total a pagar
    cuota = round(T / meses, 2)  # Cuota mensual
    interes_mensual = round(I / meses, 2)  # Interés mensual fijo
    capital_mensual = round(cuota - interes_mensual, 2)  # Capital mensual
    saldo = T  # Saldo inicial es el total a pagar

    for periodo in range(1, meses + 1):
        saldo = round(saldo - cuota, 2)
        if saldo < 0:
            saldo = 0.00
        tabla.append({
            'Periodo': periodo,
            'Cuota': cuota,
            'Interés': interes_mensual,
            'Capital': capital_mensual,
            'Saldo': saldo
        })
    return tabla
