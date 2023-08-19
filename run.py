import sys

import streamlit.web.cli as stcli

if __name__ == "__main__":
    sys.argv = [
        "streamlit",
        "run",
        "main.py",
        "--global.developmentMode=false",
    ]
    sys.exit(stcli.main())