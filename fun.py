class Function (object):
    def __init__ (self, *args, **kwargs):
        self.m_prototype = tuple (args)
        self.m_variants = []
        self.m_name = kwargs.get ("name", str (self))
        self.m_trace = kwargs.get ("trace", False)
        self.m_returns = kwargs.get ("returns", object)

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
                "%s: argument #%s (`%s') has to be of type `%s'" \
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
                    "Top level predicate functions must return True of False"

                if not ret:
                    return False
                bindings.update (bind)

            return True

        best_priority = None
        bindings = {}

        precedence = {}
        for variant in list (variant for variant in self.m_variants
                             if match_variant (variant)):
            priority = variant[2].priority
            if priority not in precedence:
                precedence[priority] = []
            precedence[priority].append (variant)

        def fmt_variants (variants):
            return "candidates are:\n" \
                + "\n".join ("  " + self.fmt_info (body)
                             for (predicate, body, options) in variants)

        if len (precedence) == 0:
            candidates = [(predicate, body, options)
                          for (predicate, body, options) in self.m_variants]
            raise TypeError ("Found no matching overload for call to %s (%s)\n"
                             % (self.m_name, ", ".join (str (arg)
                                                        for arg in args))
                             + fmt_variants (candidates))

        precedence_list = sorted (precedence.items (),
                                  key = lambda arg: arg[0])

        class Next:
            def __init__ (self, fun):
                self.__cursor = 0
                self.__fun = fun

            def __call__ (self):
                self.__cursor -= 1
                priority, variants = precedence_list[self.__cursor]
                if len (variants) != 1:
                    raise TypeError \
                        ((("Ambiguous overload for call to %s "
                           + "(%s) with priority %d\n")
                          % (self.__fun.m_name,
                             ", ".join (str (arg) for arg in args),
                             priority))
                         + fmt_variants (variants))

                # Call
                _, body, options = variants[0]
                if options.trace:
                    print "%s: %s" % (self.__fun.m_name,
                                      self.__fun.fmt_info (body))

                # This is devious.
                backup = dict (body.func_globals)
                for key, val in bindings.iteritems ():
                    body.func_globals[key] = val
                retval = body (*args)
                for key in list (body.func_globals):
                    del body.func_globals[key]
                for key, val in backup.iteritems ():
                    body.func_globals[key] = val

                if options.trace:
                    print "%s returning" % self.__fun.m_name, retval

                assert isinstance (retval, self.__fun.m_returns),\
                    "%s: return value (`%s') has to be of type `%s'" \
                    % (self.__fun.m_name, retval, self.__fun.m_returns)

                return retval

        assert "next" not in bindings
        next = Next (self)
        bindings["next"] = next

        return next ()

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
    def match (arg):
        return isinstance (arg, c)
    return match

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

class Val:
    def __call__ (self, value):
        def match (arg):
            return value
        return match

    def __eq__ (self, other):
        return lambda arg: arg == other

    def __ne__ (self, other):
        return lambda arg: arg != other

val = Val ()
any = val (True)

def if_else (pred, if_match, if_mismatch = val (None)):
    def match (arg):
        if pred (arg):
            return if_match (arg)
        else:
            return if_mismatch (arg)
    return match

def not_ (pred):
    return if_else (pred, val (False), val (True))

def or_ (pred1, *preds):
    return if_else (pred1, val (True),
                    or_ (*preds) if len (preds) > 0 else val (False))

def and_ (pred1, *preds):
    return if_else (pred1,
                    and_ (*preds) if len (preds) > 0 else val (True),
                    val (False))

class take_first:
    def __init__ (self, such_that = any):
        self.taken = False
        self.such_that = such_that
    def __call__ (self, arg):
        if self.taken:
            return False
        if self.such_that (arg):
            self.taken = True
            return True
        else:
            return False
