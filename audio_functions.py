from extras import *
import math

def sine_wave(freq: float, time: Time, amplitude: float):
    if(amplitude <= 1 and amplitude >= 0):
        return int(round(math.sin(time.seconds() * freq * 2 * math.pi), 8) * (sampleMax * amplitude))

def triangle_wave(freq: float, time: Time, amplitude: float):
    if(amplitude <= 1 and amplitude >= 0):
        complete_wave_time = (1/freq)
        full_wave_time = (complete_wave_time/2)
        wave_time = time() % complete_wave_time

        if wave_time < complete_wave_time/2:
            if wave_time < full_wave_time/2:
                progress = safe_division(wave_time, full_wave_time/2)
                return int((-progress) * sampleMax * amplitude)
            else:
                progress = safe_division(wave_time - full_wave_time/2, full_wave_time/2)
                return int((-1+progress) * sampleMax * amplitude)
        else:
            wave_time -= full_wave_time
            if wave_time < full_wave_time/2:
                progress = safe_division(wave_time, full_wave_time/2)
                return int(progress * sampleMax * amplitude)
            else:
                progress = safe_division(wave_time - full_wave_time/2, full_wave_time/2)
                return int((1 - progress) * sampleMax * amplitude)
            

def sawtooth_wave(freq: float, time: Time, amplitude: float):
    complete_wave_time = 1/freq
    wave_time = time() % complete_wave_time
    relative_wave_time = wave_time / complete_wave_time
    return int((relative_wave_time - 0.5) * sampleMax * 2 * amplitude)
                
def limit(value: int, limit: float):
    if value > limit * sampleMax:
        return int(limit * sampleMax)
    if value < -limit * sampleMax:
        return int(-limit * sampleMax)
    return value

def amplify(value: int, factor: float):
    return limit(int(value * factor), 1)

def echo(wave: list, time: Time, difference: Time):
    if(time.pcm_frames() >= difference.pcm_frames()):
        return wave[time.pcm_frames()-difference.pcm_frames()]
    else:
        return 0