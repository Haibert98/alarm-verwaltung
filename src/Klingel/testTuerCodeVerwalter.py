from numpy import var
from src.tuerCodeVerwalter import  on_message
import time

class Msg():
    def __init__(self, str):
        self.topic = str

msg = Msg("CodeErstellen")


#je nach variante werden msgs geschickt, aufraeumen sollte 0 < 1 < 2 schnell auftreten
def test(variante=0):
    for i in range(10):
        if variante == 1:
           if i < 3 and i%2==0:
                on_message(None, None, msg)
        elif variante == 2: 
            if i < 5 and i%2==0:
                on_message(None, None, msg)
        print(i)
        time.sleep(1)


on_message(None, None, msg)
time.sleep(1)

test(variante=1)
