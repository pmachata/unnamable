def any (arg):
    return True

class Function (object):
    def __init__ (self, *args, **kwargs):
        self.m_prototype = tuple (args)
        self.m_variants = []
        self.m_name = kwargs.get ("name", None)
        self.m_trace = kwargs.get ("trace", False)

    def match (self, *args, **kwargs):
        def decorator (function):
            self.bind (args, function, kwargs)
        return decorator

    def fmt_info (self, body):
        if type (body) != type (lambda:None):
            body = body.__call__.im_func
        code = body.func_code
        return "%s at %s:%s" % (code.co_name, code.co_filename,
                                code.co_firstlineno)

    def bind (self, key, body, options):
        assert isinstance (key, tuple)
        assert len (key) == len (self.m_prototype)

        colon = any
        priority = options.get ("priority", -len ([k for k in key if k == colon]))
        trace = options.get ("trace", self.m_trace)

        class struct:
            def __init__ (self, **kwargs):
                self.__dict__.update (kwargs)
        self.m_variants.append ((key, body, struct (priority=priority,
                                                    trace=trace)))

    def __call__ (self, *args):
        # Check sanity of arguments.
        for i, (a, p) in enumerate (zip (args, self.m_prototype)):
            assert isinstance (a, p),\
                "%s: argument #%s (`%s') should be of type `%s'" \
                % (self.m_name, i, a, p)

        # Find matching variants.
        def match_variant (variant):
            predicates, _, options = variant
            for arg, pred, proto in zip (args, predicates, self.m_prototype):
                if isinstance (arg, proto):
                    if arg == pred:
                        continue
                try:
                    ret = pred (arg)
                    if not ret:
                        return False
                except TypeError:
                        return False

                if isinstance (ret, tuple):
                    ret, bind = ret
                    if not ret:
                        return False
                    bindings.update (bind)
            return True

        candidates = []
        best_priority = None
        bindings = {}
        for variant in self.m_variants:
            priority = variant[2].priority
            if best_priority == None or priority >= best_priority:
                if match_variant (variant):
                    if best_priority == None or priority > best_priority:
                        candidates = []
                        best_priority = priority
                    candidates.append (variant)

        # Resolve.
        if len (candidates) != 1:
            if len (candidates) == 0:
                candidates = [(body, options)
                              for (predicate, body, options) in self.m_variants]
            message = "candidates are:\n" \
                + "\n".join ("  " + self.fmt_info (body)
                             for (body, options) in candidates)
            raise TypeError ("%s overload for call to %s (%s)\n"
                             % ("Ambiguous" if len (candidates) > 1 else "Found no",
                                self.m_name, ", ".join (str (arg)
                                                        for arg in args))
                             + message)

        # Call
        _, body, options = candidates[0]
        if options.trace:
            print "%s: %s" % (self.m_name, self.fmt_info (body))
        return body (*args, **bindings)

def bind (**kwargs):
    def match (arg):
        ret = {}
        for key, pred in kwargs.iteritems ():
            value = pred (arg)
            if not value:
                return False
            ret[key] = value
        return True, ret
    return match

def matchclass (c):
    return lambda arg: isinstance (arg, c)

def matchattr (**kwargs):
    key, = kwargs.keys ()
    value, = kwargs.values ()
    def match (arg):
        try:
            return arg.__dict__[key] == value
        except:
            return False
    return match

def if_else (pred, if_match, if_mismatch = lambda arg: None):
    def match (arg):
        if pred (arg):
            return if_match (arg)
        else:
            return if_mismatch (arg)
    return match

def val (value):
    def match (arg):
        return value
    return match

if __name__ == "__main__":
    classify = Function (object, name="classify")

    class B:
        def __init__ (self, name):
            self.name = name
        def __str__ (self):
            return self.name

    @classify.match (lambda a: a % 2 == 0)
    def classify_even (a):
        return "even"
    @classify.match (lambda a: a % 3 == 0)
    def classify_div3 (a, **kwargs):
        return "divisible by 3"


    @classify.match (0, priority=1)
    def classify_zero (a):
        return "zero"

    @classify.match (lambda a: a > 5, priority=1)
    def classify_big (a):
        return "big"

    @classify.match (any)
    def classify_unclassified (a):
        return "unclassified"

    @classify.match (matchclass (B), priority=2)
    def classify_string (a):
        return "B"

    @classify.match (matchattr (name = "xxx"), priority=3)
    def classify_xxx (a):
        return "B(xxx)"

    assert classify (0) == "zero"
    assert classify (1) == "unclassified"
    assert classify (2) == "even"
    assert classify (3) == "divisible by 3"
    assert classify (4) == "even"
    assert classify (5) == "unclassified"
    assert classify (6) == "big"
    assert classify (7) == "big"
    assert classify (8) == "big"
    assert classify (9) == "big"
    assert classify (B ("xx")) == "B"
    assert classify (B ("xxx")) == "B(xxx)"

    class C:
        def __init__ (self, name, value):
            self.name = name
            self.value = value

    test = Function (object, name="test")

    @test.match (bind (X = if_else (matchattr (name = "abc"),
                                    lambda arg: arg.value)))
    def do (arg, **kwargs):
        return "1:" + kwargs["X"]

    @test.match (bind (X = if_else (matchattr (name = "def"),
                                    lambda arg: arg.value)))
    def do (arg, **kwargs):
        return "2:" + kwargs["X"]

    @test.match (any)
    def do (arg):
        return "default"

    assert test (C ("test", "")) == "default"
    assert test (C ("abc", "yay!")) == "1:yay!"
    assert test (C ("def", "meh!")) == "2:meh!"
