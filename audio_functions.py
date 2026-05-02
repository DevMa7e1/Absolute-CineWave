from extras import *
import math

waveforms = {}

def sine_wave(freq: float, time: Time, amplitude: float):
    if(amplitude <= 1 and amplitude >= 0):
        return int(round(math.sin(time.seconds() * freq * 2 * math.pi), 8) * (frameMax * amplitude))

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
    progress = (time() / (1/freq)) % 1
    waveform = waveforms[name][1]
    progress_frame = math.floor(progress * len(waveform))
    print(progress_frame, waveform[progress_frame])
    return int(waveform[progress_frame] * amplitude)