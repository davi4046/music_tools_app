"""
MusicTools - Music Generation Software
Copyright (C) 2023  David Rud Pedersen

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import json
import math
import os

import mido
import numpy as np
import plotly.graph_objects as go
import pygame.mixer
import pyperclip
import streamlit as st
from filedialogs import open_file_dialog, save_file_dialog
from midiutil import MIDIFile
from plotly.subplots import make_subplots

import lib.expression_bank as expression_bank
from lib.constants import PITCHNAMES
from lib.sidebar import show_sidebar
from lib.style import style

show_sidebar()
style()

# Auto copy 𝑥 to the clipboard

if pyperclip.paste() != "\U0001d465":
    pyperclip.copy("\U0001d465")
    st.toast("Copied '\U0001d465' to the clipboard.")
    
# Session State Variables

for x in st.session_state:
    if x.startswith("p_"):
            st.session_state[x] = st.session_state[x]

variables = {
    "p_time_numerator": 4,
    "p_time_denominator": 4,
    "p_tempo": 72,
    "p_length": 16,
    "p_scale": "C-2741",
    "p_expression_count": 0,
    "p_show_plot": False,
    "p_initial_x": "",
    "p_new_x": "",
    "p_pitch": "",
    "p_duration": "",
    "p_rest": "",
    "p_velocity": "",
    "p_default_savepath": "",
    "p_default_loadpath": "",
}

for x in variables:
    if x not in st.session_state:
        st.session_state[x] = variables[x]

# Functions

def add_expression():
    st.session_state["p_expression_count"] += 1

def remove_expression():
    st.session_state["p_expression_count"] -= 1

def quantize_duration(duration: float) -> float:
    return 2 ** round(math.log2(duration))

def get_pitchclassset_from_scale(scale: str) -> set[int]:
    root_str, decimal_str = scale.split("-", 1)

    root = PITCHNAMES.index(root_str)

    if root == -1:
        raise Exception("Invalid scale")

    try:
        decimal = int(decimal_str)
    except:
        raise Exception("Invalid scale")

    binary = bin(decimal)[2:].zfill(12)

    if len(binary) > 12:
        raise Exception("Invalid scale")

    pitches = []

    for x in range(12):
        if binary[11 - x] == "1":
            pitches.append(x + root - 3)

    return pitches

def degree_to_pitch(degree: int, pitchclassset: set[int]) -> int:
            octave = math.floor(degree / len(pitchclassset)) + 4
            return pitchclassset[degree % len(pitchclassset)] + 12 * octave

def compile_settings() -> str:
    settings = {
        "time_signature": {
            "numerator": st.session_state["p_time_numerator"],
            "denominator": st.session_state["p_time_denominator"],
        },
        "tempo": st.session_state["p_tempo"],
        "length": st.session_state["p_length"],
        "scale": st.session_state["p_scale"],
        "expressions": [
            st.session_state["p_expression_{}".format(x)]
            for x in range(st.session_state["p_expression_count"])
        ],
        "initial_x": st.session_state["p_initial_x"],
        "new_x": st.session_state["p_new_x"],
        "pitch": st.session_state["p_pitch"],
        "duration": st.session_state["p_duration"],
        "rest": st.session_state["p_rest"],
        "velocity": st.session_state["p_velocity"],
    }
    return json.dumps(settings)

def load_settings(settings: dict):
    st.session_state["p_time_numerator"] = settings["time_signature"]["numerator"]
    st.session_state["p_time_denominator"] = settings["time_signature"]["denominator"]
    st.session_state["p_tempo"] = settings["tempo"]
    st.session_state["p_length"] = settings["length"]
    st.session_state["p_scale"] = settings["scale"]
    st.session_state["p_initial_x"] = settings["initial_x"]
    st.session_state["p_new_x"] = settings["new_x"]
    st.session_state["p_pitch"] = settings["pitch"]
    st.session_state["p_duration"] = settings["duration"]
    st.session_state["p_rest"] = settings["rest"]
    st.session_state["p_velocity"] = settings["velocity"]
    st.session_state["p_expression_count"] = len(settings["expressions"])
    for i, expression in enumerate(settings["expressions"]):
        st.session_state["p_expression_{}".format(i)] = expression

def load_settings_from_file(path_to_file: str):
    midi = mido.MidiFile(path_to_file)
    settings = json.loads(midi.tracks[1][0].text)
    load_settings(settings)

def load_demo():
    try:
        load_settings_from_file("res/demo.mid")
    except:
        st.toast("Failed to load the demo.", icon="😢")
    else:
        st.toast("Successfully loaded the demo!", icon='🎉')

# Clear expressions

index = st.session_state["p_expression_count"]

while True:
    if "p_expression_" + str(x) not in st.session_state:
        break
    del st.session_state["p_expression_" + str(x)]
    index += 1

expression_bank.clear()

# Layout

st.title("Melody Creator")

columns = st.columns(2)

with columns[0]:
    st.number_input("Time Signature", 1, 128, key="p_time_numerator")
with columns[1]:
    st.selectbox(
        "denominator",
        [2**x for x in range(8)],
        key="p_time_denominator",
        label_visibility="hidden",
    )

st.number_input("Tempo", 12, None, key="p_tempo")

st.number_input("Length", 0, None, step=1, key="p_length", help="This value is in beats.")

st.text_input("Scale", key="p_scale")
if st.session_state["p_scale"] == "":
    st.info("**Scale** is unspecified.")
else:
    try:
        get_pitchclassset_from_scale(st.session_state["p_scale"])
    except:
        st.error("Scale is invalid.")

st.header("Expressions")

for x in range(st.session_state["p_expression_count"]):
    letter = chr(ord("A") + x)
    st.text_input(letter, key="p_expression_" + str(x))

columns = st.columns(2)

if st.session_state["p_expression_count"] < 26:
    with columns[0]:
        st.button("Add Expression", on_click=add_expression)

if st.session_state["p_expression_count"] > 0:
    with columns[1]:
        st.button("Remove Expression", on_click=remove_expression)

if st.session_state["p_expression_count"] > 0:
    st.checkbox("Show Plot", key="p_show_plot")

for x in range(st.session_state["p_expression_count"]):
    letter = chr(ord("A") + x)
    expression_bank.store(letter, st.session_state["p_expression_" + str(x)])

if st.session_state["p_show_plot"]:
    fig = make_subplots()

    for x in range(st.session_state["p_expression_count"]):
        expression = st.session_state["p_expression_" + str(x)]
        if expression != "":
            letter = chr(ord("A") + x)
            x = np.linspace(0, 10, 500)
            y = []
            for x_value in x:
                try:
                    y.append(expression_bank.evaluate(expression, x_value))
                except:
                    st.error(
                        "**{}** failed to evaluate at x={}".format(letter, x_value)
                    )
                    break
            trace = go.Scatter(x=x, y=y)
            if trace != None:
                trace.name = letter
                fig.add_trace(trace)
            else:
                st.error("**{}** failed to evaluate.".format(letter))

    st.plotly_chart(fig)

st.header("Generation")

is_ready = True

st.text_input("Initial X", key="p_initial_x", help="The x-value from which the first note will be derived.")
if st.session_state["p_initial_x"] == "":
    st.info("**Initial X** is unspecified.")
    is_ready = False

st.text_input("New X", key="p_new_x", help="Expression for finding the next x-value to derive a note from.")
if st.session_state["p_new_x"] == "":
    st.info("**New X** is unspecified.")
    is_ready = False

st.text_input("Pitch", key="p_pitch", help="Gets converted from scale degree to pitch in the specifed scale.")
if st.session_state["p_pitch"] == "":
    st.info("**Pitch** is unspecified.")
    is_ready = False

st.text_input("Duration", key="p_duration", help="1.0 = quarter note")
if st.session_state["p_duration"] == "":
    st.info("**Duration** is unspecified.")
    is_ready = False

st.text_input("Rest", key="p_rest", help="Boolean statement that, if true, will make the note a rest/pause.")
if st.session_state["p_rest"] == "":
    st.info("**Rest** is unspecified.")
    is_ready = False

st.text_input("Velocity", key="p_velocity", help="Value from **0-127** determining the loudness of the note.")
if st.session_state["p_velocity"] == "":
    st.info("**Velocity** is unspecified.")
    is_ready = False

# Generation

if is_ready:
    try:
        mf = MIDIFile(1)
        mf.addText(0, 0, compile_settings())
        mf.addTempo(0, 0, st.session_state["p_tempo"])
        mf.addTimeSignature(
            0,
            0,
            st.session_state["p_time_numerator"],
            int(math.log2(st.session_state["p_time_denominator"])),
            24,
        )
        
        pitchclassset = get_pitchclassset_from_scale(st.session_state["p_scale"])

        try:
            x = expression_bank.evaluate(st.session_state["p_initial_x"])
        except:
            raise Exception("**Initial X** failed to evaluate.")
        
        time = 0

        while time < st.session_state["p_length"]:
            try:
                p_new_x = float(expression_bank.evaluate(st.session_state["p_new_x"], x))
            except:
                raise Exception("**New X** failed to evaluate at x = {}".format(x))
            try:
                pitch = int(expression_bank.evaluate(st.session_state["p_pitch"], x))
            except:
                raise Exception("**Pitch** failed to evaluate at x = {}".format(x))
            try:
                duration = float(expression_bank.evaluate(st.session_state["p_duration"], x))
            except:
                raise Exception("**Duration** failed to evaluate at x = {}".format(x))
            try:
                is_rest = bool(expression_bank.evaluate(st.session_state["p_rest"], x))
            except:
                raise Exception("**Rest** failed to evaluate at x = {}".format(x))
            try:
                velocity = int(expression_bank.evaluate(st.session_state["p_velocity"], x))
            except:
                raise Exception("**Velocity** failed to evaluate at x = {}".format(x))

            duration = max(0, duration)

            if duration > 0:
                duration = quantize_duration(duration)
                if not is_rest:
                    pitch = min(128, max(0, degree_to_pitch(pitch, pitchclassset)))
                    velocity = max(0, min(127, velocity))
                    mf.addNote(0, 0, pitch, time, duration, velocity)

            x = p_new_x
            time += duration

    except Exception as e:
        st.exception(e)
    else:
        st.success("Generation succeeded!", icon="🎉")

# Playback

def play():
    try:
        with open("melody.mid", "wb") as f:
            mf.writeFile(f)
    except:
        st.toast("Failed to write output to MIDI.", icon='😢')
    else:
        pygame.mixer.init()
        pygame.mixer.music.load("melody.mid")
        pygame.mixer.music.play()
        os.remove("melody.mid")

def stop():
    pygame.mixer.music.stop()

# Save and load

def save():
    wd = os.getcwd()
    savepath = save_file_dialog(
        "Save File", 
        default_name=st.session_state["p_default_savepath"],
        ext=[("MIDI file", "mid")]
    )
    if savepath:
        try:
            with open(savepath, "wb") as f:
                mf.writeFile(f)
        except:
            st.toast("Failed to write output to MIDI.", icon='😢')
        st.session_state["p_default_savepath"] = savepath
    os.chdir(wd)

def load():
    wd = os.getcwd()
    openpath = open_file_dialog(
        "Load File",
        directory=st.session_state["p_default_loadpath"],
        ext=[("MIDI file", "mid")]
    )
    if openpath:
        try:
            load_settings_from_file(openpath)
        except:
            st.toast("Failed to load settings from file.", icon="😢")
        else:
            st.session_state["p_default_loadpath"] = os.path.dirname(openpath)
            st.session_state["p_default_savepath"] = openpath
    os.chdir(wd)

# Buttons

st.divider()

columns = st.columns(4)

with columns[0]:
    st.button("Play", on_click=play, disabled=not is_ready)
with columns[1]:
    st.button("Stop", on_click=stop)
with columns[2]:
    st.button("Save", on_click=save, disabled=not is_ready)
with columns[3]:
    st.button("Load", on_click=load)


# Configure sidebar

with st.sidebar:
    
    st.divider()
    
    columns = st.columns(2)
    
    columns[0].button(
        "Load Demo", 
        on_click=lambda: load_demo()
    )