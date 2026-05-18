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
### Note
I don't recommend using the advanced audio functions equalizer implementation because I still don't fully understand how the EQ is supposed to work and it does not seem to produce the expected results. This is present here only for experimental purposes.
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

## Extras
### the Time class
- #### Initialization
    You can initialize a Time object without any arguments, but if you wanna give it a value, you can use the arguments **start_seconds** (will automatically convert to PCM frame count) or **start_pcm_frames**.

    **Time(start_seconds: float = 0, start_pcm_frames: int = 0)** (both arguments are optional)
- #### Calling
    When a Time object is called, it returns the number of seconds stored inside it. It takes no arguments and returns a float.

    <code>t = Time(1)<br>t() #returns 1</code>
    #### or
    <code>t = Time(start_pcm_frames=48000)<br>t() #also returns 1, if frameRate is set to 48000</code>
- #### pcm_frames()
    This function returns the PCM frame count stored inside of the Time object

    <code>t = Time(1)<br>t.pcm_frames() #returns 48000 if frameRate is set to 48000</code>
- #### increment(step: int = 1)
    This function adds the value of **step** to the PCM frame count stored inside itself. By default it adds 1, thus incrementing the value by 1.

### the BasicInterpolator class (internal)
- #### Initialization
    **BasicInterpolator(start_value: int, end_value: int, frames: int)**

    To initialize a BasicInterpolator object, you need to pass a start and end PCM frame value, and the number of frames that you want the interpolator to generate between the values.
- #### Calling
    To call the BasicInterpolator object, you need to pass an argument representing the x coordonate of the frame you want the interpolator to return. The range of coordonates is 0 (the start value) - **frames** (the end value).

    **(x: int)**
    
    Example code:<br>
    <code>bi = BasicInterpolator(waveL[0], waveL[99], 100)<br>for i in range(0, 100):<br>&ensp;waveL[i] = bi(i)</code>
### the AudioInterpolator class
- #### Note
    Theoretically, this class is primarily internal, but you could find it useful when making plug-in applier code.
- #### Initialization
    **AudioInterpolator(data: list, input_framerate: int = frameRate)**

    The AudioInterpolator object, when used in plug-in applier code, should only really be initialized with only the **data** argument set.
- #### stretch_or_squish
    **stretch_or_squish(factor: float)**

    This function multiplies the length of the sound by the **factor** value. Basically, it stretches the audio (when **factor** > 1) or squishes it (when **factor** < 1). In other words, it speeds up or slows down the audio data given. 
    
    Keep in mind that **factor** here is inverse to how you'd usually think about it. Passing a **factor** of 2 makes the audio length be 2 times bigger, but it's speed 0.5 (1/**factor**) times bigger. Subsequently, passing a **factor** of 0.5 makes the length 0.5 times bigger, but increases the speed by 2 times.

    The audio function **play_custom()** passes the inverse of the given **speed** argument (1/**speed**) to the AudioInterpolator.
- #### stretch_or_squish_to_length
    **stretch_or_squish_to_length(seconds_length: float)**
    
    This function makes the length of the audio data be exactly **seconds_length** seconds. This either makes the audio be exactly the same, slower, or quicker.
- #### get()
    This function returns the processed audio data.
- #### clear()
    This function clears the processed audio data stored inisde of the AudioInterpolator module. This function is useful if you already ran **get()** but want to do another **stretch_or_squish()** on the data inside of the object. Running **get()**, then **stretch_or_squish()**, and then **get()** again without running **clear()** gives you exactly the same result as the first **get()** even though you've ran **stretch_or_squish()**.
### the AudioData class (internal)
- #### Initialization
    **AudioData(data: bytes, frame_width: int, multiply_by: int = 1)**
    
    This initializes a new AudioData object which can be used to read PCM audio data from raw bytes. This class is used internally when importing custom waveforms because the libraries used like to return the values as a bytes/memoryview object that is hard to convert directly to a native Python class.
- #### read()
    **read()** takes no arguments and it returns the processed audio data as a list.
### safe_division() (internal)
**safe_division(a: float, b: float)**

This function divides a by b. If b is 0, it returns 0 to avoid a division by zero exeption.

### map() (internal)
**map(x: int, in_min: int, in_max: int, out_min: int, out_max: int)**

This function maps a value **x** to the range **out_min** - **out_max**. It is used internally for generating the sound visualizer images. It could be useful when writing sound code, though.

## Isolated internals
- ### Warning
    **These are all internal functions. They really are NOT meant to be used in sound or plug-in applier code.**
### compute_sound()
**compute_sound(name: str, frequency: int, frames: int, code, progress_window: tkinter.Toplevel, progress_label: tkinter.Label)**

This is the function that takes in code and spits out the waveforms for the left and right channel.
### apply_plugins()
**apply_plugins(name: str, code: str, waves: tuple, frequency: float)**

This function takes in the left and right waveforms, the plug-in applier code and spits out the modified left and right waveforms.