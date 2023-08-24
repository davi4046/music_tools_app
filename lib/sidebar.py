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

import os
import webbrowser

import streamlit as st


def show_sidebar():    
    with st.sidebar:
        with st.expander("About MusicTools"):
            with open("res/about.txt") as file:
                st.write(file.read())
        
        columns = st.columns(2)
        
        columns[0].button(
                "View on GitHub",
                on_click=lambda: webbrowser.open("https://github.com/davi4046/music_tools_app")
        )
        
        columns[1].button(
                "Open License", 
                on_click=lambda: webbrowser.open(os.path.abspath("license.txt"))
        )
            
        columns = st.columns(2)
        
        columns[0].button(
                "Buy Me a Coffee ☕",
                on_click=lambda: webbrowser.open("https://www.buymeacoffee.com/davidrudpedersen")
        )