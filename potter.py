from threading import Timer

class Tick_tack(object):
    def __init__(self, interval, function, *args, **kwargs):
        self._timer     = None
        self.interval   = interval
        self.function   = function
        self.args       = args
        self.kwargs     = kwargs
        self.is_running = False
        self.start()

    def _run(self):
        self.is_running = False
        self.start()
        self.function(*self.args, **self.kwargs)

    def start(self):
        if not self.is_running:
            self._timer = Timer(self.interval, self._run)
            self._timer.start()
            self.is_running = True

    def stop(self):
        self._timer.cancel()
        self.is_running = False
hacky_hacky = [0]
tick_buf = 0

def tick():
    hacky_hacky[0] ^= 1
rt = Tick_tack(1, tick)

from rpi_hardware_pwm import HardwarePWM
pwm = HardwarePWM(0, hz=60)
pwm.start(0) # full duty cycle
#pwm.change_duty_cycle(50)
#pwm.stop()

import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)  

CH_A = 23 #CH.A GRAY
CH_B = 24 #CH.B PURPLE
BUTTON_CLICK = 4 #SW ORANGE 0 on click
CLK = 22 #CLK GREEN
DT =  27 #DT YELLOW

# Setup your channel
GPIO.setup(CH_A, GPIO.IN)
GPIO.setup(CH_B, GPIO.IN)
GPIO.setup(BUTTON_CLICK, GPIO.IN)
GPIO.setup(CLK, GPIO.IN)
GPIO.setup(DT, GPIO.IN)

GPIO.setup(CH_A, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(CH_B, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BUTTON_CLICK, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(CLK, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(DT, GPIO.IN, pull_up_down=GPIO.PUD_UP)

btn = False



speed_req = 0
is_left = False
is_right = False
knob_transit = False

pos = 0
motor_on_move = False
motor_is_left = False
motor_is_right = False

"""
RIGHT
CLK DT
1   1   CLK_1_DT_1
1   0   CLK_1_DT_0
0   0   CLK_0_DT_0
1   1   CLK_1_DT_1
LEFT
CLK DT
1   1   CLK_1_DT_1
0   1   CLK_0_DT_1
0   0   CLK_0_DT_0
1   1   CLK_1_DT_1

"""
while(1):
    """BUTTON"""
    if not GPIO.input(BUTTON_CLICK) and not btn:
        btn ^= 1
        print("BUTTON_CLICK")
    if  GPIO.input(BUTTON_CLICK) and  btn:
        btn ^= 1
        speed_req = 0
        print("BUTTON_UP")
        
    CLK_ = GPIO.input(CLK)
    DT_ = GPIO.input(DT)
    # print("CLK: ",CLK_,"   DT: ",DT_)
    # print(speed_req)
    """SET SPEED"""
    if CLK_ and DT_ :
        if knob_transit and is_right:
            # print("left")
            if speed_req > 0 and speed_req <= 100:
                speed_req -= 5
        if knob_transit and is_left:
            # print("right")
            if speed_req >= 0 and speed_req < 100:
                speed_req += 5
        knob_transit = False
        is_left = False
        is_right = False
    if CLK_ and not DT_:
        is_right = True    
        is_left = False 
    if not CLK_ and  DT_:
        is_left = True   
        is_right = False
    if not CLK_ and not DT_:
        knob_transit = True
        
    if speed_req >= 0 and speed_req <= 100:
        pwm.change_duty_cycle(speed_req)
    """READ SPEED"""
    CH_A_ = GPIO.input(CH_A)
    CH_B_ = GPIO.input(CH_B)

    # print("CH_A_: ",CH_A_,"  CH_B_: ",CH_B_)
    if CH_A_ and CH_B_ :
        if motor_on_move and motor_is_right:
            # print("right")
            pos+=1
        if motor_on_move and motor_is_left:
            # print("left")
            pos+=1

        motor_on_move = False
        motor_is_left = False
        motor_is_right = False
    if CH_A_ and not CH_B_:
        motor_is_right = True    
        motor_is_left = False 
    if not CH_A_ and  CH_B_:
        motor_is_left = True   
        motor_is_right = False
    if not CH_A_ and not CH_B_:
        motor_on_move = True

    if tick_buf != hacky_hacky[0]:
        tick_buf = hacky_hacky[0]
        print(round(pos/100*60))
        pos = 0
