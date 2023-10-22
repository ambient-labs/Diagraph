
from .ordered_set import OrderedSet


def describe_ordered_set():
    def test_it_instantiates():
        OrderedSet({1, 2, 3})

    def test_it_can_add_and_get_as_ordered():
        o = OrderedSet()
        o.add(1)
        o.add(2)
        o.add(3)

        assert list(o) == [1, 2, 3]

    def test_it_does_not_add_duplicates():
        o = OrderedSet()
        o.add(1)
        o.add(1)
        o.add(1)

        assert list(o) == [1]

    def test_it_can_pop():
        o = OrderedSet()
        o.add(1)
        o.add(2)
        o.add(3)

        assert o.pop() == 3
        assert o.pop() == 2
        assert o.pop() == 1

    def test_it_can_iterate():
        o = OrderedSet()
        o.add(1)
        o.add(2)
        o.add(3)

        lst = [i for i in o]

        assert lst == [1, 2, 3]
