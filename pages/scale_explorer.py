import os

import pygame.mixer
import pyperclip
import streamlit as st
from midiutil.MidiFile import MIDIFile

import lib.circmath as circmath
from lib.constants import EXTENSIONS, PITCHNAMES
from lib.sidebar import show_sidebar
from lib.style import style

style()
show_sidebar()

# Session State Variables

for x in st.session_state:
    if x.startswith("p_"):
            st.session_state[x] = st.session_state[x]

variables = {
    "p_scale_binary": bin(2741)[2:].zfill(12),
    "p_scale_root_index": 0,
    "p_chord_binary": "000000000000",
    "p_chord_root_index": -1,
}

for x in range(12):
    variables["scale_checkbox_"+str(x)] = False
    variables["chord_checkbox_"+str(x)] = False

for x in variables:
    if x not in st.session_state:
        st.session_state[x] = variables[x]

# Synchronization

## Chord

if "update_chord_by_checkbox" not in st.session_state:
    st.session_state["update_chord_by_checkbox"] = False

if "update_chord_by_root" not in st.session_state:
    st.session_state["update_chord_by_root"] = False

if "update_chord_by_decimal" not in st.session_state:
    st.session_state["update_chord_by_decimal"] = False

if "update_chord_by_selectbox" not in st.session_state:
    st.session_state["update_chord_by_selectbox"] = False

def set_update_chord_by_checkbox():
    st.session_state["update_chord_by_checkbox"] = True

def set_update_chord_by_root():   
    st.session_state["p_chord_root_index"] = circmath.circ_sub(PITCHNAMES.index(st.session_state["chord_root"]), st.session_state["p_scale_root_index"], 0, 12)
    st.session_state["update_chord_by_root"] = True

def set_update_chord_by_decimal():
    st.session_state["update_chord_by_decimal"] = True

def set_update_chord_by_selectbox():
    st.session_state["update_chord_by_selectbox"] = True

def sync_chord_checkboxes():
    for x in range(12):
        st.session_state["chord_checkbox_"+str(x)] = st.session_state["p_chord_binary"][x] == "1"

def sync_chord_decimal():
    chord_binary = st.session_state["p_chord_binary"][::-1]
    chord_root_index = st.session_state["p_chord_root_index"]
    binary = chord_binary[chord_root_index:] + chord_binary[:chord_root_index]
    st.session_state["chord_decimal"] = int(binary[::-1], 2)

def sync_chord_selectboxes():
    intervals = []
    for x in range(12):
        if x != st.session_state["p_chord_root_index"] and st.session_state["p_chord_binary"][11-x] == "1":
            intervals.append((x - st.session_state["p_chord_root_index"]) % 12)
    for generic_interval in list(EXTENSIONS.keys()):
        
        options = list(EXTENSIONS[generic_interval].keys())
        
        first_interval_present = EXTENSIONS[generic_interval][options[0]] in intervals
        
        if len(options) > 1:
            second_interval_present = EXTENSIONS[generic_interval][options[1]] in intervals
        else:
            second_interval_present = False
        
        if first_interval_present and second_interval_present:
            st.session_state[generic_interval] = "Both"
        elif first_interval_present:
            st.session_state[generic_interval] = options[0]
        elif second_interval_present:
            st.session_state[generic_interval] = options[1]
        else:
            st.session_state[generic_interval] = "Omit"

def ensure_valid_chord_root():
    if st.session_state["p_chord_binary"][::-1][st.session_state["p_chord_root_index"]] == "0":
        first_index = st.session_state["p_chord_binary"][::-1].find("1", 0, -1)
        st.session_state["p_chord_root_index"] = first_index

def sync_chord_to_scale():
    # Mask chord_binary with scale_binary
    chord_decimal = int(st.session_state["p_chord_binary"], 2)
    scale_decimal = int(st.session_state["p_scale_binary"], 2)
    result = chord_decimal & scale_decimal
    result_binary = bin(result)[2:].zfill(12)
    st.session_state["p_chord_binary"] = result_binary
    ensure_valid_chord_root()

if st.session_state["update_chord_by_checkbox"]:
    new_chord_binary = ""
    for x in range(12):
        if st.session_state["chord_checkbox_"+str(x)]:
            new_chord_binary += "1"
        else:
            new_chord_binary += "0"
    st.session_state["p_chord_binary"] = new_chord_binary
    ensure_valid_chord_root()
    sync_chord_decimal()
    sync_chord_selectboxes()
    st.session_state["update_chord_by_checkbox"] = False

if st.session_state["update_chord_by_root"]:
    sync_chord_decimal()
    sync_chord_selectboxes()
    st.session_state["update_chord_by_root"] = False

if st.session_state["update_chord_by_decimal"]:

    st.session_state["update_chord_by_decimal"] = False

if st.session_state["update_chord_by_selectbox"]:
    intervals = [0]
    for x in range(6):
        generic_interval = list(EXTENSIONS.keys())[x]
        specific_interval = st.session_state[generic_interval]
        if specific_interval == "Omit":
            continue
        if specific_interval == "Both":
            for specific_interval in list(EXTENSIONS[generic_interval].keys()):
                intervals.append(EXTENSIONS[generic_interval][specific_interval])
        else:
            intervals.append(EXTENSIONS[generic_interval][specific_interval])
    new_chord_binary = ""
    for x in range(12):
        if (x - st.session_state["p_chord_root_index"]) % 12 in intervals:
            new_chord_binary += "1"
        else:
            new_chord_binary += "0"
    st.session_state["p_chord_binary"] = new_chord_binary[::-1] # Reverse
    sync_chord_checkboxes()
    sync_chord_decimal()
    sync_chord_selectboxes()
    st.session_state["update_chord_by_selectbox"] = False

## Scale

if "update_scale_by_checkbox" not in st.session_state:
    st.session_state["update_scale_by_checkbox"] = False

if "update_scale_by_root" not in st.session_state:
    st.session_state["update_scale_by_root"] = False

if "update_scale_by_decimal" not in st.session_state:
    st.session_state["update_scale_by_decimal"] = False

def set_update_scale_by_checkbox():
    st.session_state["update_scale_by_checkbox"] = True

def set_update_scale_by_root():
    st.session_state["update_scale_by_root"] = True

def set_update_scale_by_decimal():
    st.session_state["update_scale_by_decimal"] = True

def sync_scale_checkboxes():
    for x in range(12):
        st.session_state["scale_checkbox_"+str(x)] = st.session_state["p_scale_binary"][x] == "1"

def sync_scale_root():
    st.session_state["scale_root"] = PITCHNAMES[st.session_state["p_scale_root_index"]]

def sync_scale_decimal():
    st.session_state["scale_decimal"] = int(st.session_state["p_scale_binary"], 2)

if st.session_state["update_scale_by_checkbox"]:
    new_scale_binary = ""
    for x in range(12):
        if st.session_state["scale_checkbox_"+str(x)]:
            new_scale_binary += "1"
        else:
            new_scale_binary += "0"
    st.session_state["p_scale_binary"] = new_scale_binary
    sync_scale_decimal()
    sync_chord_to_scale()
    st.session_state["update_scale_by_checkbox"] = False

if st.session_state["update_scale_by_root"]:
    st.session_state["p_scale_root_index"] = PITCHNAMES.index(st.session_state["scale_root"])
    st.session_state["update_scale_by_root"] = False

if st.session_state["update_scale_by_decimal"]:
    
    if st.session_state["scale_decimal"] % 2 == 0:
        st.session_state["scale_decimal"] += 1
    
    st.session_state["p_scale_binary"] = bin(st.session_state["scale_decimal"])[2:].zfill(12)
    sync_scale_checkboxes()
    sync_chord_to_scale()
    st.session_state["update_scale_by_decimal"] = False

sync_scale_checkboxes()
sync_scale_root()
sync_scale_decimal()

sync_chord_checkboxes()
sync_chord_selectboxes()

# Manipulation

def rotate_chord_left():
    chord_binary = st.session_state["p_chord_binary"][::-1]
    chord_root_index = st.session_state["p_chord_root_index"]
    search_binary = chord_binary[chord_root_index:] + chord_binary[:chord_root_index]
    moves = search_binary[::-1].find("1", 0, -1) + 1
    st.session_state["p_chord_root_index"] = circmath.circ_sub(chord_root_index, moves, 0, 12)
    sync_chord_decimal()
    sync_chord_selectboxes()

def rotate_chord_right():
    if st.session_state["p_chord_binary"].count("1") <= 1:
        return
    chord_binary = st.session_state["p_chord_binary"][::-1]
    chord_root_index = st.session_state["p_chord_root_index"]
    search_binary = chord_binary[chord_root_index:] + chord_binary[:chord_root_index]
    moves = search_binary.find("1", 1, -1)
    st.session_state["p_chord_root_index"] = (chord_root_index + moves) % 12
    sync_chord_decimal()
    sync_chord_selectboxes()

def rotate_scale_left():
    if st.session_state["p_scale_binary"].count("1") <= 1:
        return
    new_scale_binary = st.session_state["p_scale_binary"][::-1]
    moves = new_scale_binary.find("1", 1, -1)
    new_scale_binary = new_scale_binary[moves:] + new_scale_binary[:moves]
    st.session_state["p_scale_binary"] = new_scale_binary[::-1]
    sync_scale_checkboxes()
    sync_scale_decimal()
    sync_chord_to_scale()

def rotate_scale_right():
    new_scale_binary = st.session_state["p_scale_binary"][::-1]
    moves = st.session_state["p_scale_binary"].find("1", 0, -1) + 1
    new_scale_binary = new_scale_binary[-moves:] + new_scale_binary[:-moves]
    st.session_state["p_scale_binary"] = new_scale_binary[::-1]
    sync_scale_checkboxes()
    sync_scale_decimal()
    sync_chord_to_scale()

# Playback

def play_scale():
    
    mf = MIDIFile(1)
    mf.addTempo(0, 0, 72)
    
    time = 0
    for x in range(12):
        if st.session_state["p_scale_binary"][::-1][x] == "1":
            pitch = 57 + st.session_state["p_scale_root_index"] + x
            mf.addNote(0, 0, pitch, time, 1, 100)
            time += 1
    
    with open("scale.mid", "wb") as f:
        mf.writeFile(f)
    
    pygame.mixer.init()
    pygame.mixer.music.load("scale.mid")
    pygame.mixer.music.play()
    
    os.remove("scale.mid")

def play_chord():
    
    mf = MIDIFile(1)
    mf.addTempo(0, 0, 72)
    
    binary = st.session_state["p_chord_binary"][::-1]
    binary = binary[st.session_state["p_chord_root_index"]:] + binary[:st.session_state["p_chord_root_index"]]
    for x in range(12):
        if binary[x] == "1":
            pitch = 57 + st.session_state["p_scale_root_index"] + st.session_state["p_chord_root_index"] + x
            mf.addNote(0, 0, pitch, 0, 2, 100)
    
    with open("chord.mid", "wb") as f:
        mf.writeFile(f)
    
    pygame.mixer.init()
    pygame.mixer.music.load("chord.mid")
    pygame.mixer.music.play()
    
    os.remove("chord.mid")

# Copying

def copy_scale():
    scale = "{0}-{1}".format(
        PITCHNAMES[st.session_state["p_scale_root_index"]],
        int(st.session_state["p_scale_binary"], 2)
    )
    st.session_state["p_scale"] = scale
    pyperclip.copy(scale)
    st.toast("Scale was copied to the clipboard!", icon="🎉")

def copy_chord():
    binary = st.session_state["p_chord_binary"][::-1]
    binary = binary[st.session_state["p_chord_root_index"]:] + binary[:st.session_state["p_chord_root_index"]]
    scale = "{0}-{1}".format(
        PITCHNAMES[(st.session_state["p_scale_root_index"] + st.session_state["p_chord_root_index"]) % 12],
        int(binary[::-1], 2)
    )
    st.session_state["p_scale"] = scale
    pyperclip.copy(scale)
    st.toast("Chord was copied to the clipboard!", icon="🎉")

# Layout

st.title("Scale Explorer")

## Scale

st.header("Scale")

columns = st.columns(12)

for x in range(12):
    with columns[x]:
        PITCHNAMES[(st.session_state["p_scale_root_index"] + x) % 12]
        st.checkbox(str(x), key="scale_checkbox_"+str(11-x), on_change=set_update_scale_by_checkbox, disabled=x==0, label_visibility="hidden")

st.selectbox("Root", PITCHNAMES, key="scale_root", on_change=set_update_scale_by_root)

st.number_input("Decimal", 0, 4095, step=2, key="scale_decimal", on_change=set_update_scale_by_decimal)

columns = st.columns(4)

disable_buttons = st.session_state["p_scale_binary"] == "000000000000"

with columns[0]:
    st.button("Play", key="play_scale", on_click=play_scale, disabled=disable_buttons)
with columns[1]:
    st.button("Copy", key="copy_scale", on_click=copy_scale, disabled=disable_buttons)
with columns[2]:
    st.button(":arrow_backward:", key="rotate_scale_left", on_click=rotate_scale_left, disabled=disable_buttons)
with columns[3]:
    st.button(":arrow_forward:", key="rotate_scale_right", on_click=rotate_scale_right, disabled=disable_buttons)

## Chord

st.header("Chord")

columns = st.columns(12)

for x in range(12):
    if st.session_state["p_scale_binary"][x] == "1":
        with columns[11 - x]:
            PITCHNAMES[(st.session_state["p_scale_root_index"] + 11 - x) % 12]
            st.checkbox(str(x), key="chord_checkbox_"+str(x), on_change=set_update_chord_by_checkbox, disabled=11 - x == st.session_state["p_chord_root_index"], label_visibility="hidden")

possible_roots = [
    PITCHNAMES[(st.session_state["p_scale_root_index"] + x) % 12]
    for x in range(12)
    if st.session_state["p_scale_binary"][11 - x] == "1"
    and st.session_state["p_chord_binary"][11 - x] == "1"
]

selected_index = 0
if st.session_state["p_chord_root_index"] != -1:
    selected_index = possible_roots.index(PITCHNAMES[(st.session_state["p_chord_root_index"] + st.session_state["p_scale_root_index"]) % 12])

st.selectbox("Root", possible_roots, selected_index, key="chord_root", on_change=set_update_chord_by_root)

# st.number_input("Decimal", 0, 4095, key="chord_decimal", on_change=set_update_chord_by_decimal, disabled=True)

columns = st.columns(6)

for x in range(6):
    with columns[x]:
        generic_interval = list(EXTENSIONS.keys())[x]
        options = ["Omit"]
        for specific_interval in EXTENSIONS[generic_interval]:
            if st.session_state["p_scale_binary"][11 - (EXTENSIONS[generic_interval][specific_interval] + st.session_state["p_chord_root_index"]) % 12] == "1":
                options += [specific_interval]
        if len(options) == 3:
            options += ["Both"]
        st.selectbox(generic_interval, options, key=generic_interval, on_change=set_update_chord_by_selectbox)

columns = st.columns(4)

disable_buttons = st.session_state["p_chord_binary"] == "000000000000"

with columns[0]:
    st.button("Play", key="play_chord", on_click=play_chord, disabled=disable_buttons)
with columns[1]:
    st.button("Copy", key="copy_chord", on_click=copy_chord, disabled=disable_buttons)
with columns[2]:
    st.button(":arrow_backward:", key="rotate_chord_left", on_click=rotate_chord_left, disabled=disable_buttons)
with columns[3]:
    st.button(":arrow_forward:", key="rotate_chord_right", on_click=rotate_chord_right, disabled=disable_buttons)