#!/usr/bin/env python
import vp
import sys

indices = {
	  'benchname':0, 'gcc':1, 'llvm':2, 'heur4':3, 'newalloc':4, 'nocoal':5
}
data = [
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
	
vis = vp.Graphic()
vis.drawStyle = "draw=black"
vis.width     = 12
vis.height    = 6

# label_left = vis.add(vp.Label(vis.anchor("")))

iter = vis.add(vp.Iterate())
iter.data = [1, 1.2, 1.7, 1.5, .7]

bar = iter.add(vp.Bar())
bar.xshift = lambda : bar.index() * 1.5
bar.yshift = 0
bar.width  = 0.5
bar.height = lambda : bar.datum() * 4

label            = iter.add(vp.Label())
label.position   = bar.anchors().north
label.labelstyle = "text=white"
label.placement  = "south"

vis.render(sys.stdout)
