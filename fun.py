def any (arg):
    return True

class Function (object):
    def __init__ (self, *args, **kwargs):
        self.m_prototype = tuple (args)
        self.m_variants = []
        self.m_name = kwargs.get ("name", str (self))
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

    def bind (self, predicates, body, options):
        assert isinstance (predicates, tuple)
        assert len (predicates) == len (self.m_prototype)

        for pred in predicates:
            #assert isinstance(x, collections.Callable) -- PY 2.6
            import operator
            assert operator.isCallable (pred)

        priority = options.get ("priority",
                                -len ([pred for pred in predicates
                                       if pred == any]))
        trace = options.get ("trace", self.m_trace)

        class struct:
            def __init__ (self, **kwargs):
                self.__dict__.update (kwargs)
        self.m_variants.append ((predicates, body,
                                 struct (priority=priority,
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
                ret = pred (arg)
                bind = {}
                if isinstance (ret, tuple):
                    ret, bind = ret

                assert ret == True or ret == False, \
                    "Top level predicates function must return True of False"

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
                candidates = [(predicate, body, options)
                              for (predicate, body, options) in self.m_variants]
            message = "candidates are:\n" \
                + "\n".join ("  " + self.fmt_info (body)
                             for (predicate, body, options) in candidates)
            raise TypeError ("%s overload for call to %s (%s)\n"
                             % ("Ambiguous" if len (candidates) > 1 else "Found no",
                                self.m_name, ", ".join (str (arg)
                                                        for arg in args))
                             + message)

        # Call
        _, body, options = candidates[0]
        if options.trace:
            print "%s: %s" % (self.m_name, self.fmt_info (body))

        class Bound:
            def __init__ (self, bindings):
                self.m_bindings = bindings
            def __getattr__ (self, key):
                return self.m_bindings[key]

        # This is devious.
        backup = dict (body.func_globals)
        for key, val in bindings.iteritems ():
            body.func_globals[key] = val
        retval = body (*args)
        for key in list (body.func_globals):
            del body.func_globals[key]
        for key, val in backup.iteritems ():
            body.func_globals[key] = val
        return retval

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

def catch (pred):
    def match (arg):
        try:
            return pred (arg)
        except:
            return False
    return match

def hasattr (name):
    def match (arg):
        return name in arg.__dict__
    return catch (match)

def matchattr (**kwargs):
    key, = kwargs.keys ()
    value, = kwargs.values ()
    def match (arg):
        return arg.__dict__[key] == value
    return catch (match)

def matchvalue (value):
    def match (arg):
        return arg == value
    return match

def val (value):
    def match (arg):
        return value
    return match

def if_else (pred, if_match, if_mismatch = val (None)):
    def match (arg):
        if pred (arg):
            return if_match (arg)
        else:
            return if_mismatch (arg)
    return match

if __name__ == "__main__":
    classify = Function (object, name="classify")

    def test1 ():
        class B:
            def __init__ (self, name):
                self.name = name
            def __str__ (self):
                return self.name

        @classify.match (catch (lambda a: a % 2 == 0))
        def classify_even (a):
            return "even"
        @classify.match (catch (lambda a: a % 3 == 0))
        def classify_div3 (a, **kwargs):
            return "divisible by 3"


        @classify.match (matchvalue (0), priority=1)
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

    def test2 ():

        class C:
            def __init__ (self, name, value):
                self.name = name
                self.value = value

        test = Function (object, name="test")

        @test.match (bind (X = if_else (matchattr (name = "abc"),
                                        lambda arg: arg.value)))
        def do (arg):
            return "1:" + X

        @test.match (bind (X = if_else (matchattr (name = "def"),
                                        lambda arg: arg.value)))
        def do (arg):
            return "2:" + X

        @test.match (any)
        def do (arg):
            return "default"

        assert test (C ("test", "")) == "default"
        assert test (C ("abc", "yay!")) == "1:yay!"
        assert test (C ("def", "meh!")) == "2:meh!"

    def test3 ():
        class A:
            def __init__ (self, a):
                self.m_a = a
            def a (self):
                return self.m_a

        class B:
            pass

        x = Function (object, object)

        @x.match (any, any)
        def do (i, j):
            return "%s, %s" % (i, j)

        @x.match (matchclass (B), any)
        def do (i, j):
            return "some B, %s" % j

        @x.match (any, matchvalue (5))
        def do (i, j):
            return "%s, value 5" % i

        @x.match (bind (X = catch (lambda arg: arg.a ())), any)
        def do (i, j):
            return "a=%s, %s" % (X, j)

        assert (x (1, 2) == "1, 2")
        assert (x (A (1), 2) == "a=1, 2")
        assert (x (B (), 2) == "some B, 2")
        assert (x (1, 5) == "1, value 5")

    def test4 ():
        x = Function (object)

        # Faulty branch.  Calling x must assert.
        @x.match (lambda arg: arg)
        def do (a):
            pass

        try:
            x (True)
        except AssertionError:
            assert False, "x (True) failed"

        try:
            x (8)
            asserted = False
        except AssertionError:
            asserted = True

        assert asserted

    test1 ()
    test2 ()
    test3 ()
    test4 ()

