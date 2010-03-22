#!/usr/bin/env python
#
# A picture from a talk for my paper: It compares code generated by 2 different
# algorithms and tries to demonstrate that the code improves definitely over
# not using an algorithm at all and performs nearly as well as a more expensive
# algorithm
import vp
import sys

title = [ "benchmark", "gcc", "llvm", "heur4", "prefalloc", "nocoal" ]
rows = [
	# benchmark,     gcc,    llvm, heur4, prefalloc, nocoal
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

class Data(object):
	pass

# Preprocess data
data = []
for row in rows:
	nocoal    = float(row[title.index("nocoal")])
	prefalloc = float(row[title.index("prefalloc")])
	heur4     = float(row[title.index("heur4")])
	# Calculate speedup compared to nocoal
	prefalloc = nocoal/prefalloc
	heur4     = nocoal/heur4

	datum = Data()
	datum.name      = row[title.index("benchmark")][4:]
	datum.prefalloc = prefalloc
	datum.heur4     = heur4
	datum.nocoal    = nocoal
	if datum.prefalloc < datum.heur4:
		datum.high       = "heur4"
		datum.low_value  = datum.prefalloc
		datum.high_value = datum.heur4
	else:
		datum.high       = "prefalloc"
		datum.low_value  = datum.heur4
		datum.high_value = datum.prefalloc
	datum.difference = datum.high_value - datum.low_value
	datum.delta      = datum.prefalloc - datum.heur4
	data.append(datum)

styles = {}
styles["prefalloc"] = "fill=green!50"
styles["heur4"]     = "fill=blue!30"
styles["nocoal"]    = "fill=black!30"

def ifelse(cond,true,false):
	if cond:
		return true
	return false

def speedup_to_percent(val):
	return "%.1f" % ((val - 1.0) * 100.)

def position_min_y(pos1, pos2):
	if pos1.y < pos2.y:
		return pos1
	return pos2

def position_max_y(pos1, pos2):
	if pos1.y > pos2.y:
		return pos1
	return pos2

bar_width = 0.5
bar_scale = 80.
bar_skip  = 0.3


vis = vp.Graphic()
vis.width  = len(data)*(bar_width*2+bar_skip)
vis.height = lambda: vis.width() * 3./4.
vis.style  = "draw,rounded corners=3pt"

title = vis.add(vp.Label())
title.label     = "Speedup in Percent"
title.placement = "north"
title.position  = lambda: vis.anchors().north()
title.style     = "font=\\huge"

iter = vis.add(vp.Iterate())
iter.data = data
# base position
iter.base = lambda: vp.Position(bar_skip/2. + iter.index() * (bar_width*2+bar_skip), 0)

# 2 Bars for prefalloc and heur4

bar0 = iter.add(vp.Rectangle())
bar0.position = iter.base
bar0.width    = bar_width
bar0.height   = lambda: max(0., (iter.datum().prefalloc - 1.0) * bar_scale)
bar0.style    = styles["prefalloc"]

bar1 = iter.add(vp.Rectangle())
bar1.position = bar0.anchors().south_east
bar1.width    = bar_width
bar1.height   = lambda: max(0., (iter.datum().heur4 - 1.0) * bar_scale)
bar1.style    = styles["heur4"]

# select the lower/higher one of the 2 bars
iter.lower  = lambda: ifelse(iter.datum().high == "heur4", bar0, bar1)
iter.higher = lambda: ifelse(iter.datum().high == "heur4", bar1, bar0)

# put line into the higher bar
line = iter.add(vp.Line())
line.position = lambda: iter.higher().anchors().south_west().move(
		0, iter.lower().height())
line.xshift   = lambda: iter.higher().width()
#line.position = lambda: iter.base().move(0,	iter.lower().height())
#line.xshift   = bar_width*2
line.style    = "draw=white,thick"

# Show the absoluate value of the lower bar
low_label = iter.add(vp.Label())
low_label.position  = lambda: position_max_y(
		iter.lower().anchors().north(),
		iter.lower().anchors().south().move(0, .45))
low_label.placement = "north"
low_label.style     = "font=\\small"
low_label.label     = lambda: speedup_to_percent(iter.datum().low_value)

# Show the difference between low and high
diff_label = iter.add(vp.Label())
diff_label.position  = lambda: iter.higher().anchors().north().move(
		0, -(iter.datum().difference/2.) * bar_scale)
diff_label.placement = "center"
diff_label.style     = "font=\\small"
diff_label.label     = lambda: "$\Delta %.1f$" % (iter.datum().difference * 100.)

# Put benchmark name below bar
label = iter.add(vp.Label())
label.position  = lambda: bar0.anchors().south_east().move(0, -.1)
label.placement = "north"
label.style     = "font=\\small"
label.label     = lambda: iter.datum().name


vis.render(sys.stdout)
