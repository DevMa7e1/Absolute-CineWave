# Absolute CineWave
<img width="400" alt="image" src="https://github.com/user-attachments/assets/63f80551-f4f7-4103-a859-d74513e54b1d" />
<p style="font-size: 18px">Generate sounds by writing code!</p>

## What is this?
Absolute CineWave is a programmable sound generator. It gives you a simple to use interface for generating sounds by writing Python code. 

Basically, Absolute CineWave handles the boring and tedious parts (sound computation, playing, exporting, juggling between libraries etc.) so that you can focus on actually creating the sound you wanted, while still giving you the freedom to do whatever you want.

## Why did I make this?
Absolute CineWave started out as a random thought. I had recently learned that you can directly manipulate PCM frames using Python and I was wondering if I could make some sort of application which you can use to create sounds by writing code.
## Builds' download links
### Windows 10 & 11 (64-bit)
[Download the ZIP here](https://github.com/DevMa7e1/Absolute-CineWave/releases/download/v1.0.0/Absolute-CineWave_Windows_x86-64.zip)
### Linux (64-bit)
[Download the ZIP here](https://github.com/DevMa7e1/Absolute-CineWave/releases/download/v1.0.0/Absolute-CineWave_Linux_x86-64.zip)
### MacOS
* #### Intel based devices (x86_64)
    [Download the zipped app here](https://github.com/DevMa7e1/Absolute-CineWave/releases/download/v1.0.0/Absolute-CineWave_MacOS_x86-64.zip)
* #### newer, ARM based devices (arm64)
    [Download zipped app here](https://github.com/DevMa7e1/Absolute-CineWave/releases/download/v1.0.0/Absolute-CineWave_MacOS_arm64.zip)
## How do you run the binaries?
### Linux
After unzipping, you can run the ELF binary through the terminal or by just double-clicking it.
### Windows
After unzipping the archive which contains the Windows build, you're going to have to right click and open the executable file's properties. In the properties window, click on the checkmark next to Unblock and hit Ok. Now, you can run the software by just double-clicking the exe.
### MacOS
After unzipping the app file, you can run the software by right clicking on the app file and selecting Open. A pop up will appear on which you're going to have to click on Open. Afterwards, you should be able to open the app file by just double-clicking on it.

## How do you use this? - Tutorial
To get an idea of how to use this software, you can make a simple "Hello, world!" project.
Here are the steps:
1. Open Absolute CineWave
2. Click on the New Sound button
3. In the window that just popped up, give the sound a name (or don't) and click on Create
4. Press the button that has just appeared in the main window

    You should now be looking at the coding interface. Here, you write code and it gets turned into a sound. For a simple test, you can use the following example code:
    
    <code>s = sine_wave(freq, time, 0.5)
    s ->L
    s ->R</code>
    
    This example should produce a sine wave when played.<br>
    Explanation:<br>
    * `s = sine_wave(freq, time, 0.5)` -> sets the variable s to the amplitude of the sine wave with the given frequency at the given time
    * `s ->L` -> Add the value to the left channel
    * `s ->R` -> Add the value to the right channel
    
    Tip: Absolute CineWave runs the sound code 48000 times per one second of audio. That is because you have to compute each and every PCM frame, and there are 48000 of them in a second of audio (by default).
5. Click on Open Piano Roll
6. Click on some of the gray tiles
7. Press play and hear your creation!

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

<code>s = sine_wave(freq, time, 0.5)
s ->L
s ->R</code>

### triangle_wave(frequency: float, time: Time, amplitude: float)
This function computes the triangle wave amplitude value at the x coordonate provided by the Time object. <br>Example sound code:

<code>t = triangle_wave(freq, time, 0.5)
s ->L
s ->R</code>

### sawtooth_wave(frequency: float, time: Time, amplitude: float)
This function computes the saw-tooth wave amplitude value at the x coordonate provided by the Time object. <br>Example sound code:

<code>s = sine_wave(freq, time, 0.5)
s ->L
s ->R</code>

### custom(name: str, frequency: float, time: Time, amplitude: float)
This function uses an imported waveform as a waveform. Basically, it squishes or stretches the imported waveform such that it is exactly **1 / freq** seconds long and then "plays" it repeatedly. <br>Example sound code:

<code>w = custom('CustomWaveform.flac', freq, time, 0.5)
w ->L
w ->R</code>

### play_custom(name: str, time: Time, amplitude: float, speed: float = 1)
This function "plays" an imported waveform at the given playback speed.<br>Example sound code:

<code>w = play_custom('sample.flac', time, 1, 2)
w ->L
w ->R</code>

### limit(value: int, limit: float)
This function caps a PCM frame's amplitude. If a value goes above the limit or below the opposite of the limit (-limit), the function returns the limit as a PCM frame value. Otherwise, the value just gets returned back with no modification.<br>Example sound code:

<code>s = sine_wave(freq, time, 1)
limit(s, 0.5) ->L
limit(s, 0.5) ->R</code>

### echo(wave: list, time: Time, difference: Time)
This function returns the value of the PCM frame that was "played" **difference** seconds ago.<br>Example sound code:

<code>s = sine_wave(freq, time, 0.5)
echo(waveL, time, Time(0.25)) + s ->L
echo(waveR, time, Time(0.35)) + s ->R</code>

## 3. Advanced audio functions: the EQ class
### Note
I don't recommend using the advanced audio functions equalizer implementation because I still don't fully understand how the EQ is supposed to work and it does not seem to produce the expected results. This is present here only for experimental purposes.
### Initializing a new EQ object: 
**EQ(wave: list)**<br>
Example plug-in applier code:<br>
<code>from advanced_audio_functions import EQ
eqL = EQ(waveL)
eqR = EQ(waveR)</code>

### Boosting/attenuating a frequency range: 
**.apply_eq(start_frequency: int, end_frequency: int, factor: float)**<br>
Example plug-in applier code:<br>
<code>from advanced_audio_functions import EQ
eqL = EQ(waveL)
eqR = EQ(waveR)
eqL.apply_eq(100, 200, 2)
eqR.apply_eq(100, 200, 2)</code>

#### Getting back the wave
**(no arguments)**<br>
Example plug-in applier code:<br>
<code>from advanced_audio_functions import EQ
eqL = EQ(waveL)
eqR = EQ(waveR)
eqL.apply_eq(100, 200, 2)
eqR.apply_eq(100, 200, 2)
eqL() ->L
eqR() ->R</code>

## Extras
### the Time class
- #### Initialization
    You can initialize a Time object without any arguments, but if you wanna give it a value, you can use the arguments **start_seconds** (will automatically convert to PCM frame count) or **start_pcm_frames**.

    **Time(start_seconds: float = 0, start_pcm_frames: int = 0)** (both arguments are optional)
- #### Calling
    When a Time object is called, it returns the number of seconds stored inside it. It takes no arguments and returns a float.

    <code>t = Time(1)
    t() #returns 1</code>
    #### or
    <code>t = Time(start_pcm_frames=48000)
    t() #also returns 1, if frameRate is set to 48000</code>
- #### pcm_frames
    This function returns the PCM frame count stored inside of the Time object

    <code>t = Time(1)
    t.pcm_frames() #returns 48000 if frameRate is set to 48000</code>
- #### increment
    **increment(step: int = 1)**

    This function adds the value of **step** to the PCM frame count stored inside itself. By default it adds 1, thus incrementing the value by 1.

### the BasicInterpolator class (internal)
- #### Initialization
    **BasicInterpolator(start_value: int, end_value: int, frames: int)**

    To initialize a BasicInterpolator object, you need to pass a start and end PCM frame value, and the number of frames that you want the interpolator to generate between the values.
- #### Calling
    To call the BasicInterpolator object, you need to pass an argument representing the x coordonate of the frame you want the interpolator to return. The range of coordonates is 0 (the start value) - **frames** (the end value).

    **(x: int)**
    
    Example code:<br>
    <code>bi = BasicInterpolator(waveL[0], waveL[99], 100)
    for i in range(0, 100):
    &ensp;waveL[i] = bi(i)</code>
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
- #### get
    This function returns the processed audio data.
- #### clear
    This function clears the processed audio data stored inisde of the AudioInterpolator module. This function is useful if you already ran **get()** but want to do another **stretch_or_squish()** on the data inside of the object. Running **get()**, then **stretch_or_squish()**, and then **get()** again without running **clear()** gives you exactly the same result as the first **get()** even though you've ran **stretch_or_squish()**.
### the AudioData class (internal)
- #### Initialization
    **AudioData(data: bytes, frame_width: int, multiply_by: int = 1)**
    
    This initializes a new AudioData object which can be used to read PCM audio data from raw bytes. This class is used internally when importing custom waveforms because the libraries used like to return the values as a bytes/memoryview object that is hard to convert directly to a native Python class.
- #### read
    **read()** takes no arguments and it returns the processed audio data as a list.
### safe_division (internal)
**safe_division(a: float, b: float)**

This function divides a by b. If b is 0, it returns 0 to avoid a division by zero exeption.

### map (internal)
**map(x: int, in_min: int, in_max: int, out_min: int, out_max: int)**

This function maps a value **x** to the range **out_min** - **out_max**. It is used internally for generating the sound visualizer images. It could be useful when writing sound code, though.

## Isolated internals
- ### Warning
    **These are all internal functions. They really are NOT meant to be used in sound or plug-in applier code.**
### compute_sound
**compute_sound(name: str, frequency: int, frames: int, code, progress_window: tkinter.Toplevel, progress_label: tkinter.Label)**

This is the function that takes in code and spits out the waveforms for the left and right channel.
### apply_plugins
**apply_plugins(name: str, code: str, waves: tuple, frequency: float)**

This function takes in the left and right waveforms, the plug-in applier code and spits out the modified left and right waveforms.

## Config options
### tempo
Changes the tempo at time stamps. For example:<br>
`tempo: 15>90` -> from note 15 on tempo is going to be 90 BPM.

You can change the tempo more than once by separating the values by commas.<br>
`tempo: 15>90, 20>120`

### transition
Sets the transition method between sounds. Valid values: `interpolate`, `remove`, `none`.

### transition_seconds
Sets the amount of time that will be atributed to transitioning between notes.

# How to make the binary
## Linux
1. `sudo apt install git python3-full portaudio19-dev` (adjust per your distro)
2. `git clone https://github.com/DevMa7e1/Absolute-CineWave`
3. `cd Absolute-CineWave`
4. `python3 -m venv venv`
5. `source venv/bin/activate`
6. `pip install -r requirements.txt`
7. `pip install pyinstaller`
8. `python3 -m PyInstaller -F -n AbsoluteCineWave --add-data blue.png:. --add-data cog.png:. --add-data gray.png:. --add-data plugin.png:. --add-data advanced_audio_functions.py:. main.py --hidden-import='PIL._tkinter_finder'`

## Windows
1. Make sure you have Python 3.12 or above installed
2. [Download the source code](https://github.com/DevMa7e1/Absolute-CineWave/archive/refs/heads/main.zip)
3. Unzip it
4. Open the resulting folder
5. Hit right click, press Open in Terminal
7. Make sure that you are using cmd by running the command `cmd`
6. Run the command `py -m venv venv` or, if that results in an error, try `python3 -m venv venv`
7. Run the command `./venv/Scripts/activate`
8. Run the command `pip install -r requirements.txt` and `pip install pyinstaller`
9. Run the command `python -m PyInstaller -F -n AbsoluteCineWave --add-data blue.png:. --add-data cog.png:. --add-data gray.png:. --add-data plugin.png:. --add-data advanced_audio_functions.py:. main.py -noconsole`

## MacOS
1. Make sure you have Homebrew installed
2. [Download the source code](https://github.com/DevMa7e1/Absolute-CineWave/archive/refs/heads/main.zip)
3. Open a new terminal window
4. `cd` into the unzipped source code
5. Run `brew update` and `brew install python@3.14 python-tk@3.14 portaudio`
6. Run `python3 -m venv venv`
7. Run `source ./venv/bin/activate`
8. Run `pip install -r requirements.txt`
9. Run `pip install py2app`
10. Run `py2applet --make-setup main.py audio_functions.py advanced_audio_functions.py extras.py isolated_internals.py blue.png cog.png gray.png plugin.png`
11. Run `python setup.py py2app`