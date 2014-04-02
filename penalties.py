import serial
import time

if __name__ == '__main__':
    '''
    Shoots penalty shot
    '''
    comm = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
    comm.write('A_RUN_CATCH\n')
    time.sleep(0.1)
    comm.write('A_RUN_KICK\n')
    comm.write('A_RUN_ENGINE %d %d\n' % (0, 0))

