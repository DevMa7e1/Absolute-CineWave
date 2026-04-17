import tkinter as tk
import pvspeaker
import math
import re

window = tk.Tk()
window.wm_title("Absolute CineWave")

sampleRate = 48000
sampleBits = 16
sampleMax = 2**sampleBits / 2 - 1
pv = pvspeaker.PvSpeaker(sampleRate, sampleBits)
pv.start()

def mod_or_one(a, b):
    if a == b*2:
        return sampleRate
    else:
        return a % (b*2)

def sine_wave(freq: int, time: int, amplitude: float):
    return int(round(math.sin(mod_or_one(time, 1/freq*sampleRate/2) / (1/freq*sampleRate/2) * math.pi), 8) * (sampleMax * amplitude))

def limit(value, limit):
    if value > limit * sampleMax:
        return int(limit * sampleMax)
    if value < -limit * sampleMax:
        return int(-limit * sampleMax)
    return value

freq, time = 0, 0

def amplify(value, factor):
    return limit(int(value * factor), 1)

wave = []

def play_sound():
    global textInput, freq, time, wave
    code = textInput.get("1.0", "end-1c")
    wave.clear()
    freq = 330
    for i in code.split("\n"):
        matches = re.match("(.*) ->", i)
        if(matches != None):
            code = code.replace(i, f"wave.append({str(matches[1])})")
    for i in range(sampleRate * 2):
        time = i
        exec(code)
    pv.write(wave)
    pv.flush()
    

label = tk.Label(window, text="Sound 1")
textInput = tk.Text()
button = tk.Button(text="Play", command=play_sound)
label.pack()
textInput.pack()
button.pack()
window.mainloop()