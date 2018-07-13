import time.sleep as sleep
import Adafruit_PCA9685

pwm = Adafruit_PCA9685.PCA9685()

Repouso = (90, 90, 90)
Marcas = ((43, 42, 120), (92, 42, 146), (145, 42, 114),
          (53, 38, 84), (93, 42, 100), (130, 35, 72),
          (65, 28, 45), (90, 26, 36), (115, 28, 38))
mot0 = [0, Repouso[0], Repouso[0]]
mot1 = [4, Repouso[1], Repouso[1]]
mot2 = [8, Repouso[2], Repouso[2]]
abre = 30
pega = 10


def set_pos(num_pos):
    if isinstance(num_pos, int):
        if 0 <= num_pos <= 9:
            ctrlMotor(*Marcas[num_pos])
        else:
            raise Exception('Position out of limits!')
    else:
        raise ValueError('Value {} is not a integer!'.format(num_pos))


def set_pos(tuple_pos):
    if isinstance(tuple_pos, tuple) or isinstance(tuple_pos, list):
        if len(tuple_pos > 3):
            if 0 <= tuple_pos[0] <= 180 or 0 <= tuple_pos[1] <= 180 or 0 <= tuple_pos[2] <= 180:
                ctrlMotor(tuple_pos)
            else:
                raise Exception('Some angule on {} is out of range!'.format(tuple_pos))
        else:
            raise Exception('Tuple of angules can not have more than 3 elements!')
    else:
        raise ValueError('{} Is not a tuple or list'.format(tuple_pos))


def abrir():
    moverMotor(12, abre)


def pega():
    moverMotor(12, pega)


def set_repouso():
    ctrlMotor(*Repouso)


def ctrlMotor(*tuple_pos):
    mot0[2], mot1[2], mot2[2] = tuple_pos

    while True:
        '''
        Enquanto a diferença entre a pos_escrita e a pos_desejada de cada motor for maior que 0, ou seja,
        Enquanto o motor ainda nao tiver alcançado a pos_desejada, diminui ou aumenta o angulo do motor conforme o caso.
        '''
        # tratamento do motor 0
        if abs(mot0[1] - mot0[2]) > 10:
            print("IF mot0")
            # Se a pos_escrita for menor que a pos_desejada, aumenta em 1 o valor da pos_escrita
            if mot0[1] < mot0[2]:
                mot0[1] += (mot0[1] + mot0[2])/10
            else:
                # caso contrario, diminui a pos_escrita em 1 unidade.
                mot0[1] -= (mot0[1] + mot0[2])/10
        else:
            print("OK mot0")
        # tratamento do motor 1
        if abs(mot1[1] - mot1[2]) > 10:
            print("IF mot1")
            if mot1[1] < mot1[2]:
                mot1[1] += (mot1[1] + mot1[2])/10
            else:
                mot1[1] -= (mot1[1] + mot1[2])/10
        else:
            print("OK mot1")
        # tratamento do motor 2
        # o motor 2, recebe uma alteração de valor de 2 unidades, pois no nosso caso isso evita travamentos
        if abs(mot2[1] - mot2[2]) > 10:
            print("IF mot2")
            if mot2[1] < mot2[2]:
                mot2[1] += (mot2[1] + mot2[2])/10
            else:
                mot2[1] -= (mot2[1] + mot2[2])/10
        else:
            print("OK mot2")
        # Verifica se nao existe diferença entre a pos_escrita e pos_desejada de cada um dos motores
        if (abs(mot0[1] - mot0[2]) != 0) and (abs(mot1[1] - mot1[2]) != 0) and (abs(mot2[1] - mot2[2]) >= 2):
            print("MOTOR: " + str(mot0[0]) + "ANGULO: " + str(mot0[1]))
            moverMotor(mot0[0], mot0[1])
            print("MOTOR: " + str(mot1[0]) + "ANGULO: " + str(mot1[1]))
            moverMotor(mot1[0], mot1[1])
            print("MOTOR: " + str(mot2[0]) + "ANGULO: " + str(mot2[1]))
            moverMotor(mot2[0], mot2[1])

        else:
            print("SAINDO LAÇO CTRL")
            set_repouso()
            break


def moverMotor(motor, posicao):
    def ajuste(x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    mover = True
    if motor == 0:
        posWt = ajuste(posicao, 0, 180, 150, 550)
        # Define os minimos e maximos de cada motor, para evitar travamento,
        # esses valores foram definidos manualmente com base em testes.
        if (posWt < 148) or (posWt > 560):
            mover = False
    if motor == 4:
        posWt = ajuste(posicao, 0, 90, 300, 545)
        if (posWt < 150) or (posWt > 580):
            mover = False
    if motor == 8:
        posWt = ajuste(posicao, 0, 160, 121, 480)
        if (posWt < 121) or (posWt > 480):
            mover = False

    if motor == 12:
        posWt = ajuste(posicao, 0, 60, 540, 310)
        if (posWt < 350) or (posWt > 540):
            mover = False
    if mover:
        # funcao da bibliteca Adafruit, que escreve o valor PWM em determinada porta.
        pwm.setPWM(motor, 0, posWt)
        sleep(0.03)
