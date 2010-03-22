#!/usr/bin/env python
#
# An alternative version of speedup.py (which was not used in the end)
import vp
import sys

title = [ "benchmark", "gcc", "llvm", "heur4", "newalloc", "nocoal" ]
rows = [
	# benchmark,     gcc,    llvm, heur4, newalloc, bad
	[ "164.gzip",    119,   120,    107,  108,   118  ],
	[ "175.vpr",      86,    86,   91.6,  90.1,  94.4 ],
	[ "176.gcc",      49.2,  53.7, 53.1,  53.4,  56.3 ],
	[ "181.mcf",      58,    60.7, 59.3,  57.0,  59.0 ],
	[ "186.crafty",   63.4,  57.6, 56.5,  56.9,  59.4 ],
	[ "197.parser",  123,   133,  124  ,   122, 126   ],
	[ "253.perlbmk",  76.9,  83.9, 84.3,  87.7,  94.2 ],
	[ "254.gap",      57.4,  57.9, 62.7,  63.2,  66.4 ],
	[ "255.vortex",   94.2, 112,  101  ,   102, 105   ],
	[ "256.bzip2",    95.3, 101,   86.5,  86.6,  90.6 ],
	[ "300.twolf",   138,   137,  131  , 129,   139   ],
]

# Adapt data: create arry with (name, [nocoal, newalloc, heur4]) entries
class Data(object):
	pass

data = []
for row in rows:
	nocoal   = float(row[title.index("nocoal")])
	newalloc = float(row[title.index("newalloc")])
	heur4    = float(row[title.index("heur4")])
	# Calculate speedup compared to nocoal
	newalloc = nocoal/newalloc
	heur4    = nocoal/heur4
	if heur4 < 1.0:
		heur4 = 1.0
	nocoal   = 1.0

	datum = Data()
	datum.name  = row[title.index("benchmark")][4:]
	datum.newalloc = newalloc
	datum.heur4    = heur4
	datum.nocoal   = nocoal
	if datum.newalloc < datum.heur4:
		datum.high       = "heur4"
		datum.low_value  = datum.newalloc
		datum.high_value = datum.heur4
	else:
		datum.high       = "newalloc"
		datum.low_value  = datum.heur4
		datum.high_value = datum.newalloc
	#datum.data  = [ ("newalloc", newalloc), ("heur4", heur4) ]
	#datum.data  = sorted(datum.data, key=lambda x: x[1])
	data.append(datum)

styles = {}
styles["newalloc"] = "fill=green!40"
styles["heur4"]    = "fill=blue!15"
styles["nocoal"]   = "fill=black!30"

bar_width = 1.
bar_scale = 80.
bar_skip  = 0.6

def ifelse(cond,true,false):
	if cond:
		return true
	return false

def speedup_to_percent(val):
	return "%+.1f\\%%" % ((val - 1.0) * 100.)

def position_min_y(pos1, pos2):
	if pos1.y < pos2.y:
		return pos1
	return pos2

def position_max_y(pos1, pos2):
	if pos1.y > pos2.y:
		return pos1
	return pos2

vis = vp.Graphic()
vis.width  = len(data)*(bar_width+bar_skip)
vis.height = lambda: vis.width() * 3./4.
vis.style  = "draw,rounded corners=3pt"

title = vis.add(vp.Label())
title.label     = "Speedup"
title.placement = "north"
title.position  = vis.anchors().north
title.style     = "font=\\huge"

iter = vis.add(vp.Iterate())
iter.data = data
# base position
iter.base = lambda: vp.Position(bar_skip/2. + iter.index() * (bar_width+bar_skip), 0)

# lower-bar
low_bar = iter.add(vp.Rectangle())
low_bar.position = iter.base
low_bar.width    = bar_width
low_bar.height   = lambda: max(0., (iter.datum().low_value - 1.0) * bar_scale)
low_bar.style    = styles["nocoal"]

# higher part
high_bar = iter.add(vp.Rectangle())
high_bar.position = low_bar.anchors().north_west
#high_bar.width    = lambda: ifelse(iter.datum().high == "heur4",
#		bar_width-.3, bar_width)
high_bar.width    = bar_width
high_bar.height   = lambda: (iter.datum().high_value - iter.datum().low_value) * bar_scale
high_bar.style    = lambda: styles[iter.datum().high]

mytime = iter.add(vp.Line())
mytime.position = lambda: iter.base().move(0, (iter.datum().newalloc - 1.0) * bar_scale)
mytime.width    = bar_width
mytime.style    = "draw,thick"

change_label = iter.add(vp.Label())
change_label.position  = high_bar.anchors().center
change_label.placement = "center"
change_label.label     = lambda: ("%+.1f\\%%" %
	((iter.datum().newalloc - iter.datum().heur4) * 100.))

change_label2 = iter.add(vp.Label())
change_label2.position  = lambda: position_max_y(
		low_bar.anchors().center(),
		low_bar.anchors().south().move(0, .45))
change_label2.placement = "center"
change_label2.label     = lambda: speedup_to_percent(iter.datum().low_value)

#high_label = iter.add(vp.Label())
#high_label.position  = high_bar.anchors().north
#high_label.placement = "north"
#high_label.label     = lambda: speedup_to_percent(iter.datum().high_value)
#high_label.style     = "text=black"
#
#low_label = iter.add(vp.Label())
#low_label.position  = lambda: position_max_y(
#		low_bar.anchors().south().move(0, .45),
#		position_min_y(
#			high_bar.anchors().north().move(0, -.4),
#			low_bar.anchors().north()))
#low_label.placement = "north"
#low_label.label     = lambda: speedup_to_percent(iter.datum().low_value)
#low_label.style     = "text=black"

# Put label below bar
label = iter.add(vp.Label())
label.position  = lambda: low_bar.anchors().south().move(0, -.1)
label.placement = "north"
label.style     = "font=\\small"
label.label     = lambda: iter.datum().name


# Create a legend
#label0 = vis.add(vp.Label())
#label0.position = vis.anchors().north_east
#label0.label    = "compared to ``no coalescing''"
#
#legendno = vis.add(vp.Rectangle())
#legendno.position  = lambda: label0.anchors.north_west().move(-.1, 0)
#legendno.placement = "north east"
#legendno.style     = styles["nocoal"]
#
#label1 = vis.add(vp.Label())
#label1.position = label0.anchors().
#label1.label    = "compared to ``no coalescing''"
#
#legendno = vis.add(vp.Rectangle())
#legendno.position  = lambda: label0.anchors.north_west().move(-.1, 0)
#legendno.placement = "north east"
#legendno.style     = styles["nocoal"]



vis.render(sys.stdout)
