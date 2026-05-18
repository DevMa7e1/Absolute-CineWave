import tkinter as tk
from tkinter import messagebox
from extras import *
from audio_functions import *

def compute_sound(name: str, freq: int, frames: int, code, progress_window: tk.Toplevel, progress_label: tk.Label):
    global sounds
    waveR = []
    waveL = []
    time = Time()
    for i in range(frames):
        if i % 1000 == 0:
            progress = i / (frames)
            progress_label.config(text=f"Computing\n[{'='*(int(progress*20)-1)}>{' '*(20-int(progress*20))}]")
            progress_window.update()
        try:
            exec(code)
        except Exception as e:
            messagebox.showerror("Code execution error", str(e))
            raise Exception(f"Execution error: {str(e)}")
        time.increment()
    if len(waveL) > 0:
        if type(waveL[-1]) != int:
            messagebox.showerror('Computation error', f'The code for {name} didn\'t output PCM frames of type int.')
    if len(waveL) != len(waveR):
        messagebox.showerror("Computation error", f"The length of sound in the left channel does not match the\
 one in the right channel! (L: {len(waveL)} vs R: {len(waveR)})")
        raise Exception("L and R channels don't match in length.")
    if len(waveL) != frames:
        messagebox.showerror('Computation error', f'The code for {name} produced too little or too many \
PCM frames ({len(waveL)}/{frames}).')
        raise Exception('To many or too little PCM frames generated.')
    return waveL, waveR
def apply_plugins(name: str, code: str, waves: tuple, freq: float):
    waveL = waves[0]
    waveR = waves[1]
    try:
        exec(compile(code, f'{name} plugin code', 'exec'))
        return waveL, waveR
    except Exception as e:
        messagebox.showerror('Plugin computation error', str(e))
        raise Exception(f"Plugin computation error: {e}")