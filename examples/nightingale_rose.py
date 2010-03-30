#!/usr/bin/env python
#
# # Nightingales Rose
# 
# This is an attempt to reproduce
# <http://vis.stanford.edu/protovis/ex/crimea-rose.html>
import vp
import sys

months = [ "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec" ]
data = [
# wounds, other, diseases
	{ "date":  "4/1854", "wounds":  0, "other":110, "diseases": 110 },
	{ "date":  "5/1854", "wounds":  0, "other": 95, "diseases": 105 },
	{ "date":  "6/1854", "wounds":  0, "other": 40, "diseases":  95 },
	{ "date":  "7/1854", "wounds":  0, "other":140, "diseases": 520 },
	{ "date":  "8/1854", "wounds": 20, "other":150, "diseases": 800 },
	{ "date":  "9/1854", "wounds":220, "other":230, "diseases": 740 },
	{ "date": "10/1854", "wounds":305, "other":310, "diseases": 600 },
	{ "date": "11/1854", "wounds":480, "other":290, "diseases": 820 },
	{ "date": "12/1854", "wounds":295, "other":310, "diseases":1199 },
	{ "date":  "1/1855", "wounds":230, "other":460, "diseases":1440 },
	{ "date":  "2/1855", "wounds":180, "other":520, "diseases":1270 },	
	{ "date":  "3/1855", "wounds":155, "other":350, "diseases": 935 },
	{ "date":  "4/1855", "wounds":195, "other":195, "diseases": 560 },
	{ "date":  "5/1855", "wounds":180, "other":155, "diseases": 550 },
	{ "date":  "6/1855", "wounds":330, "other":130, "diseases": 650 },
	{ "date":  "7/1855", "wounds":260, "other":130, "diseases": 430 },
	{ "date":  "8/1855", "wounds":290, "other":110, "diseases": 490 },
	{ "date":  "9/1855", "wounds":355, "other":100, "diseases": 290 },
	{ "date": "10/1855", "wounds":135, "other": 95, "diseases": 245 },
	{ "date": "11/1855", "wounds":100, "other":140, "diseases": 325 },
	{ "date": "12/1855", "wounds": 40, "other":120, "diseases": 215 }
]
styles = {
	"wounds":   "fill=red!30,draw=red!10",
	"other":    "fill=black!20,draw=black!10",
	"diseases": "fill=blue!20,draw=blue!10",
}

data = data[0:12] # for now

vis = vp.Graphic()

iter = vis.add(vp.Iterate())
iter.data = data

# sort a "row" of data
iter.angle        = lambda: -0.25 + (iter.index() * (1./12.))
iter.month_year   = lambda: iter.datum()["date"].split("/")
iter.sorted_datum = lambda: sorted(
			filter(lambda x: x[0] != "date", iter.datum().iteritems()),
			key=lambda x: x[1])

inner_iter = iter.add(vp.Iterate())
inner_iter.data   = iter.sorted_datum
inner_iter.first()["radius"] = 0.

wedge = inner_iter.add(vp.Wedge())
wedge.angle  = iter.angle
wedge.len    = 1./12.
wedge.radius = lambda: inner_iter.radius()
wedge.size   = lambda: inner_iter.datum()[1] * .004 - inner_iter.radius()
wedge.style  = lambda: styles[inner_iter.datum()[0]]

inner_iter.next()["radius"] = lambda: wedge.radius() + wedge.size()

label = iter.add(vp.Label())
label.rotate   = lambda: iter.angle() + (1./12.)*0.5
label.position = lambda: vp.PolarCoordinate(vp.Origin, label.rotate(), max(inner_iter.radius(),1.5))
label.label    = lambda: months[int(iter.month_year()[0])-1]

vis.render(sys.stdout)
