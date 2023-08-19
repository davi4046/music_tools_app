from st_pages import show_pages_from_config
from streamlit_extras.switch_page_button import switch_page

show_pages_from_config("pages/pages.toml")

switch_page("melody_creator")