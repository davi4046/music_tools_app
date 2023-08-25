# MusicTools
MusicTools is a small application for generating music, consisting of currently two tools: Scale Explorer and Melody Creator.

## Scale Explorer

Scale Explorer uses a binary system for defining scales, inspired by [A study of musical scales by Ian Ring](https://ianring.com/musictheory/scales/).

Here are the features:

- Pick a scale by turning on and off bits and selecting a root note.
- Easily find chords within the scale.
- Listen to playback of both chord and scale.
- Copy the chord or scale into Melody Creator.
- Rotate to find scales within the same family or to invert chords.
- View chord name and scale name in the sidebar.

## Melody Creator

Melody Creator uses mathematical expressions to generate melodies.

Here are the features:

- Select time signature, tempo, length, and scale.
- Create reusable expressions, each assigned a letter from A-Z.
- View the reusable expressions as graphs.
- Define note pitch, duration, velocity, and type by expressions.
- Listen to playback of the generated melody.
- Save and load melodies to/from MIDI.

## Making Changes

This is for people who want to make alterations to the code of the program.

1. Pull the repository unto your computer with Git or download it from [GitHub](https://github.com/davi4046/music_tools_app).
2. Setup a virtual environment in the root directory of the project.
3. Enter the virtual environment in your IDE and the terminal.
4. Use a package manager like pip to install the packages in the `requirements.txt` file.
5. Make the wanted changes to the code.
6. Run `streamlit run main.py` in the terminal to test the changes.

## Building Changes

These instructions assume that you've done the steps under [Making Changes](#making-changes).

1. If your changes uses any new packages not from the standard library, these must be added to the `requirements.txt` file. If you've added a lot of imports, you can use the [pipreqs](https://pypi.org/project/pipreqs/) package to collect the requirements.

    - Install [pipreqs](https://pypi.org/project/pipreqs/) in the virtual environment with your package manager.
   
    - Run `pipreqs` in the terminal. The `requirement.txt` file will now contain all imported packages.
  
2. Install the [pyinstaller](https://pypi.org/project/pyinstaller/) package in the virtual environment with your package manager.
   
3. Run `pyinstaller --onefile run.py --clean` in the terminal. This will generate a `run.spec` file in the directory.
  
4. Add the following code in the beginning of the `run.spec` file:

```
from PyInstaller.utils.hooks import collect_data_files, copy_metadata

datas = [("project_env/Lib/site-packages/streamlit/runtime", "./streamlit/runtime")]
datas += collect_data_files("streamlit")
datas += copy_metadata("streamlit")
```

5. Replace `project_env/Lib` with the path to the `site_packages` directory in your virtual environment directory.

6. In `run.spec`, set pathex to this:

```
a = Analysis(
    ...
    pathex=["."],
    ...
)
```

7. In `run.spec`, write all imports under `hiddenimports`. For example:

```
a = Analysis(
    ...
    hiddenimports=["midiutil", "mido", "numpy", "plotly", "pygame", "pyperclip", "st_pages", "streamlit", "streamlit_extras.switch_page_button", "filedialogs"],
    ...
)
```

8. Run `pyinstaller run.spec --clean` in the terminal. In the `dist` directory, you will find `run.exe`.

9. To test the build, you need to *copy* any files used by the application into the `dist` directory (while maintaining their original directory structure). By default it should look like this:
   
```
dist/
├─ lib/
├─ pages/
├─ res/
├─ main.py
├─ license.txt
├─ run.exe
```

10. Now go ahead and run `run.exe`. The application should start now.
  
11. If you get an error that an import is missing, add it to the `hiddenimports` variable and run `pyinstaller run.spec --clean` again.

**If something still isn't working, feel free to let me know. I will gladly try to help you out.**

## Distribution

If you want to more easily distribute your version, you can use something like [Inno Setup](https://jrsoftware.org/isdl.php) to create an installer.

Just make sure the structure of the `dist` directory is maintained when installing.
