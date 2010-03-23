#!/usr/bin/env python
import sys
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

# Convert angle in vp format [0:1] clockwise from top to tikz angle [0:360] counterclockwise from east
def angle_to_tikz(angle):
	return 90. - angle*360
def angle_to_tikz_rotate(angle):
	return angle*-360

class PolarCoordinate(object):
	def __init__(self, middle, angle, radius):
		self.middle = middle
		self.angle  = angle
		self.radius = radius

	def move(self, x, y):
		return PolarCoordinate(self.middle.move(x, y), self.angle, self.radius)

	def write(self, out):
		assert self.middle.anchor == None  # not supported yet
		x     = self.middle.x
		y     = self.middle.y
		polar = "%.3f:%.3f" % (angle_to_tikz(self.angle), self.radius)
		if x == 0 and y == 0:
			str = "(%s)" % polar
		else:
			str = "([xshift=%.3f,yshift=%.3f]%s)" % (x, y, polar)
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
		placement = self.placement()
		if placement == "south west":
			base = self.position
		elif placement == "south east":
			base = lambda: self.position().move(-self.width(), 0)
		elif placement == "south":
			base = lambda: self.position().move(-self.width()/2., 0)
		elif placement == "north west":
			base = lambda: self.position().move(0, -self.height())
		elif placement == "north east":
			base = lambda: self.position().move(-self.width(), -self.height())
		elif placement == "north":
			base = lambda: self.position().move(-self.width()/2., -self.height())
		elif placement == "west":
			base = lambda: self.position().move(0, -self.height()/2.)
		elif placement == "east":
			base = lambda: self.position().move(-self.width(), -self.height()/2.)
		elif placement == "center":
			base = lambda: self.position().move(-self.width()/2., -self.height()/2.)
		else:
			assert False # invalid/unknown placement

		if name == "south_west":
			return base
		elif name == "south":
			return lambda: base().move(self.width() / 2., 0)
		elif name == "south_east":
			return lambda: base().move(self.width(), 0)
		elif name == "west":
			return lambda: base().move(0, self.height() / 2.)
		elif name == "center":
			return lambda: base().move(self.width() / 2., self.height() / 2.)
		elif name == "east":
			return lambda: base().move(self.width(), self.height() / 2.)
		elif name == "north_west":
			return lambda: base().move(0, self.height())
		elif name == "north":
			return lambda: base().move(self.width() / 2., self.height())
		elif name == "north_east":
			return lambda: base().move(self.width(), self.height())
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

# (private) base class for everything which ends up as a tikz node
class TikzNode(Mark):
	defaults           = Prototype(Mark.defaults)
	defaults.placement = "south"
	defaults.style     = ""
	defaults.rotate    = None

	id = 0

	def __init__(self):
		super(TikzNode,self).__init__()
		self.anchors = AnchorGetter(self)

	def get_anchor(self, name):
		if name in [ "north_west", "north", "north_east", "west", "center", "east", "south_west", "south", "south_east" ]:
			name = name.replace("_", " ")
			return (lambda : Position(0, 0, "%s.%s" % (self.__myname(), name)))

	def render_node_begin(self, out):
		style     = self.style()
		placement = self.placement()
		rotate    = self.rotate()
		if rotate != None:
			if style != "":
				style += ","
			style += "rotate=%s" % angle_to_tikz_rotate(rotate)

		if style != "":
			style += ","
		style += "anchor=%s" % placement

		self.__myname = "%s%d" % (self.name_base(), TikzNode.id)
		TikzNode.id += 1

		out.write("\\node[%s] (%s) at " % (style, self.__myname()))
		self.position().write(out)
		out.write(" { ")
		
	def render_node_end(self, out):
		out.write(" };\n")

class Label(TikzNode):
	defaults       = Prototype(TikzNode.defaults)
	defaults.label = ""

	name_base = "label"

	def __init__(self):
		super(Label,self).__init__()

	def render(self, out):
		self.render_node_begin(out)
		out.write(self.label())
		self.render_node_end(out)

class SubGraphics(TikzNode):
	defaults = Prototype(TikzNode.defaults)
	name_base = "subfig"

	def __init__(self):
		super(SubGraphics,self).__init__()
		self.children = []

	def add(self, mark):
		self.children().append(mark) # hmm... non lazy variant
		mark.set_parent(self)
		return mark

	def render(self, out):
		self.render_node_begin(out)
		out.write("\n \\begin{tikzpicture}\n")
		for child in self.children():
			child.render(out)
		out.write("\\end{tikzpicture}\n")
		self.render_node_end(out)

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
	defaults.len    = 0.25  # wedge is between start_angle and start_angle+len
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

		start  = angle_to_tikz(self.angle())
		end    = angle_to_tikz(self.angle()+self.len())
		radius = self.radius()
		out.write("\\path[%s] " % style)
		self.anchors().inner_end().write(out)
		out.write(" arc(%.3f:%.3f:%.3f)" % (end, start, radius))
		out.write(" -- ")
		self.anchors().outer_start().write(out)
		out.write(" arc(%.3f:%.3f:%.3f)" % (start, end, radius+self.size()))
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
class Iterate(Mark):
	def __init__(self, data = []):
		super(Iterate,self).__init__()
		self.data     = data
		self.children = []
		self.datum    = lambda: self.datum()
		self.index    = lambda: self.index()
		self.first    = {}
		self.next     = {}

	def add(self, mark):
		self.children().append(mark)   # hmm this isn't lazy...
		mark.set_parent(self)
		return mark

	def render(self, out):
		data     = self.data()
		children = self.children()

		for key,val in self.first().iteritems():
			setattr(self, key, val)

		index = 0
		for datum in data:
			self.index = index
			self.datum = datum
			for child in children:
				child.render(out)
			index += 1

			for key,val in self.next().iteritems():
				setattr(self, key, val())
		# if someone reference datum/index after this point its a bug
		del self.datum
		del self.index
