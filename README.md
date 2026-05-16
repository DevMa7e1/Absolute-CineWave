# Absolute CineWave
<p style="font-size: 18px">Generate sounds by writing code!</p>

## What is this?
Absolute CineWave is a programmable sound generator. It gives you a simple to use interface for generating sounds by writing Python code. 

Basically, Absolute CineWave handles the boring and tedious parts (sound computation, playing, exporting, juggling between libraries etc.) so that you can focus on actually creating the sound you wanted, while still giving you the freedom to do whatever you want.

# Reference
## 1. Predefined variables
- ### For sound computing:
    | Name | Purpose |
    |---------|-------------|
    |**freq** | the frequency of the note that is being computed (selected from the piano roll)|
    |**time** | the Time object that holds the number of the current PCM frame that is being computed|
    |**frames** | the total number of frames that should be computed|
    |**name** | the name of the sound|
    |**waveL** | the left sound wave as a list of 32 bit signed integers|
    |**waveR** | the right sound wave as a list of 32 bit signed integers|
    |**code** | the source code of the sound (internal, not intended to be used in your sound code) |
    |**progress_window** | the tkinter Toplevel widget that displays the current amount of progress made (internal, not intended to be used in your sound code)|
    |**progress_label** | the tkinter Label widget, child of **progress_window**<br>it shows the current amount of progress made (internal, not intended to be used in your sound code)|
- ### For applying plug-ins to sounds:
    | Name | Purpose |
    |---------|------------|
    |**name** | the name of the sound |
    |**code** | the plugin code (internal, not intended to be used in your plug-in applier code)|
    |**waves** | tuple of the left and right sound waves (kinda internal)|
    |**waveL** | the left sound wave, given as a list of 32 bit signed integers|
    |**waveR** | the right sound wave, given as a list of 32 bit signed integers|
    |**freq** | the frequency of the note (selected from the piano roll)|


## 2. Audio functions:
### sine_wave(frequency: float, time: Time, amplitude: float)
This function computes the sine wave amplitude value at the x coordonate provided by the Time object. <br>Example sound code:

<code>s = sine_wave(freq, time, 0.5)<br>s ->L<br>s ->R</code>

### triangle_wave(frequency: float, time: Time, amplitude: float)
This function computes the triangle wave amplitude value at the x coordonate provided by the Time object. <br>Example sound code:

<code>t = triangle_wave(freq, time, 0.5)<br>s ->L<br>s ->R</code>

### sawtooth_wave(frequency: float, time: Time, amplitude: float)
This function computes the saw-tooth wave amplitude value at the x coordonate provided by the Time object. <br>Example sound code:

<code>s = sine_wave(freq, time, 0.5)<br>s ->L<br>s ->R</code>

### custom(name: str, frequency: float, time: Time, amplitude: float)
This function uses an imported waveform as a waveform. Basically, it squishes or stretches the imported waveform such that it is exactly **1 / freq** seconds long and then "plays" it repeatedly. <br>Example sound code:

<code>w = custom('CustomWaveform.flac', freq, time, 0.5)<br>w ->L<br>w ->R</code>

### play_custom(name: str, time: Time, amplitude: float, speed: float = 1)
This function "plays" an imported waveform at the given playback speed.<br>Example sound code:

<code>w = play_custom('sample.flac', time, 1, 2)<br>w ->L<br>w ->R</code>

### limit(value: int, limit: float)
This function caps a PCM frame's amplitude. If a value goes above the limit or below the opposite of the limit (-limit), the function returns the limit as a PCM frame value. Otherwise, the value just gets returned back with no modification.<br>Example sound code:

<code>s = sine_wave(freq, time, 1)<br>limit(s, 0.5) ->L<br>limit(s, 0.5) ->R</code>

### echo(wave: list, time: Time, difference: Time)
This function returns the value of the PCM frame that was "played" **difference** seconds ago.<br>Example sound code:

<code>s = sine_wave(freq, time, 0.5)<br>echo(waveL, time, Time(0.25)) + s ->L<br> echo(waveR, time, Time(0.35)) + s ->R</code>

## 3. Advanced audio functions: the EQ class
### Initializing a new EQ object: 
**EQ(wave: list)**<br>
Example plug-in applier code:<br>
<code>from advanced_audio_functions import EQ<br>eqL = EQ(waveL)<br>eqR = EQ(waveR)</code>

### Boosting/attenuating a frequency range: 
**.apply_eq(start_frequency: int, end_frequency: int, factor: float)**<br>
Example plug-in applier code:<br>
<code>from advanced_audio_functions import EQ<br>eqL = EQ(waveL)<br>eqR = EQ(waveR)<br>eqL.apply_eq(100, 200, 2)<br>eqR.apply_eq(100, 200, 2)</code>

#### Getting back the wave
**(no arguments)**<br>
Example plug-in applier code:<br>
<code>from advanced_audio_functions import EQ<br>eqL = EQ(waveL)<br>eqR = EQ(waveR)<br>eqL.apply_eq(100, 200, 2)<br>eqR.apply_eq(100, 200, 2)<br>eqL() ->L<br>eqR() ->R</code>
