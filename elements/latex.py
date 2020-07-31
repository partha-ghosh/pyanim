import hashlib
import os

import bs4
import numpy as np

from .group import Group
from .path import Path
from .shapes import Rectangle


class TexConfig:
    main_font = None
    mono_font = None
    sans_font = None
    margin = 5.5


def use_fonts():
    return (f"\\setmainfont{{{TexConfig.main_font}}}" if TexConfig.main_font else "")
    +(f"\\setmonofont{{{TexConfig.mono_font}}}" if TexConfig.mono_font else "")
    +(f"\\setsansfont{{{TexConfig.sans_font}}}" if TexConfig.sans_font else "")


def Tex(expr):
    filename = int(hashlib.md5(bytes(f"{expr}", encoding="utf-8")).hexdigest(), 16)
    if not os.path.exists(f"/tmp/{filename}.tex"):
        with open(f'/tmp/{filename}.tex', 'w') as f:
            f.write(f'''
\\documentclass{{article}}
\\usepackage{{amsmath}}
\\usepackage{{amssymb}}
\\usepackage{{amsfonts}}
\\usepackage{{tikz}}
\\usepackage[a4paper, margin={TexConfig.margin}cm]{{geometry}}
\\usepackage{{fontspec}}
''' + use_fonts() + f'''
\\thispagestyle{{empty}}
\\begin{{document}}
{expr}
\\end{{document}}''')

        os.system(f"cd /tmp && xelatex -no-pdf {filename}.tex && dvisvgm -e -n {filename}.xdv")

    with open(f'/tmp/{filename}.svg', 'r') as f:
        soup = bs4.BeautifulSoup(f, 'xml')

    uses = soup.find_all('use')
    rects = soup.find_all('rect')

    def transform_tex_point(point, x, y):
        return complex(point.real + x, -point.imag - y)

    chars = Group()
    fx = float(uses[0].attrs['x'])
    fy = float(uses[0].attrs['y'])
    for use in uses:
        path = soup.find(id=use.attrs['xlink:href'][1:]).attrs['d']
        x = float(use.attrs['x']) - fx
        y = float(use.attrs['y']) - fy
        path = Path(path)
        path.matrix(np.array([[1, 0, 0, x], [0, -1, 0, -y], [0, 0, 1, 0], [0, 0, 0, 1.0]]))
        chars.append(path)
    for rect in rects:
        x = float(rect.attrs['x']) - fx
        y = float(rect.attrs['y']) - fy
        width = float(rect.attrs['width'])
        height = float(rect.attrs['height'])
        r = Rectangle(0, 0, width, height)
        r.matrix(np.array([[1, 0, 0, x], [0, -1, 0, -y], [0, 0, 1, 0], [0, 0, 0, 1.0]]))
        chars.append(r)

    # if merge:
    #     tex = Path("")
    #     for char in chars:
    #         tex.append(char.path)
    #     tex.place_at_pos(0, 0)
    #     tex.update(stroke_width=stroke_width)
    #     tex.scale(scale)
    #     return tex
    # else:
    chars.fill([255, 255, 255]).stroke([255, 255, 255]).stroke_width(1)
    chars.scale(8, 8)
    return chars
