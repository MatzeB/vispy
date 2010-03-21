import types
import new

# Support for prototype based programming. This mainly means that if
# something isn't found in the current class then it is looked up in the
# object pointed to by prototype
class Prototype(object):
	def __init__(self, inherit=None):
		self.prototype = inherit

	def __getattr__(self, name):
		prototype = Prototype.__getattribute__(self, "prototype")
		if prototype == None:
			raise AttributeError("'%s' has no attribute '%s'" % (self, name))
		result = getattr(prototype, name)
		# Rebind methods to self if they are bound to prototype
		if (isinstance(result, types.MethodType) and
			result.im_self == prototype):
			result = new.instancemethod(result.im_func, self, result.im_class)
		return result

	def extend(self, prototype):
		self.prototype = prototype
