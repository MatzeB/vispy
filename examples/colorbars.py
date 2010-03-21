#!/usr/bin/env python
#
# Attempt to rebuild: http://applestooranges.com/blog/post/css-for-bar-graphs/
#  Vertical CSS Rectangle Graph example
import vp
import sys

data = [
	("Critical", 22, (0.99, 0.64, 0.67)),
	("High",     7,  (0.12, 0.80, 0.78)),
	("Medium",   3,  (0.16, 0.94, 0.76)),
	("Low",      8,  (0.61, 0.58, 0.70)),
	("Info",     2,  (0.27, 0.42, 0.51))
]

# little helper function
def addcolors(col1,col2):
	return (col1[0]+col2[0], col1[1]+col2[1], col1[2]+col2[2])

vis        = vp.Graphic()
vis.style  = "draw=black,rounded corners=3pt"
vis.width  = 7.5
vis.height = 6

# Part1: Draw some ruler lines
riter = vis.add(vp.Iterate(range(5,23,5)))

rule          = riter.add(vp.Line())
rule.position = lambda : vp.Position(0, riter.datum() * 0.25)
rule.xshift   = vis.width
rule.style    = "draw=black!30"

# Part2: draw bar, label on top of the bar and label below the bar for each
#        value

iter = vis.add(vp.Iterate(data))
# Project values out of the datum for convenience
iter.label = lambda : iter.datum()[0]
iter.value = lambda : iter.datum()[1]
iter.color = lambda : iter.datum()[2]

topcolor       = iter.add(vp.Color())
topcolor.color = iter.color 

bottomcolor       = iter.add(vp.Color())
bottomcolor.color = lambda: addcolors(iter.color(), (0, 0, +0.15))

bar = iter.add(vp.Rectangle())
bar.position = lambda : vp.Position(iter.index() * 1.5 + 0.5, 0)
bar.width    = 0.5
bar.height   = lambda : iter.value() * 0.25
bar.style    = lambda : "shade,shading=axis,top color=%s,bottom color=%s" % (topcolor.name(), bottomcolor.name())

label           = iter.add(vp.Label())
label.label     = iter.value
label.position  = bar.anchors().north
label.style     = "text=white"
label.placement = "north"

description           = iter.add(vp.Label())
description.label     = iter.label
description.position  = lambda : bar.anchors().south().move(0, -0.3)
description.style     = "text=black"
description.placement = "north"

vis.render(sys.stdout)
