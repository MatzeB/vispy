#!/usr/bin/env python
#
# # Stacked barchart
#
# A stacked barchart. This mimicks: 
# <http://de.wikipedia.org/wiki/Datei:Anteil_Nimitz.png>
import vp
import sys

data = [
	{ "year":1975, "complete": 14, "nimitz":  1 },
	{ "year":1980, "complete": 13, "nimitz":  2 },
	{ "year":1985, "complete": 14, "nimitz":  3 },
	{ "year":1990, "complete": 15, "nimitz":  5 },
	{ "year":1995, "complete": 12, "nimitz":  6 },
	{ "year":2000, "complete": 12, "nimitz":  8 },
	{ "year":2005, "complete": 12, "nimitz":  9 },
	{ "year":2010, "complete": 11, "nimitz": 10 },
]

bar_width       = 0.33
bar_space_left  = 0.33
bar_space_right = 0.33
bar_skip        = bar_width + bar_space_left + bar_space_right
data_scale      = 0.15

vis = vp.Graphic()

data_area = vis.add(vp.SubGraphics())

# Scale
scale_iter = data_area.add(vp.Iterate())
scale_iter.data = lambda: range(0, 17, 2)

scale_line = scale_iter.add(vp.Line())
scale_line.position = lambda: vp.Position(0, scale_iter.datum() * data_scale)
scale_line.xshift = 10 # calculated panel width...
scale_line.style = lambda: "draw=black!40" if scale_iter.datum() > 0 else "draw=black"

scale_label = scale_iter.add(vp.Label())
scale_label.position = lambda: scale_line.anchors().begin().move(-0.25, 0)
scale_label.placement = "east"
scale_label.label     = scale_iter.datum

# Bars and Bar labels
iter = data_area.add(vp.Iterate())
iter.data = data

bar_c = iter.add(vp.Rectangle())
bar_c.position = lambda: vp.Position(bar_space_left + iter.index() * bar_skip, 0)
bar_c.height   = lambda: iter.datum()["complete"] * data_scale
bar_c.style    = "shade,shading=axis,top color=blue!70,bottom color=blue!65"
bar_c.width    = bar_width

bar_n = iter.add(vp.Rectangle())
bar_n.position = bar_c.anchors().south_west
bar_n.height   = lambda: iter.datum()["nimitz"] * data_scale
bar_n.style    = "shade,shading=axis,top color=red!70,bottom color=red!65"
bar_n.width    = bar_width

barlabel = iter.add(vp.Label())
barlabel.position = lambda: bar_c.anchors().south().move(0, -0.25)
barlabel.label    = lambda: iter.datum()["year"]
barlabel.placement = "north"

vis.render(sys.stdout)
