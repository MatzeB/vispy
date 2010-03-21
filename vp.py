#!/usr/bin/env python
from prototype import Prototype

class TikzPosition(object):
	def __init__(self, anchor, xshift, yshift):
		self.anchor = anchor
		self.xshift = xshift
		self.yshift = yshift

	def move(self, xshift, yshift):
		return TikzPosition(self.anchor, self.xshift + xshift, self.yshift + yshift)
	
	def write(self, out):
		if self.anchor == None:
			out.write("(%.3f, %.3f)" % (self.xshift, self.yshift))
			return
		if self.xshift == 0 and self.yshift == 0:
			out.write("(%s)" % self.anchor)
			return
		out.write("([xshift=%.3f,yshift=%.3f]%s)" % (self.xshift, self.yshift, self.anchor))
		return

Origin = TikzPosition(None, 0, 0)

class Mark(Prototype):
	defaults          = Prototype()
	defaults.xshift   = 0
	defaults.yshift   = 0
	defaults.position = Origin

	def __init__(self, inherit = None):
		super(Mark,self).__init__(inherit)
		self.parent = None
		self.full_position = lambda : self.position().move(self.xshift(), self.yshift())

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
		return self.target.get_anchor(name)

class Bar(Mark):
	defaults           = Prototype(Mark.defaults)
	defaults.width     = 0.0
	defaults.height    = 0.0
	defaults.lineWidth = None
	defaults.drawStyle = None
	defaults.fillStyle = "fill=black"
	defaults.placement = "south west"

	def __init__(self, inherit = None):
		super(Bar,self).__init__(inherit)
		self.anchors = AnchorGetter(self)

	def get_anchor(self, name):
		assert self.placement() == "south west" # no support for other placements (yet)
		base = self.full_position

		if name == "south_west":
			return base
		elif name == "south":
			return lambda : base().move(self.width() / 2., 0)
		elif name == "south_east":
			return lambda : base().move(self.width(), 0)
		elif name == "center":
			return lambda : base().move(self.width() / 2., self.height() / 2.)
		elif name == "north_west":
			return lambda : base().move(0, self.height())
		elif name == "north":
			return lambda : base().move(self.width() / 2., self.height())
		elif name == "north_east":
			return lambda : base().move(self.width(), self.height())

	def __get_real_style(self):
		drawStyle = self.drawStyle()
		fillStyle = self.fillStyle()
		if drawStyle == None:
			return fillStyle
		if fillStyle == None:
			return drawStyle
		return drawStyle + ", " + fillStyle

	def render(self, out):
		style = self.__get_real_style()
		if style == None:
			return

		out.write("\\path[%s] " % style)
		self.anchors().south_west().write(out)
		out.write(" rectangle ")
		self.anchors().north_east().write(out)
		out.write(";\n")

class Label(Mark):
	defaults            = Prototype(Mark.defaults)
	defaults.labelstyle = None
	defaults.placement = "south"

	id = 0

	def __init__(self, inherit = None):
		super(Label,self).__init__(inherit)
		self.anchors = AnchorGetter(self)
		self.label   = lambda : self.datum()

	def get_anchor(self, name):
		myname = self.__myname
		if name in [ "north_west", "north", "north_east", "west", "center", "east", "south_west", "south", "south_east" ]:
			name = name.replace("_", " ")
			return (lambda : TikzPosition("%s.%s" % (self.__myname, name)))

	def render(self, out):
		style     = self.labelstyle()
		label     = self.label()
		placement = self.placement()

		position = self.full_position()
		if style != None:
			style = "[%s,anchor=%s]" % (style, placement)
		else:
			style = "[anchor=%s]" % placement
		self.__myname = "label%d" % Label.id
		Label.id += 1

		out.write("\\node%s (%s) at " % (style, self.__myname()))
		position.write(out)
		out.write(" { %s }" % label)
		out.write(";\n")

class Panel(Bar):
	defaults           = Prototype(Bar.defaults)
	defaults.canvas    = None
	defaults.overflow  = "visible"
	defaults.fillStyle = None
	defaults.drawStyle = "draw=black"

	def __init__(self, inherit = None):
		super(Panel,self).__init__(inherit)
		self.children = []

	def add(self, mark):
		self.children().append(mark)
		mark.set_parent(self)
		return mark

	def render(self, out):
		super(Panel,self).render(out)
		for child in self.children():
			child.render(out)

# A Panel which should be used as the toplevel panel in the graphic
class Graphic(Panel):
	defaults           = Prototype(Panel.defaults)
	defaults.options   = "[baseline=(current bounding box.south)]"
	defaults.left      = 0
	defaults.bottom    = 0
	defaults.fillStyle = None
	defaults.drawStyle = None

	def __init__(self, inherit = None):
		super(Graphic,self).__init__(inherit)

	def render(self, out):
		opts = self.options
		out.write("\\begin{tikzpicture}%s%%\n" % self.options())
		super(Graphic,self).render(out)
		out.write("\\end{tikzpicture}\n")

# A special object that can be inserted into Panels. It collects a list of
# children and a list of data. It then iterates over all data elements
# instantiating a new "copy" (really a small class with prototype) with
# datum and index set to the data/element number of the currently processed
# datum.
#
# TODO: children/data is strictly evaluate should we make this lazy too?
class Iterate(Prototype):
	def __init__(self):
		super(Iterate,self).__init__()
		self.children = []
		self.data     = []

	def add(self, mark):
		self.children.append(mark)
		mark.set_parent(self.parent)
		return mark

	def render(self, out):
		# Iterate over all entries in the data list createing lightwight
		# prototypes with it and rendering them
		index = 0
		for datum in self.data:
			for child in self.children:
				child.datum = datum
				child.index = index
				child.render(out)
			index += 1

		for child in self.children:
			del child.datum
			del child.index

	def set_parent(self, new_parent):
		self.parent = new_parent
