#!/usr/bin/env python
#
# This is an attempt to reproduce
# 	http://vis.stanford.edu/protovis/ex/crimea-rose.html
import vp
import sys

months = [ "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec" ]
data = [
# wounds, other, disease
	[ 230, 460, 1440 ],
	[ 180, 520, 1270 ],	
	[ 155, 350,  935 ],
	[ 195, 195,  560 ],
	[ 180, 155,  550 ],
	[ 330, 130,  650 ],
	[ 260, 130,  430 ],
	[ 290, 110,  490 ],
	[ 355, 100,  290 ],
	[ 135,  95,  245 ],
	[ 100, 140,  325 ],
	[  40, 120,  215 ]
]

vis = vp.Graphic()

iter = vis.add(vp.Iterate())
iter.data = data

wedge = iter.add(vp.Wedge())
wedge.angle  = lambda: 90 - iter.index() * (360/12)
wedge.len    = -360/12
wedge.radius = 0
wedge.size   = lambda: iter.datum()[0] * .02
wedge.style  = "draw=black!30,fill=blue!20"

label = iter.add(vp.Label())
label.position = wedge.anchors().outer
label.label    = lambda: months[iter.index()]
label.rotate   = lambda: wedge.angle() - 90. + wedge.len()/2.

vis.render(sys.stdout)
