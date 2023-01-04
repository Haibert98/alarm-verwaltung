import string
import random
class TokenGenerator():

    def generiere():
        key = ""
        #bestimmt laenge des keys
        for i in range(0, 15):
            #entscheidung zwischen int oder char
            coin = random.randint(0,1)
            if coin == 0:
                key = key+str(random.randint(0,9))
            else:
                key = key+random.choice(string.ascii_letters)


        #fertige key
        return key