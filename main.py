import tkinter as tk
import tkinter.filedialog
import tkinter.messagebox
import pvspeaker
import re
from audio_functions import *
from extras import *
from threading import Thread
from functools import partial
from pathlib import Path
from time import sleep
import wave
import array
#For debugging purposes
#import matplotlib.pyplot as plt

window = tk.Tk()
window.wm_title("Absolute CineWave")

pv = pvspeaker.PvSpeaker(sampleRate, sampleBits)
pv.start()

time = Time()

def compute_sound(name: str, freq: int, frames: int, progress_window: tk.Toplevel, progress_label: tk.Label):
    global sounds
    code = sounds[name][1]
    wave = []
    time = Time()
    for i in range(frames):
        if i % 1000 == 0:
            progress = i / (frames)
            progress_label.config(text=f"Computing\n[{'='*(int(progress*20)-1)}>{' '*(20-int(progress*20))}]")
            progress_window.update()
        try:
            exec(code)
        except Exception as e:
            tkinter.messagebox.showerror("Code execution error", str(e))
            raise Exception(f"Execution error: {str(e)}")
        time.increment()
    #Debugging
    #plt.plot(wave)
    #plt.show()
    #input(">")
    return wave

def play_sound(name: str):
    global sounds, frequencies, pv, tempo
    notes = sounds[name][2]
    waves = {}
    pwindow = tk.Toplevel()
    pwindow.minsize(200, 75)
    pwindow.maxsize(200, 75)
    pwindow.wm_title("Computing sounds...")
    progress_label = tk.Label(pwindow)
    progress_label2 = tk.Label(pwindow)
    progress_label.pack()
    progress_label2.pack()
    progress_label.config(text="Preparing to compute notes...")
    pwindow.update()
    totalprogress = 0
    for i in notes:
        if not i[1] in waves.keys():
            waves[i[1]] = compute_sound(name, frequencies[11-i[0]], int(60 / tempo * sampleRate), pwindow, progress_label2)
        else:
            wave = compute_sound(name, frequencies[11-i[0]], int(60 / tempo * sampleRate), pwindow, progress_label2)
            for j in range(int(60 / tempo * sampleRate)):
                waves[i[1]][j] = limit(waves[i[1]][j] + wave[j], 1)
        totalprogress += 1
        progress_label.config(text=f"Computed {totalprogress}/{len(notes)}.")
        pwindow.update()
    pwindow.destroy()
    window.update()
    keys = sorted(list(waves.keys()))
    for i in range(len(keys)):
        pv.write(waves[keys[i]])
        Thread(target=pv.flush).start()
        if(i < len(keys)-1):
            sleep(60 / tempo * (keys[i+1] - keys[i]))
        else:
            sleep(60 / tempo)

sounds = {}
tempo = 60

def save_code(code_input: tk.Text, name: str):
    global sounds
    code = code_input.get("1.0", "end-1c")
    code2 = code_input.get("1.0", "end-1c")
    for i in code.split("\n"):
        tabs = 0
        matches = re.match("(.*) ->", i)
        if(matches != None and len(matches.groups())):
            tabs = i.count('\t')
            code = code.replace(i, f"{'\t'*tabs}wave.append({str(matches[1])})")
    compiled = None
    try:
        compiled = compile(code, name, 'exec')
        sounds[name] = [code2, compiled, sounds[name][2]]
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

def select_note(x: int, y: int, name: str, button: tk.Button):
    global blue, gray, sounds
    if (x, y) in sounds[name][2]:
        sounds[name][2].remove((x, y))
        button.config(image=gray)
    else:
        sounds[name][2].append((x, y))
        button.config(image=blue)
        

letter_notation = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
frequencies = [261.63, 277.18, 293.66, 311.13, 329.63, 349.23, 369.99, 392, 415.30, 440, 466.16, 493.88]

def forwards(buttonself: tk.Button, buttons, pwindow: tk.Toplevel, poslabel: tk.Label, name: str):
    poslabel.config(text=str(int(poslabel.cget("text"))+1))
    position = int(poslabel.cget("text"))
    for i in buttons:
        i.destroy()
    for x in range(12):
        for y in range(16):
            if (x, y+position) in sounds[name][2]:
                new_button = tk.Button(pwindow, image=blue, padx=4, pady=4)
                buttons.append(button)
            else:
                new_button = tk.Button(pwindow, image=gray, padx=4, pady=4)
                buttons.append(button)
            new_button.config(command=partial(select_note, x, y+position, name, new_button))
            new_button.grid(row=x, column=y+1)
    buttonself.config(command=partial(forwards, buttonself, buttons, pwindow, poslabel, name))

def backwards(buttonself: tk.Button, buttons, pwindow: tk.Toplevel, poslabel: tk.Label, name: str):
    if(int(poslabel.cget("text")) > 0):
        poslabel.config(text=str(int(poslabel.cget("text"))-1))
        position = int(poslabel.cget("text"))
        for x in range(12):
            for y in range(16):
                if (x, y+position) in sounds[name][2]:
                    new_button = tk.Button(pwindow, image=blue, padx=4, pady=4)
                    buttons.append(button)
                else:
                    new_button = tk.Button(pwindow, image=gray, padx=4, pady=4)
                    buttons.append(button)
                new_button.config(command=partial(select_note, x, y+position, name, new_button))
                new_button.grid(row=x, column=y+1)
    buttonself.config(command=partial(backwards, buttonself, buttons, pwindow, poslabel, name))

def play_window(name: str):
    global notes, blue, gray, sounds
    position = 0
    buttons = []
    pwindow = tk.Toplevel()
    pwindow.wm_title("Absolute CineWave: Piano roll")
    for x in range(12):
        note_label = tk.Label(pwindow, text=letter_notation[11-x])
        note_label.grid(row=x, column=0)
    for x in range(12):
        for y in range(16):
            if (x+position, y) in sounds[name][2]:
                new_button = tk.Button(pwindow, image=blue, padx=4, pady=4)
                buttons.append(button)
            else:
                new_button = tk.Button(pwindow, image=gray, padx=4, pady=4)
                buttons.append(button)
            new_button.config(command=partial(select_note, x+position, y, name, new_button))
            new_button.grid(row=x, column=y+1)
    play_button = tk.Button(pwindow, text="Play", command=partial(play_sound, name))
    position_label = tk.Label(pwindow, text="0")
    forwards_button = tk.Button(pwindow, text=">")
    forwards_button.config(command=partial(forwards, forwards_button, buttons, pwindow, position_label, name))
    backwards_button = tk.Button(pwindow, text="<")
    backwards_button.config(command=partial(backwards, backwards_button, buttons, pwindow, position_label, name))
    play_button.grid(row=12, column=0)
    forwards_button.grid(row=12, column=2)
    backwards_button.grid(row=12, column=1)
    position_label.grid(row=12, column=17)

def set_tempo():
    global tempo_input, tempo
    try:
        tempo = float(tempo_input.get())
    except Exception as e:
        tkinter.messagebox.showerror("Tempo error", "The value entered is not a number or Python can't process it.")
        tkinter.messagebox.showerror("Tempo error", str(e))

def play_all():
    global sounds, frequencies, pv, tempo, window
    pwindow = tk.Toplevel()
    pwindow.wm_title("Computing sounds...")
    pwindow.minsize(200, 75)
    pwindow.maxsize(200, 75)
    progress_label = tk.Label(pwindow)
    progress_label2 = tk.Label(pwindow)
    progress_label.pack()
    progress_label2.pack()
    progress_label.config(text="Preparing to compute notes...")
    waves = {}
    totalprogress = 0
    total = 0
    for i in sounds.keys():
        total += len(sounds[i][2])
    for sound in sounds.keys():
        name = sound
        notes = sounds[name][2]
        window.update()
        for i in notes:
            if not i[1] in waves.keys():
                waves[i[1]] = compute_sound(name, frequencies[11-i[0]], int(60 / tempo * sampleRate), pwindow, progress_label2)
            else:
                wave = compute_sound(name, frequencies[11-i[0]], int(60 / tempo * sampleRate), pwindow, progress_label2)
                for j in range(int(60 / tempo * sampleRate)):
                    waves[i[1]][j] = limit(waves[i[1]][j] + wave[j], 1)
            totalprogress += 1
            progress_label.config(text=f"Computed {totalprogress}/{total}.")
            pwindow.update()
    pwindow.destroy()
    window.update()
    keys = sorted(list(waves.keys()))
    for i in range(len(keys)):
        pv.write(waves[keys[i]])
        Thread(target=pv.flush).start()
        if(i < len(keys)-1):
            sleep(60 / tempo * (keys[i+1] - keys[i]))
        else:
            sleep(60 / tempo)

def export_all():
    global sounds, frequencies, pv, tempo, window
    pwindow = tk.Toplevel()
    pwindow.wm_title("Computing sounds...")
    pwindow.minsize(200, 75)
    pwindow.maxsize(200, 75)
    progress_label = tk.Label(pwindow)
    progress_label2 = tk.Label(pwindow)
    progress_label.pack()
    progress_label2.pack()
    progress_label.config(text="Preparing to compute notes...")
    waves = {}
    totalprogress = 0
    total = 0
    for i in sounds.keys():
        total += len(sounds[i][2])
    for sound in sounds.keys():
        name = sound
        notes = sounds[name][2]
        window.update()
        for i in notes:
            if not i[1] in waves.keys():
                waves[i[1]] = compute_sound(name, frequencies[11-i[0]], int(60 / tempo * sampleRate), pwindow, progress_label2)
            else:
                wave1 = compute_sound(name, frequencies[11-i[0]], int(60 / tempo * sampleRate), pwindow, progress_label2)
                for j in range(int(60 / tempo * sampleRate)):
                    waves[i[1]][j] = limit(waves[i[1]][j] + wave1[j], 1)
            totalprogress += 1
            progress_label.config(text=f"Computed {totalprogress}/{total}.")
            pwindow.update()
    pwindow.destroy()
    window.update()
    keys = sorted(list(waves.keys()))
    data = array.array('h')
    for i in range(len(keys)):
        for j in waves[keys[i]]:
            data.append(j)
        if i < len(keys)-1:
            for j in range((keys[i+1] - keys[i] - 1) * sampleRate):
                data.append(0)
    filename = tkinter.filedialog.asksaveasfilename(initialdir = "/",
                                          title = "Export audio",
                                          filetypes = (("WAV audio file",
                                                        "*.wav"),))

    encoder = wave.open(filename, 'wb')
    encoder.setnchannels(1)
    encoder.setsampwidth(4)
    encoder.setframerate(sampleRate/2)
    encoder.writeframes(data)
    encoder.close()

tempo_label = tk.Label(text="Tempo (BPM)")
tempo_button = tk.Button(text="Set", command=set_tempo)
tempo_input = tk.Entry()
tempo_input.insert(10, "60")
button = tk.Button(window, text="New sound", command=new_sound)
progress_label = tk.Label()
play_all_button = tk.Button(window, text="Play all", command=partial(play_all))
export_button = tk.Button(window, text="Export all", command=partial(export_all))
tempo_label.pack()
tempo_input.pack()
tempo_button.pack()
button.pack()
play_all_button.pack()
export_button.pack()
progress_label.pack()
window.mainloop()