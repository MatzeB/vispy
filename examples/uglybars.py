#!/usr/bin/env python
#
# Reproduction of bar charts from my last paper
# In retrospect the final image was quiet ugly ;-)
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

# Adapt data: create arry with (name, [gcc, llvm, newalloc]) entries
data = []
for row in rows:
	name     = row[title.index("benchmark")][4:]
	gcc      = float(row[title.index("gcc")])
	llvm     = float(row[title.index("llvm")])
	newalloc = float(row[title.index("newalloc")])
	# Normalize to gcc time
	llvm     = llvm/gcc
	newalloc = newalloc/gcc
	gcc      = 1.0

	data.append( (name, [gcc, llvm, newalloc]) )
barcolors = [ "black!20", "black!60", "black" ]

# helper
def ifelse(cond,true,false):
	if cond:
		return true
	return false

# Create the image
vis        = vp.Graphic()
vis.ptions = "baseline=(current bounding box.south)"
vis.width  = 12
vis.height = 6
vis.style  = "draw"

label_left = vis.add(vp.Label())
label_left.style     = "rotate=90"
label_left.placement = "south" # note that tikz seems to rotate the anchors
label_left.position  = vis.anchors().west().move(-0.4, 0)
label_left.label     = """
	\\centering
	\\small 
	\\begin{tabular}{c}
		Normalized Runtime \\\\
		(smaller is better)
	\\end{tabular}"""

# TODO: add bar legend here

one          = vis.add(vp.Line())
one.position = vp.Position(0, 4.)
one.xshift   = vis.width

iter      = vis.add(vp.Iterate())
iter.data = data

# convenience for placement
iter.base = lambda: vp.Position(iter.index() * 1.9, 0)

# Create 3 bars
bariter      = iter.add(vp.Iterate())
bariter.data = lambda: iter.datum()[1]

bar          = bariter.add(vp.Rectangle())
bar.position = lambda: iter.base().move(bariter.index()*0.5, 0)
bar.width    = 0.5
bar.height   = lambda: bariter.datum() * 4.
bar.style    = lambda: "fill=%s" % barcolors[bariter.index()]

# with a label on top of the bar
barlabel           = bariter.add(vp.Label())
barlabel.position  = lambda: ifelse(bar.height() > 4.005,
		bar.anchors().north(),
		bar.anchors().north().sety(4.005))
barlabel.label     = lambda: "%.2f" % bariter.datum()
barlabel.style     = "rotate=90,font=\\footnotesize"
barlabel.placement = "west"

# Place the benchmark name below the bars
label           = iter.add(vp.Label())
label.position  = lambda: iter.base().move(0.75, 0)
label.placement = "east"
label.style     = "rotate=90,font=\\small"
label.label     = lambda: iter.datum()[0]

vis.render(sys.stdout)
