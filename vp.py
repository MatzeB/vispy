#!/usr/bin/env python
from prototype import Prototype

class Position(object):
	def __init__(self, x, y, anchor=None):
		self.x = x
		self.y = y
		self.anchor = anchor

	def move(self, x, y):
		return Position(self.x + x, self.y + y, self.anchor)

	def setx(self, x):
		return Position(x, self.y, self.anchor)
	
	def sety(self, y):
		return Position(self.x, y, self.anchor)
	
	def write(self, out):
		if self.anchor == None:
			str = "(%.3f, %.3f)" % (self.x, self.y)
		elif self.x == 0 and self.y == 0:
			str = "(%s)" % self.anchor
		else:
			str = "([xshift=%.3f,yshift=%.3f]%s)" % (self.x, self.y, self.anchor)
		out.write(str)

class PolarCoordinate(object):
	def __init__(self, middle, angle, radius):
		self.middle = middle
		self.angle  = angle
		self.radius = radius

	def move(self, x, y):
		return PolarCoordinate(self.middle.move(x, y), self.angle, self.radius)

	def write(self, out):
		assert self.middle.anchor == None  # not supported yet
		str = "([xshift=%.3f,yshift=%.3f]%.3f:%.3f)" % (self.middle.x, self.middle.y, self.angle, self.radius)
		out.write(str)

Origin = Position(0, 0)

class Mark(Prototype):
	defaults          = Prototype()
	defaults.position = Origin

	def __init__(self):
		super(Mark,self).__init__()
		self.parent = None

	# A special getter which always returns lazy values
	def __getattribute__(self, name):
		try:
			val = super(Mark,self).__getattribute__(name)
		except AttributeError:
			# if we can't find the value look it up in defaults
			defaults = super(Mark,self).__getattribute__("defaults")
			val = getattr(defaults, name)

		if not callable(val):
			return lambda : val
		return val

	def render(self, out):
		out.write("% a mark\n")

	def set_parent(self, new_parent):
		self.parent = new_parent

class AnchorGetter(object):
	def __init__(self, target):
		self.target = target

	def __getattr__(self, name):
		anchor = self.target.get_anchor(name)
		if anchor == None:
			raise AttributeError("'%s' has no anchor '%s'" % (self.target, name))
		return anchor

class Rectangle(Mark):
	defaults           = Prototype(Mark.defaults)
	defaults.placement = "south west"
	defaults.width     = 1.0
	defaults.height    = 1.0
	defaults.style     = None

	def __init__(self):
		super(Rectangle,self).__init__()
		self.anchors = AnchorGetter(self)

	def get_anchor(self, name):
		assert self.placement() == "south west" # no support for other placements (yet)
		base = self.position

		if name == "south_west":
			return base
		elif name == "south":
			return lambda : base().move(self.width() / 2., 0)
		elif name == "south_east":
			return lambda : base().move(self.width(), 0)
		elif name == "west":
			return lambda : base().move(0, self.height() / 2.)
		elif name == "center":
			return lambda : base().move(self.width() / 2., self.height() / 2.)
		elif name == "east":
			return lambda : base().move(self.width(), self.height() / 2.)
		elif name == "north_west":
			return lambda : base().move(0, self.height())
		elif name == "north":
			return lambda : base().move(self.width() / 2., self.height())
		elif name == "north_east":
			return lambda : base().move(self.width(), self.height())
		return None

	def render(self, out):
		style = self.style()
		# No need to draw anything if style isn't set
		if style == None:
			return

		out.write("\\path[%s] " % style)
		self.anchors().south_west().write(out)
		out.write(" rectangle ")
		self.anchors().north_east().write(out)
		out.write(";\n")

class Label(Mark):
	defaults           = Prototype(Mark.defaults)
	defaults.placement = "south"
	defaults.label     = ""
	defaults.style     = ""
	defaults.rotate    = None

	id = 0

	def __init__(self):
		super(Label,self).__init__()
		self.anchors = AnchorGetter(self)

	def get_anchor(self, name):
		myname = self.__myname
		if name in [ "north_west", "north", "north_east", "west", "center", "east", "south_west", "south", "south_east" ]:
			name = name.replace("_", " ")
			return (lambda : Position(0, 0, "%s.%s" % (self.__myname, name)))

	def render(self, out):
		style     = self.style()
		label     = self.label()
		placement = self.placement()
		rotate    = self.rotate()
		if rotate != None:
			if style != None:
				style += ","
			style += "rotate=%s" % rotate

		if style != None:
			style += ","
		style += "anchor=%s" % placement

		self.__myname = "label%d" % Label.id
		Label.id += 1

		out.write("\\node[%s] (%s) at " % (style, self.__myname()))
		self.position().write(out)
		out.write(" { %s }" % label)
		out.write(";\n")

class Panel(Rectangle):
	defaults = Prototype(Rectangle.defaults)

	def __init__(self):
		super(Panel,self).__init__()
		self.children = []

	def add(self, mark):
		self.children().append(mark) # hmm... non lazy variant
		mark.set_parent(self)
		return mark

	def render(self, out):
		super(Panel,self).render(out)
		for child in self.children():
			child.render(out)

# A Panel which should be used as the toplevel panel in the graphic
class Graphic(Panel):
	defaults         = Prototype(Panel.defaults)
	defaults.options = "[baseline=(current bounding box.south)]"

	def __init__(self):
		super(Graphic,self).__init__()

	def render(self, out):
		opts = self.options
		out.write("\\begin{tikzpicture}%s%%\n" % self.options())
		super(Graphic,self).render(out)
		out.write("\\end{tikzpicture}\n")

class Line(Mark):
	defaults        = Prototype(Mark.defaults)
	defaults.xshift = 1
	defaults.yshift = 0
	defaults.style  = "draw"

	def __init__(self):
		super(Mark,self).__init__()
		self.anchors = AnchorGetter(self)

	def get_anchor(self, name):
		if name == "begin":
			return self.position
		elif name == "end":
			return lambda: self.position().move(self.xshift(), self.yshift())
		return None

	def render(self, out):
		style = self.style()
		if style == None:
			return

		out.write("\\path[%s] " % style)
		self.anchors().begin().write(out)
		out.write(" -- ")
		self.anchors().end().write(out)
		out.write(";\n")

class Wedge(Mark):
	defaults = Prototype(Mark.defaults)
	defaults.angle  = 0
	defaults.len    = 90.0  # wedge is between start_angle and start_angle+len
	defaults.radius = 0.5
	defaults.size   = 1.0
	defaults.style  = "fill=black"

	def __init__(self):
		super(Mark,self).__init__()
		self.anchors = AnchorGetter(self)

	def get_anchor(self, name):
		if name == "center":
			return self.position
		elif name == "inner_start":
			return lambda: PolarCoordinate(self.position(), self.angle(), self.radius())

		elif name == "inner_end":
			return lambda: PolarCoordinate(self.position(), self.angle()+self.len(), self.radius())
		elif name == "outer_start":
			return lambda: PolarCoordinate(self.position(), self.angle(), self.radius()+self.size())
		elif name == "outer_end":
			return lambda: PolarCoordinate(self.position(), self.angle()+self.len(), self.radius()+self.size())
		elif name == "inner":
			return lambda: PolarCoordinate(self.position(), self.angle()+self.len()/2., self.radius())
		elif name == "outer":
			return lambda: PolarCoordinate(self.position(), self.angle()+self.len()/2., self.radius()+self.size())
		return None

	def render(self, out):
		style = self.style()
		if style == None:
			return

		out.write("\\path[%s] " % style)
		self.anchors().inner_end().write(out)
		out.write(" arc(%s:%s:%s) " % (self.angle()+self.len(), self.angle(), self.radius()))
		out.write(" -- ")
		self.anchors().outer_start().write(out)
		out.write(" arc(%s:%s:%s) " % (self.angle(), self.angle()+self.len(), self.radius()+self.size()))
		out.write(" -- cycle;\n")

# A color value
class Color(Mark):
	defaults            = Prototype(Mark.defaults)
	defaults.colormodel = "hsb"
	defaults.color      = (.0, .0, .0)

	id = 0

	def __init__(self):
		super(Mark,self).__init__()

	def render(self, out):
		name  = "color%d" % Color.id
		model = self.colormodel()
		color = self.color()
		Color.id += 1
		
		out.write("\\definecolor{%s}{%s}{%.3f,%.3f,%.3f}\n" % (name, model, color[0], color[1], color[2]))
		self.name = name

# A special object that can be inserted into Panels. It collects a list of
# children and a list of data. It then iterates over all data elements
# instantiating a new "copy" (really a small class with prototype) with
# datum and index set to the data/element number of the currently processed
# datum.
#
# TODO: children/data is strictly evaluate should we make this lazy too?
class Iterate(Mark):
	def __init__(self, data = []):
		super(Iterate,self).__init__()
		self.data     = data
		self.children = []
		self.datum    = lambda: self.datum()
		self.index    = lambda: self.index()

	def add(self, mark):
		self.children().append(mark)   # hmm this isn't lazy...
		mark.set_parent(self)
		return mark

	def render(self, out):
		data     = self.data()
		children = self.children()

		index = 0
		for datum in data:
			self.index = index
			self.datum = datum
			for child in children:
				child.render(out)
			index += 1
		# if someone reference datum/index after this point its a bug
		del self.datum
		del self.index
