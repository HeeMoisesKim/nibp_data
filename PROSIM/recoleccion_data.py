from re import A
from datetime import datetime
from turtle import delay
import serial
import time
import re
import json
import sys


def millis(): return int(round(time.time() * 1000))


def EsfigmoREC():
    sis = 0
    dia = 0
    t_total = 0
    t_inicio = millis()  # inicio a contar el tiempo
    flag_esfigmo = 1  # variable que mantiene el ciclo

    try:  # si se realizó bien la conexión con el esp32 trata de conectar con el esfigmo
        # establecer conexión con el serial del esfigmo
        ser2 = serial.Serial('/dev/ESFIGMO', 115200, timeout=10)
        ser2.flush()

    # enviar a ubidots que está conectado el esfigmo
    #   payload = {"pressure": {"value": 1, "context": {"comment": "connected"}}}
    except serial.SerialException:
        print("fallo conexion")

    time.sleep(2)

    ser2.write(b"inflar\n")  # enviar al micro que inicie la medicióndz
    while flag_esfigmo == 1:  # entro en el ciclo hasta que recibo los datos del esfigmo, error o alcanzo el tiempo límite
        t_final = millis()
        t_total = t_final - t_inicio  # contar el tiempo total

        try:

            if ser2.in_waiting > 0:
                line = ser2.readline().decode('utf-8')  # leer puerto serial 2 (esfigmo)
                if "pulso:" in line:
                    pulso = line
                    print(pulso)
                line = ser2.readline().decode('utf-8').rstrip()  # leer puerto serial 2 (esfigmo)
                if "presion:" in line:
                    presion = line
                    print(presion)
                line = ser2.readline().decode('utf-8').rstrip()
                if line == "nibp":  # mediciones correctas de esfigmo
                    sis = ser2.readline().decode('utf-8').rstrip()  # obtener valor presión  sistólica
                    dis = ser2.readline().decode('utf-8').rstrip()  # obtener valor presión diastólica
                    sis = float(sis)  # convertir a float
                    print(sis)
                    dis = float(dis)  # convertir a float
                    print(dis)
                    flag_esfigmo = 0  # salir del ciclo
                    # print(complete)

                    if (sis > 200 or sis < 0) or (dia > 200 or dia < 0):
                        event = 3.5  # medición fuera de rango esfigmo
                elif line == "b":  # error porque no se colocó el brazo
                    flag_esfigmo = 0  # salir del ciclo
                    event = 3.5  # medición fuera de rango esfigmo
                elif line == "f":  # error porque se llenó el buffer
                    flag_esfigmo = 0  # salir del ciclo
                    event = 3.55  # error esfigmo
                elif line == "d":  # error porque el micro murió
                    event = 3.55  # error esfigmo
            if t_total > 150000:  # espera 150 segundos para poder salir del ciclo si el comando no llego al esp32
                event = 3.55  # error esfigmogmo)
                flag_esfigmo = 0

        except:
            flag_esfigmo = 0
            print("no mayor que 0")

    return pulso, presion, sis, dis


def RecordEsfigmoTry(bpm, cc, diametro, DiastolicaTeorica, SiastolicaTeorica, VEsfigmo, NoGrabacion, NoN, pulso, presion, sis, dis):

    flag_bpm = 0
    flag_cc = 0
    flag_brazo = 0
    t1 = "Genero correcto"
    t2 = "dad correcta"
    t3 = "Peso correcto"
    t4 = "Version Correcta"
    pulso2 = []
    presion2 = []

    DiastolicaTeorica = int(DiastolicaTeorica)
    SiastolicaTeorica = int(SiastolicaTeorica)
    VEsfigmo = float(VEsfigmo)

    if VEsfigmo < 0.0 or VEsfigmo > 20.0:
        t4 = "Version no aceptada"
        flag_vesfigmo = 1
    else:
        Vesfigmo = str(VEsfigmo)

    date = datetime.now().date()
    date = str(date)

    pulso = pulso.split(',')
    presion = presion.split(',')

    for i in range(0, len(pulso)-1):
        pulso2.append(int(re.search(r'\d+', pulso[i]).group(0)))

    for j in range(0, len(pulso)-1):
        presion2.append(int(re.search(r'\d+', presion[j]).group(0)))

    record = {
        "pulse": pulso2,
        "pressure": presion2,
        "Sistolic": sis,
        "Diastolic": dis,
        "BPM": bpm,
        "CC": cc,
        "D_brazo": diametro,
        "TheoricalSistolic": SiastolicaTeorica,
        "TheoricalDiastolic": DiastolicaTeorica}
    print(record)
    with open('subject'+'_'+NoN+'_'+'Rec' + NoGrabacion + '_' + 'VEsfigmo'+Vesfigmo + '_' + date+'.json', 'w') as fp:
        json.dump(record, fp)


pulso, presion, sis, dis = EsfigmoREC()


# def RecordEsfigmoTry(bpm, cc, diametro, DiastolicaTeorica, SiastolicaTeorica, VEsfigmo, NoGrabacion, NoN):
RecordEsfigmoTry(sys.argv[1], sys.argv[2],
                 sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], sys.argv[7], sys.argv[8], pulso, presion, sis, dis)
