from extras import *
import math

waveforms = {}
frequencies = [261.63, 277.18, 293.66, 311.13, 329.63, 349.23, 369.99, 392, 415.30, 440, 466.16, 493.88]

def sine_wave(freq: float, time: Time, amplitude: float):
    if(amplitude <= 1 and amplitude >= 0):
        return int(round(math.sin(time.seconds() * freq * 2 * math.pi), 8) * (frameMax * amplitude))
    return 0

def triangle_wave(freq: float, time: Time, amplitude: float):
    if(amplitude <= 1 and amplitude >= 0):
        complete_wave_time = (1/freq)
        full_wave_time = (complete_wave_time/2)
        wave_time = time() % complete_wave_time

        if wave_time < complete_wave_time/2:
            if wave_time < full_wave_time/2:
                progress = safe_division(wave_time, full_wave_time/2)
                return int((-progress) * frameMax * amplitude)
            else:
                progress = safe_division(wave_time - full_wave_time/2, full_wave_time/2)
                return int((-1+progress) * frameMax * amplitude)
        else:
            wave_time -= full_wave_time
            if wave_time < full_wave_time/2:
                progress = safe_division(wave_time, full_wave_time/2)
                return int(progress * frameMax * amplitude)
            else:
                progress = safe_division(wave_time - full_wave_time/2, full_wave_time/2)
                return int((1 - progress) * frameMax * amplitude)
            

def sawtooth_wave(freq: float, time: Time, amplitude: float):
    complete_wave_time = 1/freq
    wave_time = time() % complete_wave_time
    relative_wave_time = wave_time / complete_wave_time
    return int((relative_wave_time - 0.5) * frameMax * 2 * amplitude)
                
def limit(value: int, limit: float):
    if value > limit * frameMax:
        return int(limit * frameMax)
    if value < -limit * frameMax:
        return int(-limit * frameMax)
    return value

def amplify(value: int, factor: float):
    return limit(int(value * factor), 1)

def echo(wave: list, time: Time, difference: Time):
    if(time.pcm_frames() >= difference.pcm_frames()):
        return wave[time.pcm_frames()-difference.pcm_frames()]
    else:
        return 0

def custom(name: str, freq: float, time: Time, amplitude: float):
    waveform = waveforms[name]
    if not f'cobj{freq}' in waveform[1]:
        audioi = AudioInterpolator(waveform[0], frameRate)
        audioi.stretch_or_squish_to_length(1/freq)
        waveform[1][f'cobj{freq}'] = audioi.get()
    frame = time.pcm_frames() % len(waveform[1][f'cobj{freq}'])
    return int(waveform[1][f'cobj{freq}'][frame] * amplitude)

def play_custom(name: str, time: Time, amplitude: float, raise_by: int = 0):
    waveform = waveforms[name]
    if not f'pcobj{raise_by}' in waveform[1]:
        audioi = AudioInterpolator(waveform[0], frameRate)
        audioi.stretch_or_squish(1/raise_by)
        waveform[1][f'pcobj{raise_by}'] = audioi.get()
    frame = time.pcm_frames() % len(waveform[1][f'pcobj{raise_by}'])
    return int(waveform[1][f'pcobj{raise_by}'][frame] * amplitude)