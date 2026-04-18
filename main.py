import tkinter as tk
import tkinter.messagebox
import pvspeaker
import re
from audio_functions import *
from extras import *
from threading import Thread
from functools import partial
#For debugging purposes
#import matplotlib.pyplot as plt

window = tk.Tk()
window.wm_title("Absolute CineWave")

pv = pvspeaker.PvSpeaker(sampleRate, sampleBits)
pv.start()

time = Time()

def play_sound(name: str, freq: int):
    global wave, sounds
    code = sounds[name][1]
    wave.clear()
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
        sounds[name] = [code, compiled]
    except Exception as e:
        tkinter.messagebox.showerror("Syntax error", str(e))

def open_sound(name: str):
    sound_window = tk.Toplevel()
    sound_window.wm_title(f"{name}: Absolute CineWave")
    code_input = tk.Text(sound_window)
    code_input.insert(tk.END, sounds[name][0])
    save_button = tk.Button(sound_window, text="Save", command=partial(save_code, code_input, name))
    play_button = tk.Button(sound_window, text="Play", command=partial(play_sound, name, 330))
    code_input.pack()
    save_button.pack()
    play_button.pack()

def create_sound(name: str):
    global sounds
    sounds[name] = ["", None]
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

button = tk.Button(window, text="New sound", command=new_sound)
button.pack()
window.mainloop()