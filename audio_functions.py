from extras import *
import math

try:
    waveforms.keys() #type: ignore
except:
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
    waveformL = waveform[0][0]
    waveformR = waveform[0][1]
    if not f'cobjL{freq}' in waveform[1]:
        audioi = AudioInterpolator(waveformL, frameRate)
        audioi.stretch_or_squish_to_length(1/freq)
        waveform[1][f'cobjL{freq}'] = audioi.get()
    if not f'cobjR{freq}' in waveform[1]:
        audioi = AudioInterpolator(waveformR, frameRate)
        audioi.stretch_or_squish_to_length(1/freq)
        waveform[1][f'cobjR{freq}'] = audioi.get()
    frame = time.pcm_frames() % len(waveform[1][f'cobjL{freq}'])
    return int(waveform[1][f'cobjL{freq}'][frame] * amplitude), int(waveform[1][f'cobjR{freq}'][frame] * amplitude)

def play_custom(name: str, time: Time, amplitude: float, speed: int = 1):
    waveform = waveforms[name]
    waveformL = waveform[0][0]
    waveformR = waveform[0][1]
    if not f'pcobjL{speed}' in waveform[1].keys():
        audioi = AudioInterpolator(waveformL, frameRate)
        audioi.stretch_or_squish(1/speed)
        waveform[1][f'pcobjL{speed}'] = audioi.get()
    if not f'pcobjR{speed}' in waveform[1].keys():
        audioi = AudioInterpolator(waveformR, frameRate)
        audioi.stretch_or_squish(1/speed)
        waveform[1][f'pcobjR{speed}'] = audioi.get()
    frame = time.pcm_frames() % len(waveform[1][f'pcobjL{speed}'])
    return int(waveform[1][f'pcobjL{speed}'][frame] * amplitude), int(waveform[1][f'pcobjR{speed}'][frame] * amplitude)