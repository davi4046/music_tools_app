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

PITCHNAMES = ["A", "A#", "B", "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#"]

EXTENSIONS = {
    "3rd": {"Minor": 3, "Major": 4},
    "5th": {"Diminished": 6, "Perfect": 7},
    "7th": {"Minor": 10, "Major": 11},
    "9th": {"Minor": 1, "Major": 2},
    "11th": {"Perfect": 5, "Augmented": 6},
    "13th": {"Minor": 8, "Major": 9}
}