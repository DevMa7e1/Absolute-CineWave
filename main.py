import tkinter as tk
import tkinter.messagebox
import pvspeaker
import re
from audio_functions import *
from extras import *
from threading import Thread
from functools import partial
from pathlib import Path
#For debugging purposes
#import matplotlib.pyplot as plt

window = tk.Tk()
window.wm_title("Absolute CineWave")

pv = pvspeaker.PvSpeaker(sampleRate, sampleBits)
pv.start()

time = Time()

def compute_sound(name: str, freq: int):
    global sounds
    code = sounds[name][1]
    wave = []
    popup = tk.Toplevel()
    popup.wm_title("Processing...")
    info_label = tk.Label(popup, text="Processing your code...")
    info_label.pack()
    window.update()
    popup.update()
    time = Time()
    for i in range(sampleRate * 2):
        if i % 1000 == 0:
            progress = i / (sampleRate * 2)
            info_label.config(text=f"Computing\n[{'='*(int(progress*20)-1)}>{' '*(20-int(progress*20))}]")
            window.update()
            popup.update()
        try:
            exec(code)
        except Exception as e:
            tkinter.messagebox.showerror("Code execution error", str(e))
            popup.destroy()
            window.update()
            popup.update()
            raise Exception(f"Execution error: {str(e)}")
        time.increment()
    #Debugging
    #plt.plot(wave)
    #plt.show()
    #input(">")
    popup.destroy()
    window.update()
    popup.update()
    return wave

def play_wave(wave: list):
    global pv
    pv.write(wave)
    pv.flush()
    #Thread(target=pv.flush).start()

def play_sound(name: str):
    global sounds, frequencies
    notes = sounds[name][2]
    for x in range(len(notes[0])):
        wave = []
        for y in range(12):
            if notes[y][x]:
                if wave == []:
                    wave = compute_sound(name, frequencies[11-y])
                else:
                    wave2 = compute_sound(name, frequencies[11-y])
                    for i in range(len(wave)):
                        wave[i] = limit(wave[i]+wave2[i], 1)
        if wave != []:
            play_wave(wave)
        

sounds = {}

def save_code(code_input: tk.Text, name: str):
    global sounds
    code = code_input.get("1.0", "end-1c")
    for i in code.split("\n"):
        tabs = 0
        matches = re.match("(.*) ->", i)
        if(matches != None and len(matches.groups())):
            tabs = i.count('\t')
            code = code.replace(i, f"{'\t'*tabs}wave.append({str(matches[1])})")
    compiled = None
    try:
        compiled = compile(code, name, 'exec')
        sounds[name] = [code, compiled, sounds[name][2]]
    except Exception as e:
        tkinter.messagebox.showerror("Syntax error", str(e))

def open_sound(name: str):
    sound_window = tk.Toplevel()
    sound_window.wm_title(f"{name}: Absolute CineWave")
    code_input = tk.Text(sound_window)
    code_input.insert(tk.END, sounds[name][0])
    save_button = tk.Button(sound_window, text="Save", command=partial(save_code, code_input, name))
    play_button = tk.Button(sound_window, text="Open Piano Roll", command=partial(play_window, name))
    code_input.pack()
    save_button.pack()
    play_button.pack()

def create_sound(name: str):
    global sounds
    sounds[name] = ["", None, []]
    new_button = tk.Button(window, text=name, command=partial(open_sound, name))
    new_button.pack()

def fancy_text_getter_and_passer(name_input: tk.Text, window: tk.Toplevel):
    name = name_input.get("1.0", "end-1c")
    window.destroy()
    create_sound(name)

def new_sound():
    dialogue = tk.Toplevel()
    dialogue.wm_title("Create a sound")
    name_label = tk.Label(dialogue, text="The name of the new sound:")
    name_input = tk.Text(dialogue, height=1, width=25)
    name_input.insert(tk.END, f"Sound {str(len(sounds)+1)}")
    create_button = tk.Button(dialogue, text="Create", command=partial(fancy_text_getter_and_passer, name_input, dialogue))
    name_label.pack()
    name_input.pack()
    create_button.pack()

blue = tk.PhotoImage(file=Path(__file__).parent.absolute().joinpath('blue.png'))
gray = tk.PhotoImage(file=Path(__file__).parent.absolute().joinpath('gray.png'))

def select_note(x: int, y: int, name:str, button: tk.Button):
    global blue, gray, sounds
    sounds[name][2][x][y] = not sounds[name][2][x][y]
    if sounds[name][2][x][y]:
        button.config(image=blue)
    else:
        button.config(image=gray)

letter_notation = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
frequencies = [261.63, 277.18, 293.66, 311.13, 329.63, 349.23, 369.99, 392, 415.30, 440, 466.16, 493.88]

def play_window(name: str):
    global notes, blue, gray, sounds
    pwindow = tk.Toplevel()
    pwindow.wm_title("Absolute CineWave: Piano roll")
    if(sounds[name][2] == []):
        for i in range(12):
            sounds[name][2].append([])
            for j in range(16):
                sounds[name][2][-1].append(False)
    for x in range(12):
        note_label = tk.Label(pwindow, text=letter_notation[11-x])
        note_label.grid(row=x, column=0)
    for x in range(12):
        for y in range(16):
            if sounds[name][2][x][y]:
                new_button = tk.Button(pwindow, image=blue, padx=4, pady=4)
            else:
                new_button = tk.Button(pwindow, image=gray, padx=4, pady=4)
            new_button.config(command=partial(select_note, x, y, name, new_button))
            new_button.grid(row=x, column=y+1)
    play_button = tk.Button(pwindow, text="Play", command=partial(play_sound, name))
    play_button.grid(row=12, column=0)
    

button = tk.Button(window, text="New sound", command=new_sound)
button.pack()
window.mainloop()