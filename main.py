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

class Time:
    def __init__(self, start_seconds: float = 0, start_pcm_frames: int = 0):
        global sampleRate
        self._time = int(start_seconds * sampleRate) + start_pcm_frames
    def __call__(self, *args, **kwds):
        return self.seconds()
    def seconds(self):
        global sampleRate
        return self._time / sampleRate
    def pcm_frames(self):
        return self._time
    def increment(self, step = 1):
        self._time += step

def mod_or_one(a, b):
    if a == b*2:
        return sampleRate
    else:
        return a % (b*2)

def sine_wave(freq: int, time: Time, amplitude: float):
    if(amplitude <= 1 and amplitude >= 0):
        return int(round(math.sin(mod_or_one(time.pcm_frames(), 1/freq*sampleRate/2) / (1/freq*sampleRate/2) * math.pi), 8) * (sampleMax * amplitude))

def limit(value: int, limit: int):
    if value > limit * sampleMax:
        return int(limit * sampleMax)
    if value < -limit * sampleMax:
        return int(-limit * sampleMax)
    return value

freq, time = 0, Time()

def amplify(value: int, factor: float):
    return limit(int(value * factor), 1)

wave = []

def echo(time: Time, difference: Time):
    global wave
    if(time.pcm_frames() >= difference.pcm_frames()):
        return wave[time.pcm_frames()-difference.pcm_frames()]
    else:
        return 0
def play_sound():
    global textInput, freq, time, wave
    code = textInput.get("1.0", "end-1c")
    wave.clear()
    freq = 330
    for i in code.split("\n"):
        tabs = 0
        matches = re.match("(.*) ->", i)
        if(matches != None and len(matches.groups())):
            tabs = i.count('\t')
            code = code.replace(i, f"{'\t'*tabs}wave.append({str(matches[1])})")
    time = Time()
    for i in range(sampleRate * 2):
        exec(code)
        time.increment()
    pv.write(wave)
    pv.flush()

label = tk.Label(window, text="Sound 1")
textInput = tk.Text()
button = tk.Button(text="Play", command=play_sound)
label.pack()
textInput.pack()
button.pack()
window.mainloop()