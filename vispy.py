#!/usr/bin/env python
import sys
import types
import new

# Support for prototypical based programming. This mainly means that if
# something isn't found in the current class then it is looked up in the
# object pointed to by prototype
class Prototype(object):
	def __init__(self, inherit=None):
		self.prototype = inherit

	def __getattr__(self, name):
		if self.prototype == None:
			raise AttributeError("'%s' object has no attribute '%s'" % (type(self), name))
		result = getattr(self.prototype, name)
		# Rebind methods to self if they are bound to prototype
		if (isinstance(result, types.MethodType) and
			result.im_self == self.prototype):
			result = new.instancemethod(result.im_func, self, result.im_class)
		return result

	def extend(self, prototype):
		self.prototype = prototype

class Mark(Prototype):
	defaults         = Prototype()
	defaults.data    = lambda d : [d]
	defaults.visible = True
	defaults.reverse = False
	defaults.left    = None
	defaults.right   = None
	defaults.top     = None
	defaults.bottom  = None

	def __init__(self, inherit = defaults):
		super(Mark,self).__init__(inherit)
		self.parent = None

	def render(self, out):
		out.write("% a mark\n")

	def set_parent(self, new_parent):
		self.parent = new_parent

	def evaluate(self, name):
		if hasattr(self, name):
			raw_value = getattr(self, name)
		else:
			raw_value = getattr(self.defaults, name)

		if callable(raw_value):
			return raw_value(self)
		return raw_value

class Bar(Mark):
	defaults           = Prototype(Mark.defaults)
	defaults.width     = None
	defaults.height    = None
	defaults.lineWidth = None
	defaults.drawStyle = None
	defaults.fillStyle = "fill=black"

	def __init__(self, inherit = defaults):
		super(Bar,self).__init__(inherit)

	def get_real_left(self):
		left = self.evaluate("left")
		if self.parent != None:
			left += self.parent.evaluate("left")
		return left

	def get_real_bottom(self):
		bottom = self.evaluate("bottom")
		if self.parent != None:
			bottom += self.parent.evaluate("bottom")
		return bottom

	def get_real_width(self):
		return self.evaluate("width")

	def get_real_height(self):	
		return self.evaluate("height")

	def get_real_style(self):
		drawStyle = self.evaluate("drawStyle")
		fillStyle = self.evaluate("fillStyle")
		if drawStyle == None:
			return fillStyle
		if fillStyle == None:
			return drawStyle
		return drawStyle + ", " + fillStyle

	def render(self, out):
		style = self.get_real_style()
		if style != None:
			out.write("\\path[%s] " % style)
			out.write("(%1.3f, %1.3f)" % (self.get_real_left(), self.get_real_bottom()))
			out.write(" rectangle ")
			out.write("+(%1.3f, %1.3f)" % (self.get_real_width(), self.get_real_height()))
			out.write(";\n")

class Panel(Bar):
	defaults           = Prototype(Bar.defaults)
	defaults.canvas    = None
	defaults.overflow  = "visible"
	defaults.fillStyle = None
	defaults.drawStyle = "draw=black"

	def __init__(self, inherit = defaults):
		super(Panel,self).__init__(inherit)
		self.children = []

	def add(self, mark):
		self.children.append(mark)
		mark.set_parent(self)
		return mark

	def render(self, out):
		super(Panel,self).render(out)
		for child in self.children:
			child.render(out)

class Graphic(Panel):
	defaults           = Prototype(Panel.defaults)
	defaults.options   = "[baseline=(current bounding box.south)]"
	defaults.left      = 0
	defaults.bottom    = 0
	defaults.fillStyle = None
	defaults.drawStyle = None

	def __init__(self, inherit = defaults):
		super(Graphic,self).__init__(inherit)

	def render(self, out):
		out.write("\\begin{tikzpicture}%s%%\n" % self.options)
		super(Graphic,self).render(out)
		out.write("\\end{tikzpicture}\n")

class Iterate(Prototype):
	def __init__(self):
		super(Iterate,self).__init__()
		self.children = []
		self.data     = []

	def additer(self, mark):
		mark.extend(self)
		self.children.append(mark)
		mark.set_parent(self.parent)
		return mark

	def render(self, out):
		# Iterate over all entries in the data list createing lightwight
		# prototypes with it and rendering them
		index = 0
		for datum in self.data:
			for child in self.children:
				obj       = Prototype(child)
				obj.datum = datum
				obj.index = index
				obj.render(out)
			index += 1

	def set_parent(self, new_parent):
		self.parent = new_parent

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
	
vis = Graphic()
vis.drawStyle = "draw=black"
vis.width     = 12
vis.height    = 6

iter = vis.add(Iterate())
iter.data = [1, 1.2, 1.7, 1.5, .7]

bar = iter.additer(Bar())
bar.bottom = 0
bar.width  = 20
bar.height = lambda self : self.datum * 80
bar.left   = lambda self : self.index * 25

# label = iter.add(Label(bar)):

vis.render(sys.stdout)
