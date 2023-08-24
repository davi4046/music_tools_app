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