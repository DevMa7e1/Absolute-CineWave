import tkinter as tk
import pvspeaker
import re
from audio_functions import *
from extras import *
from threading import Thread
#For debugging purposes
#import matplotlib.pyplot as plt

window = tk.Tk()
window.wm_title("Absolute CineWave")

pv = pvspeaker.PvSpeaker(sampleRate, sampleBits)
pv.start()

freq, time = 0, Time()

def play_sound():
    global textInput, freq, time, wave
    code = textInput.get("1.0", "end-1c")
    wave.clear()
    freq = 330
    popup = tk.Toplevel()
    popup.wm_title("Processing...")
    info_label = tk.Label(popup, text="Processing your code...")
    info_label.pack()
    window.update()
    popup.update()
    for i in code.split("\n"):
        tabs = 0
        matches = re.match("(.*) ->", i)
        if(matches != None and len(matches.groups())):
            tabs = i.count('\t')
            code = code.replace(i, f"{'\t'*tabs}wave.append({str(matches[1])})")
    time = Time()
    for i in range(sampleRate * 2):
        if i % 1000 == 0:
            progress = i / (sampleRate * 2)
            info_label.config(text=f"Computing\n[{'='*(int(progress*20)-1)}>{' '*(20-int(progress*20))}]")
            window.update()
            popup.update()
        exec(code)
        time.increment()
    #Debugging
    #plt.plot(wave)
    #plt.show()
    #input(">")
    popup.destroy()
    window.update()
    popup.update()
    pv.write(wave)
    Thread(target=pv.flush).start()

label = tk.Label(window, text="Sound 1")
textInput = tk.Text()
button = tk.Button(text="Play", command=play_sound)
label.pack()
textInput.pack()
button.pack()
window.mainloop()