import numpy as np
from numpy import atan2, cos, degrees, radians, sin, tan

"""
running (a better way probably exists):
import placer
...
import importlib
importlib.reload(placer)
"""

"""
# or paste this for easier reloading (a better way probably exists)
def reload():
    shell.clear()
    import importlib
    importlib.reload(placer)
"""

KICAD = True
if KICAD:
    import pcbnew
    board = pcbnew.LoadBoard("D:\\Files\\ProgramFiles\\KiCad\\isomorphic90\\board1\\board1.kicad_pcb")

KEY_DIST_MM = 24.15
ROW_DIST_MM = KEY_DIST_MM * sin(radians(60))
ROW_HORIZ_OFFSET_MM = KEY_DIST_MM * cos(radians(60))
KEY_WIDTH_MM = 21.0
KEY_WIDTH_MAJOR_MM = 2.0 * KEY_WIDTH_MM * tan(radians(30))
ROW_HORIZ_ANGLE = degrees(atan2(2 * ROW_DIST_MM, 6 * KEY_DIST_MM))

KEY_DATA = [
    # (x offset, count)
    (0,  2),
    (1,  5),
    (0,  8),
    (1,  10),
    (0,  10),
    (1,  10),
    (0,  10),
    (1,  10),
    (0,  10),
    (5,  8),
    (10, 5),
    (17, 2),
]

# value=MX#, index=index into layout array
LAYOUT_TO_MX = [
     1, 2,
    11,12, 3, 4, 5,
    21,22,13,14,15, 6, 7, 8,
    31,32,23,24,25,16,17,18, 9,10,
    41,42,33,34,35,26,27,28,19,20,
    51,52,43,44,45,36,37,38,29,30,
    61,62,53,54,55,46,47,48,39,40,
    71,72,63,64,65,56,57,58,49,50,
    81,82,73,74,75,66,67,68,59,60,
          83,84,85,76,77,78,69,70,
                   86,87,88,79,80,
                            89,90
]

# Z-axis rotation affine
Rz = lambda t: np.matrix([
    [cos(t), -sin(t), 0],
    [sin(t), cos(t), 0],
    [0, 0, 1],
])

# Translation affine
T = lambda x, y: np.matrix([
    [1, 0, x],
    [0, 1, y],
    [0, 0, 1],
])

# Converts mm to PCB internal units
SCALE = 1000000
mmtop = lambda mm: mm / 19.05
ptomm = lambda u: u * 19.05
vec = lambda x,y: np.matrix([[x], [y], [1]])

# Where to place first switch
CENTER = (37, 42.4)

PREFIX_FILTER = "D"

if KICAD:
    # fps = list(pcbnew.GetBoard().GetFootprints())
    fps = list(board.GetFootprints())

if KICAD:
    mxs = sorted(
        (fp for fp in fps if fp.GetReference()[:len(PREFIX_FILTER)] == PREFIX_FILTER
                         and fp.GetReference()[len(PREFIX_FILTER):].isdigit()),
        key=lambda fp: int(fp.GetReference()[len(PREFIX_FILTER):])
    )
    for fp in mxs:
        name = fp.GetReference()
        print(f"{name}")
    
keys = np.matrix([[],[],[]])
# row num, unit stagger, num keys in row
for (row, (xoff, nkeys)) in enumerate(KEY_DATA):
    # col num
    for col in range(nkeys):
        new_key = vec(xoff * ROW_HORIZ_OFFSET_MM + col * KEY_DIST_MM, row * ROW_DIST_MM)
        keys = np.concatenate((keys, new_key), axis=1)

# apply global rotation
keys = Rz(radians(-ROW_HORIZ_ANGLE)) * keys

# apply global translation
keys = T(CENTER[0], CENTER[1]) * keys

if KICAD:
    # set footprints
    for i, pos in enumerate(keys.T):
        mx = mxs[LAYOUT_TO_MX[i]-1]
        print(f"---\n  mx={mx.GetReference()}\npos={pos}")
        mx.SetPosition(pcbnew.VECTOR2I(int(pos[0,0]*SCALE), int(pos[0,1]*SCALE)))

if KICAD:
    board.Save("D:\\Files\\ProgramFiles\\KiCad\\isomorphic90\\board1\\board1.kicad_pcb")
    print("saved")
