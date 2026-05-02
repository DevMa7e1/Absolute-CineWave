import tkinter as tk
import tkinter.filedialog
import tkinter.messagebox
import pyaudio
import re
from audio_functions import *
from extras import *
from functools import partial
from pathlib import Path
from time import sleep
import wave
import array
import dill
#For debugging purposes
#import matplotlib.pyplot as plt

window = tk.Tk()
window.wm_title("Absolute CineWave")

p = pyaudio.PyAudio()
out = p.open(format=pyaudio.paInt32,
                channels=1,
                rate=frameRate*2,
                output=True,
                frames_per_buffer=bufferSize)

time = Time()

saved = True

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

def interpolate_between_notes(frames: int, waves: dict):
    keys = sorted(list(waves.keys()))
    for i in range(len(keys)-1):
        wave1 = waves[keys[i]]
        wave2 = waves[keys[i+1]]
        linear = LinearInterpolator(wave1[len(wave1)-frames], wave2[0], frames)
        for j in range(frames, 0, -1):
            wave1[len(wave1)-j] = int(linear(frames-j))
    return waves

def remove_frames_until_perfect_transition(frames: int, waves: dict):
    keys = sorted(list(waves.keys()))
    for i in range(len(keys)-1):
        wave1: list = waves[keys[i]]
        wave2: list = waves[keys[i+1]]
        wave1sect = sorted(wave1[len(wave1)-frames//2-1:])
        wave2sect = sorted(wave2[:frames//2])
        it1, it2 = 0, 0
        val1, val2 = 0, 0
        closest = 1000000
        while(it1 < len(wave1sect) and it2 < len(wave2sect)):
            if(wave1sect[it1] > wave2sect[it2]):
                it2 += 1
                if not (it1 < len(wave1sect) and it2 < len(wave2sect)):
                    break
            if(wave1sect[it1] < wave2sect[it2]):
                it1 += 1
                if not (it1 < len(wave1sect) and it2 < len(wave2sect)):
                    break
            if(wave1sect[it1] == wave2sect[it2]):
                closest = 0
                val1, val2 = wave1sect[it1], wave2sect[it2]
                break
            if(abs(wave1sect[it1] - wave2sect[it2]) < closest):
                val1, val2 = wave1sect[it1], wave2sect[it2]
                closest = abs(wave1sect[it1] - wave2sect[it2])
        index, index2 = len(wave1) - wave1[::-1].index(val1, 0, frames//2), wave2.index(val2, 0, frames//2)
        waves[keys[i]] = waves[keys[i]][:index]
        waves[keys[i+1]] = waves[keys[i+1]][index2:]
    return waves

playing = True
stopped = False

def play_pause():
    global playing
    playing = not playing
def stop():
    global stopped
    stopped = True

def play_waves_with_big_buffer(waves: dict):
    global frameRate, playing, stopped
    buffer = []
    keys = sorted(list(waves.keys()))
    for i in range(len(keys)):
        buffer += waves[keys[i]]
        if i < len(keys)-1:
            buffer += [buffer[-1]] * int(60 / tempo * (keys[i+1] - keys[i] - 1) * frameRate)
    chunk = 0
    chunks = []
    while chunk * 20 * frameRate < len(buffer):
        pvchunk = buffer[chunk * 20 * frameRate:chunk * 20 * frameRate + min(len(buffer)-chunk * 20 * frameRate, 20 * frameRate)]
        chunks.append(pvchunk)
        chunk += 1
    controls_window = tk.Toplevel()
    time_label = tk.Label(controls_window, text="Played 0s / 0s")
    pause_play_button = tk.Button(controls_window, text="Pause/Play", command=play_pause)
    stop_button = tk.Button(controls_window, text="Stop", command=stop)
    time_label.grid(column=0, row=0)
    pause_play_button.grid(column=0, row=1)
    stop_button.grid(column=1, row=1)
    window.update()
    abI = 0
    audio_buffer = []
    chunks = []
    total_len = len(buffer)
    while len(buffer) > 0:
        if len(buffer) > bufferSize:
            chunks.append(bytes(array.array('l', buffer[:bufferSize])))
            buffer = buffer[bufferSize:]
        else:
            chunks.append(bytes(array.array('l', buffer + [0] * (bufferSize-len(buffer)))))
            buffer.clear()
    buffer2 = []
    for chunk in chunks:
        chunk_a = array.array('l', chunk)
        for i in chunk_a:
            buffer2.append(i)
    for i in chunks:
        audio_buffer.append(i)
    abL = len(chunks)
    while abL > abI:
        controls_window.update()
        if playing:
            out.write(audio_buffer[abI])
        else:
            while not playing:
                controls_window.update()
                sleep(0.1)
        if stopped:
            stopped = False
            break
        time_label.config(text=f"Played {round(abI*bufferSize/frameRate, 2)}s / {round(total_len/frameRate, 2)}s")
        abI += 1
    controls_window.destroy()

def process_config(text: str):
    config = {}
    for i in text.split('\n'):
        if i.count(':') == 1:
            i = i.replace(' ', '')
            config[i.split(':')[0]] = i.split(':')[1]
    return config

def standard_sound_processing(name: str, progress_label2: tk.Label, pwindow: tk.Toplevel, waves: dict = {}, progress_label = None):
    global sounds, frequencies, tempo
    notes = sounds[name][2]
    config = process_config(sounds[name][3])
    adjusted_tempo = False
    new_tempo = tempo
    tempos = {}
    if 'tempo' in config.keys():
        config["tempo"] = config["tempo"].split(",")
        adjusted_tempo = True
        for i in config['tempo']:
            if(len(i.split('>')) == 2):
                where = int(i.split('>')[0])
                what = int(i.split('>')[1])
                tempos[where] = what

    totalprogress = 0
    for i in notes:

        if adjusted_tempo:
            for where in sorted(tempos.keys()):
                if where > i[1]:
                    break
                else:
                    new_tempo = tempos[where]
                    
        if not i[1] in waves.keys():
            waves[i[1]] = compute_sound(name, frequencies[11-i[0]], int(60 / new_tempo * frameRate), pwindow, progress_label2)
        else:
            wave = compute_sound(name, frequencies[11-i[0]], int(60 / new_tempo * frameRate), pwindow, progress_label2)
            for j in range(int(60 / tempo * frameRate)):
                waves[i[1]][j] = limit(waves[i[1]][j] + wave[j], 1)
        totalprogress += 1
        
        if progress_label:
            progress_label.config(text=f"Computed {totalprogress}/{len(notes)}.")
    if 'transition_seconds' in config.keys():
        frames = int(float(config['transition_seconds'])*frameRate)
    else:
        frames = frameRate//100
    if 'transition' in config.keys() and config['transition'] == 'interpolate':
        waves = interpolate_between_notes(frames, waves)
    elif 'transition' in config.keys() and config['transition'] == 'remove':
        waves = remove_frames_until_perfect_transition(frames, waves)
    elif 'transition' in config.keys() and config['transition'] == 'none':
        pass
    else:
        waves = remove_frames_until_perfect_transition(frames, waves)
    return waves

def play_sound(name: str):
    global sounds, frequencies, pv, tempo
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
    waves = {}
    waves = standard_sound_processing(name, progress_label2, pwindow, {}, progress_label)
    pwindow.destroy()
    play_waves_with_big_buffer(waves)

sounds = {}
tempo = 60

def save_code(code_input: tk.Text, name: str, close_window: bool = False, sound_window: tk.Toplevel = None): # type: ignore
    global sounds, saved
    saved = False
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
        sounds[name][0] = code2 
        sounds[name][1] = compiled
        if close_window:
            sound_window.destroy()
        else:
            sound_window.destroy()
            play_window(name)
    except Exception as e:
        tkinter.messagebox.showerror("Syntax error", str(e))

def save_config(config_input: tk.Text, name: str):
    global sounds, saved
    saved = False
    config = config_input.get("1.0", "end-1c")
    sounds[name][3] = config

def open_sound(name: str, destroy_pwindow: bool = False, pwindow: tk.Toplevel = None): # type: ignore
    sound_window = tk.Toplevel()
    sound_window.wm_title(f"{name}: Absolute CineWave")
    code_input = tk.Text(sound_window)
    code_input.insert(tk.END, sounds[name][0])

    sound_window.protocol("WM_DELETE_WINDOW", partial(save_code, code_input, name, True, sound_window))

    play_button = tk.Button(sound_window, text="Open Piano Roll", command=partial(save_code, code_input, name, sound_window=sound_window)) # type: ignore
    code_input.pack()
    play_button.pack()

    if destroy_pwindow:
        pwindow.destroy()

def create_sound(name: str):
    global sounds, current_column, current_row, saved
    saved = False
    current_column += 1
    if(current_column >= 3):
        current_column = 0
        current_row += 1
    sounds[name] = ["", None, [], '']
    new_button = tk.Button(window, text=name, command=partial(open_sound, name)) # type: ignore
    new_button.grid(column=current_column, row=current_row)

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
cog = tk.PhotoImage(file=Path(__file__).parent.absolute().joinpath('cog.png'))

def select_note(x: int, y: int, name: str, button: tk.Button):
    global blue, gray, sounds, saved
    saved = False
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
                buttons.append(new_button)
            else:
                new_button = tk.Button(pwindow, image=gray, padx=4, pady=4)
                buttons.append(new_button)
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
                    buttons.append(new_button)
                else:
                    new_button = tk.Button(pwindow, image=gray, padx=4, pady=4)
                    buttons.append(new_button)
                new_button.config(command=partial(select_note, x, y+position, name, new_button))
                new_button.grid(row=x, column=y+1)
    buttonself.config(command=partial(backwards, buttonself, buttons, pwindow, poslabel, name))

def sound_config(name: str):
    global sounds
    cwindow = tk.Toplevel()
    config_input = tk.Text(cwindow, height=6, width=25)
    config_input.pack()
    config_input.insert(tk.END, sounds[name][3])
    save_button = tk.Button(cwindow, text="Save", command=partial(save_config, config_input, name))
    save_button.pack()

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
                buttons.append(new_button)
            else:
                new_button = tk.Button(pwindow, image=gray, padx=4, pady=4)
                buttons.append(new_button)
            new_button.config(command=partial(select_note, x+position, y, name, new_button))
            new_button.grid(row=x, column=y+1)
    play_button = tk.Button(pwindow, text="Play", command=partial(play_sound, name))
    position_label = tk.Label(pwindow, text="0")
    
    forwards_button = tk.Button(pwindow, text=">")
    forwards_button.config(command=partial(forwards, forwards_button, buttons, pwindow, position_label, name))
    
    backwards_button = tk.Button(pwindow, text="<")
    backwards_button.config(command=partial(backwards, backwards_button, buttons, pwindow, position_label, name))
    
    config_button = tk.Button(pwindow, image=cog, command=partial(sound_config, name))
    
    play_button.grid(row=12, column=0)
    forwards_button.grid(row=12, column=2)
    backwards_button.grid(row=12, column=1)
    config_button.grid(row=12, column=3)
    position_label.grid(row=12, column=17)

    pwindow.protocol("WM_DELETE_WINDOW", partial(open_sound, name, True, pwindow))

def set_tempo():
    global tempo_input, tempo, saved
    saved = False
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
    for name in sounds.keys():
        waves = standard_sound_processing(name, progress_label2, pwindow, waves)
        totalprogress += 1
        progress_label.config(text=f"Computed {totalprogress}/{total}.")
        pwindow.update()
    pwindow.destroy()
    window.update()
    play_waves_with_big_buffer(waves)

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
    for name in sounds.keys():
        window.update()
        waves = standard_sound_processing(name, progress_label2, pwindow, waves)
        totalprogress += 1
        progress_label.config(text=f"Computed {totalprogress}/{total}.")
        pwindow.update()
    pwindow.destroy()
    window.update()
    keys = sorted(list(waves.keys()))
    data = array.array('l')
    for i in range(len(keys)):
        for j in waves[keys[i]]:
            data.append(j)
        if i < len(keys)-1:
            for j in range((keys[i+1] - keys[i] - 1) * frameRate):
                data.append(0)
    filename = tkinter.filedialog.asksaveasfilename(initialdir = "/",
                                          title = "Export audio",
                                          filetypes = (("WAV audio file",
                                                        "*.wav"),))
    if type(filename) != tuple and filename != '':
        encoder = wave.open(filename, 'wb')
        encoder.setnchannels(1)
        encoder.setsampwidth(4)
        encoder.setframerate(frameRate/2)
        encoder.writeframes(data)
        encoder.close()

def convert_to_type_code(size: int) -> str:
    match size:
        case 8:
            return 'b'
        case 16:
            return 'h'
        case 32:
            return 'l'
        case 64:
            return 'q'
    return 'l'

def import_waveform():
    filename = tkinter.filedialog.askopenfilename(initialdir = "/",
                                              title = "Import a custom waveform",
                                              filetypes = (("WAV file",
                                                            "*.wav"),))
    if type(filename) != tuple and filename != '':
        decoder = wave.open(filename, 'rb')
        wfrate = decoder.getframerate()
        wfwidth = decoder.getsampwidth() * 8
        wfdata = decoder.readframes(decoder.getnframes())
        if wfwidth == frameBits:
            native_wfdata = array.array(convert_to_type_code(frameBits), wfdata)
            waveforms[Path(filename).name] = [wfrate, native_wfdata]
        else:
            tkinter.messagebox.showerror('Import error', f'The WAV file you selected has a sample width that differes from the one currently selected \
for this project ({frameBits}). Please convert your file to a {frameBits} bit WAV file using audio software then try again.')

def save_project():
    global sounds, tempo, saved
    filename = tkinter.filedialog.asksaveasfilename(initialdir = "/",
                                          title = "Save your project",
                                          filetypes = (("Absolute CineWave project",
                                                        "*.acwproj"),))
    if type(filename) != tuple and filename != '':
        file = open(filename, 'wb')
        dill.dump((sounds, tempo), file)
        file.close()
        saved = True
    else:
        saved = False

def load_project():
    global sounds, tempo, current_column, current_row, tempo_input, saved
    if not saved:
        answer = tkinter.messagebox.askyesnocancel("Before you load another project...", "Do you want to save your current project?")
        if answer:
            save_project()
        if answer == False:
            saved = True
    if saved:
        filename = tkinter.filedialog.askopenfilename(initialdir = "/",
                                              title = "Load a project",
                                              filetypes = (("Absolute CineWave project",
                                                            "*.acwproj"),))
        if type(filename) != tuple and filename != '':
            file = open(filename, 'rb')
            sounds, tempo = dill.load(file)
            file.close()
            for i in sounds.keys():
                current_column += 1
                if(current_column >= 3):
                    current_column = 0
                    current_row += 1
                new_button = tk.Button(window, text=i, command=partial(open_sound, i)) # type: ignore
                new_button.grid(column=current_column, row=current_row)
            tempo_input.delete(0, tk.END)
            tempo_input.insert(10, str(tempo))

def check_if_saved_then_close():
    global saved, window
    if not saved:
        answer = tkinter.messagebox.askyesnocancel("Before you go...", "Do you want to save your project?")
        if answer:
            save_project()
        if answer == False:
            window.destroy()
    else:
        window.destroy()

window.protocol("WM_DELETE_WINDOW", check_if_saved_then_close)

current_row = 4
current_column = -1

tempo_label = tk.Label(text="Tempo (BPM)")
tempo_button = tk.Button(text="Set", command=set_tempo)
tempo_input = tk.Entry(width=5)
tempo_input.insert(10, "60")

new_sound_button = tk.Button(window, text="New sound", command=new_sound)
progress_label = tk.Label()
play_all_button = tk.Button(window, text="Play all", command=partial(play_all))
export_button = tk.Button(window, text="Export all", command=partial(export_all))

save_project_button = tk.Button(text="Save project", command=save_project)
load_project_button = tk.Button(text="Load project", command=load_project)

custom_ = tk.Button(window, command=import_waveform, text="Add waveform")

spacer = tk.Label(text=" ")

tempo_label.grid(column=0, row=0)
tempo_input.grid(column=1, row=0)
tempo_button.grid(column=2, row=0)

new_sound_button.grid(column=0, row=1)
play_all_button.grid(column=1, row=1)
export_button.grid(column=2, row=1)

save_project_button.grid(column=0, row=2)
load_project_button.grid(column=2, row=2)

custom_.grid(row=2, column=1)

spacer.grid(row=3, column=0)
window.mainloop()