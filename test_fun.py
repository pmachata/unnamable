import fun

def test1 ():
    class B:
        def __init__ (self, name):
            self.name = name
        def __str__ (self):
            return self.name

    classify = fun.Function (object, name="classify")

    @classify.match (fun.catch (lambda a: a % 2 == 0))
    def classify_even (a):
        return "even"
    @classify.match (fun.catch (lambda a: a % 3 == 0))
    def classify_div3 (a, **kwargs):
        return "divisible by 3"


    @classify.match (fun.val == 0, priority=1)
    def classify_zero (a):
        return "zero"

    @classify.match (lambda a: a > 5, priority=1)
    def classify_big (a):
        return "big"

    @classify.match (fun.any)
    def classify_unclassified (a):
        return "unclassified"

    @classify.match (fun.matchclass (B), priority=2)
    def classify_string (a):
        return "B"

    @classify.match (fun.matchattr (name = "xxx"), priority=3)
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

    test = fun.Function (object, name="test")

    @test.match (fun.bind (X = fun.if_else (fun.matchattr (name = "abc"),
                                            lambda arg: arg.value)))
    def do (arg):
        return "1:" + X

    @test.match (fun.bind (X = fun.if_else (fun.matchattr (name = "def"),
                                            lambda arg: arg.value)))
    def do (arg):
        return "2:" + X

    @test.match (fun.any)
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

    x = fun.Function (object, object)

    @x.match (fun.any, fun.any)
    def do (i, j):
        return "%s, %s" % (i, j)

    @x.match (fun.matchclass (B), fun.any)
    def do (i, j):
        return "some B, %s" % j

    @x.match (fun.any, fun.val == 5)
    def do (i, j):
        return "%s, value 5" % i

    @x.match (fun.bind (X = fun.catch (lambda arg: arg.a ())), fun.any)
    def do (i, j):
        return "a=%s, %s" % (X, j)

    assert (x (1, 2) == "1, 2")
    assert (x (A (1), 2) == "a=1, 2")
    assert (x (B (), 2) == "some B, 2")
    assert (x (1, 5) == "1, value 5")

def test4 ():
    x = fun.Function (object)

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

def test5 ():
    x = fun.Function (object)

    @x.match (fun.any)
    def do (i):
        return 1

    @x.match (fun.val != 3)
    def do (i):
        return 2

    assert x (0) == 2
    assert x (1) == 2
    assert x (2) == 2
    assert x (3) == 1
    assert x (4) == 2
    assert x (5) == 2
    assert x (6) == 2

def test6 ():
    x = fun.Function (object)

    @x.match (fun.any)
    def do (i):
        return 1

    @x.match (fun.take_first (fun.val == 2))
    def do (i):
        return 2

    assert x (0) == 1
    assert x (0) == 1
    assert x (1) == 1
    assert x (1) == 1
    assert x (2) == 2
    assert x (2) == 1
    assert x (3) == 1
    assert x (3) == 1

def test7 ():
    x = fun.Function (object)

    @x.match (fun.any)
    def do (i):
        return 1

    @x.match (fun.or_ (fun.val == 1, fun.val == 2))
    def do (i):
        return 2

    assert x (0) == 1
    assert x (0) == 1
    assert x (1) == 2
    assert x (1) == 2
    assert x (2) == 2
    assert x (2) == 2
    assert x (3) == 1
    assert x (3) == 1

def test8 ():
    x = fun.Function (object)

    @x.match (fun.any)
    def do (i):
        return 1

    @x.match (fun.and_ (fun.val != 1, fun.val != 2))
    def do (i):
        return 2

    assert x (0) == 2
    assert x (0) == 2
    assert x (1) == 1
    assert x (1) == 1
    assert x (2) == 1
    assert x (2) == 1
    assert x (3) == 2
    assert x (3) == 2

def test9 ():
    x = fun.Function ()
    q = []

    @x.match ()
    def do ():
        q.append (1)

    @x.match (priority=1)
    def do ():
        next ()
        q.append (2)

    @x.match (priority=2)
    def do ():
        next ()
        q.append (3)

    x ()
    assert q == [1, 2, 3]

def test10 ():
    class X:
        def __init__ (self):
            self.x = fun.Function (int)

            @self.x.match (int)
            def do (i):
                return i + 1

    assert X ().x (1) == 2

test1 ()
test2 ()
test3 ()
test4 ()
test5 ()
test6 ()
test7 ()
test8 ()
test9 ()
test10 ()
