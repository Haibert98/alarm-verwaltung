import matplotlib.pyplot as plt
import sys

def draw(xwert:list, ywert:list):
    plt.figure(figsize=(13, 8))
    
    plt.title("Herzfrequenz des Patienten", )
    plt.ylabel("Herzfrequenz in bpm")
    
    plt.xticks(rotation=30)
    plt.xlabel("Zeit")
    plt.yticks([0,20,40,60,80,100,120,140,160,180,200]) # Y-Achsen Beschriftung
    plt.ylim(0,200) # Y-Achsen Skalierung
    plt.grid(axis='y') # Gitterlinie für Y-Achse
    plt.rc('font', size=17)          # controls default text sizes
    plt.rc('axes', titlesize=100)     # fontsize of the axes title
    plt.rc('axes', labelsize=100)    # fontsize of the x and y labels
    plt.rc('xtick', labelsize=100)    # fontsize of the tick labels
    plt.rc('ytick', labelsize=100)    # fontsize of the tick labels
    plt.rc('legend', fontsize=100)    # legend fontsize
    plt.rc('figure', titlesize=100)  # fontsize of the figure title
    plt.plot(xwert, ywert, "o--") # gestrichelte Linie mit Datenpunkten
    plt.savefig('/home/projectuser/projectlp/heartbeat.png')
    # plt.savefig('F:/alarm-unterstuetzung/src/Webserver/seite/heartbeat.png')


if __name__ == '__main__':
    xwert = []
    ywert = []
    puls = ""
    ts = ""
    if len(sys.argv) < 3:
        raise
    else:
        length = int((len(sys.argv)-1)/2)
        for i in range(length):
            puls = sys.argv[1+i]
            ts = sys.argv[length+1+i]
            if "[" in puls:
                 puls = puls.replace("[", "")
            if "," in puls:
                puls = puls.replace(",", "")
            if "]" in puls:
                puls = puls.replace("]", "")
            ywert.append(int(puls))
            if "[" in ts:
                 ts = ts.replace("[", "")
            if "," in ts:
                ts = ts.replace(",", "")
            if "]" in ts:
                ts = ts.replace("]", "")
            xwert.append(str(ts))
        draw(xwert, ywert)
