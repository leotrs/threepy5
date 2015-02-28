# -*- coding: utf-8 -*-
"""Data model for note taking application `threepy5`."""

from wx.lib.pubsub import pub
from collections import namedtuple
import utils


######################
# Default values
######################

# There are global constants because we need to set the default value
# for the LoudSetter* classes before creating the classes themselves.

# NO_ID = -1
# """Default ID for a `Card`."""

NO_RECT = [0,0,-1,-1]
"""Default rect for a `Card`."""

# Content defaults
DEFAULT_KIND      = "kind"
"""Default kind name for a `Content`."""

DEFAULT_RATING    = 0
"""Default rating for a `Content`."""

DEFAULT_SCALE = 1.0
"""Default scale for an `Image`."""

# Line defaults
DEFAULT_COLOUR    = (0,0,0,0)
"""Default colour for a `Line`"""

DEFAULT_THICKNESS = 1
"""Default thickness for a `Line`"""


        
###################################
# utils.Publisher classes
###################################

# LoudSetterID        = utils.makeLoudSetter("ID", NO_ID)
# LoudSetterID        = utils.LoudSetterID
LoudSetterRect      = utils.makeLoudSetter("Rect", NO_RECT)
LoudSetterHeader    = utils.makeLoudSetter("Header", "")
LoudSetterTitle     = utils.makeLoudSetter("Title", "")
LoudSetterKind      = utils.makeLoudSetter("Kind", DEFAULT_KIND)
LoudSetterRating    = utils.makeLoudSetter("Rating", DEFAULT_RATING)
LoudSetterContent   = utils.makeLoudSetter("Content", "")
LoudSetterCollapsed = utils.makeLoudSetter("Collapsed", False)
LoudSetterPath      = utils.makeLoudSetter("Path", "")
LoudSetterScale     = utils.makeLoudSetter("Scale", DEFAULT_SCALE)
LoudSetterLines     = utils.makeLoudSetter("Lines", [])
LoudSetterMembers   = utils.makeLoudSetter("Members", [])
LoudSetterName      = utils.makeLoudSetter("Name", "")
LoudSetterCards     = utils.makeLoudSetter("Cards", [])
LoudSetterGroups    = utils.makeLoudSetter("Groups", [])
LoudSetterDecks     = utils.makeLoudSetter("Decks", [])


def subscribe(attr, call, obj):
    """Call to tell `threpy5` to call `call` when `obj` changes its `attr`.

    * `attr: ` the name of the attribute to listen to (a string).
    * `call: ` a callable object to call when `attr` is updated.
    * `obj: ` the object whose attribute `attr` we want to track.
    """
    topic = ".".join([obj._make_topic_name(), "UPDATE_" + attr.upper()])
    pub.subscribe(call, topic)



######################
# Card classes
######################

class Card(utils.Publisher):
    """`Card` is a "virtual 3x5 index card". They are assumed to lie on a
    surface, in which relative position to other `Card`s is very important.

    As an abstract class, its inheritors specialize in handling text
    (`Content`), titles (`Header`), images (`Image`), etc.

    After creating a `Card`, do what's possible to never change its _id.
    Weird things happen when you change _id, though it could be possible
    if done carefully.
    """
    rect = LoudSetterRect()

    def __init__(self, rect=NO_RECT):
        """Constructor.

        * `rect: ` (x, y, w, h), accepts floats.
        """
        super(Card, self).__init__()
        self.rect = rect

        
    ### properties

    @property
    def Position(self):
        """The position of this `Card`.

        `returns: ` a (x, y) tuple of floats.
        """
        return namedtuple("Point", "x y")(self.rect[0], self.rect[1])

    @Position.setter
    def Position(self, pt):
        """Set the position of this `Card`."""
        self.rect[0], self.rect[1] = pt[0], pt[1]

    @property
    def Size(self):
        """The size of this `Card`.

        `returns: ` a (x, y) tuple of floats.
        """
        return namedtuple("Size", "w h")(self.rect[2], self.rect[3])

    @Size.setter
    def Size(self, sz):
        """Set the position of this `Card`."""
        self.rect[2], self.rect[3] = sz[0], sz[1]

        
    ### methods

    def MoveBy(self, dx, dy):
        """Move the card relateive to its current position.

        * `dx: ` amount to move in the horizontal direction.
        * `dy: ` amount to move in the vertical direction.
        """
        self.Position = (self.rect[0] + dx, self.rect[1] + dy)

    def Dump(self):
        """Return a dict holding all this `Card`'s data. When overriding,
        call this method and append all adittional data to the object returned.
        
        `returns: ` an object holding data. Generally, a `dict`.
        """
        return {"id": self.id, "rect": self.rect}

    def Load(self, data):
        """Read data from an object and load it into this `Card`.

        * `obj: ` must be a dict in the format returned by `Card.Dump`.
        """
        self.id = data["id"]
        self.rect = data["rect"]



class Content(Card):
    """A `Card` which holds text contents. Features: title, kind, rating, content.

    In its content text field, the user may input "tags". Any line of the form
        ^my-tag: foo bar baz$
    is considered to define the tag "my-tag". Tag names (before the colon) must
    be single words, and their content (after the colon) may be any string,
    until a newline.

    A tag can be anything, though they usually describe facts about concepts:

        Content Card "Protein"
        kind: concept
        rating: 2 stars
            Proteins are chains of amino-acids which...
            Number: there are x types of proteins.
            Kinds: transmembrane proteins, integral membrane proteins.

    This `Content` has two tags: "number" and "kinds".

    A `Content` can be "collapsed". This means that its content text is hidden
    and we only wish to display its title.
    """
    KIND_LBL_CONCEPT    = "Concept"
    KIND_LBL_RESEARCH   = "Research"
    KIND_LBL_ASSUMPTION = "Assumption"
    KIND_LBL_FACT       = "Fact"
    KIND_LBLS = [KIND_LBL_CONCEPT, KIND_LBL_RESEARCH, KIND_LBL_ASSUMPTION, KIND_LBL_FACT]
    
    RATING_MAX = 3
    DEFAULT_RECT_CONT = (0,0,250,150)

    title = LoudSetterTitle()
    kind = LoudSetterKind()
    rating = LoudSetterRating()
    content = LoudSetterContent()
    collapsed = LoudSetterCollapsed()

    def __init__(self, rect=DEFAULT_RECT_CONT, title="", kind=DEFAULT_KIND, rating=DEFAULT_RATING, content="", collapsed=False):
        """Constructor.

        * `rect: ` (x, y, w, h), accepts floats.
        * `kind: ` one of `Content.KIND_*`.
        * `content: ` the content text.
        * `rating: ` a measure of the importance of this `Content`. Must be an
        int from 0 to `RATING_MAX`, inclusive.
        * `collapsed: ` if `True`, we ignore the contents. In that case, this
        `Content` would funtion sort of like a `Header` with a kind and a rating.
        """
        super(Content, self).__init__(rect=rect)
        self.title = title
        self.kind = kind
        self.rating = rating
        self.content = content
        self.collapsed = collapsed

    def IncreaseRating(self, wrap=True):
        """Set the rating to be one more than its current value.
        
        * `wrap: ` if `True`, and we increase to more than the maximum rating, we set it to zero.
        if `False` and the new rating is more than `self.MAX`, don't do anything."""
        new = self.rating + 1
        if wrap and new > self.RATING_MAX:
            new = 0
        elif new > self.RATING_MAX:
            return
        
        self.rating = new



class Header(Card):
    """`Card` that holds a title or header."""
    header = LoudSetterHeader()

    def __init__(self, rect=NO_RECT, header=""):
        """Constructor.

        * `rect: ` (x, y, w, h), accepts floats.
        * `header: ` the title or header.
        """
        super(Header, self).__init__(rect=rect)
        self.header = header



class Image(Card):
    """A `Card` that holds a single image. Note that this class doesn't
    actually load the image from disk. If the application needs to display
    the image, it must load it by itself.
    """
    path = LoudSetterPath()
    scale = LoudSetterScale()

    def __init__(self, rect=NO_RECT, path="", scale=DEFAULT_SCALE):
        """Constructor.

        * `rect: ` (x, y, w, h), accepts floats.
        * `path: ` the path to the image on disk.
        * `scale: ` the scale at which we show the image. This is the float by which we need
        to resize the original image so that it fits in `self.rect`.
        """
        super(Image, self).__init__(rect=rect)
        self.path = path
        self.scale = scale



######################
# Annotation class
######################

# class Line(object):
#     """A `Line` represents a single stroke of the annotations or doodles the user draws in the
#     infinite surface that the `Card`s are drawn on. These are drawn on top of the `Card`s.
#     """

#     # colour = LoudSetterColour()
#     # thickness = LoudSetterThickness()
#     # pts = LoudSetterPts()

#     Add = utils.AddDesc("pts")
#     Remove = utils.RemoveDesc("pts")

#     def __init__(self, colour=DEFAULT_COLOUR, thickness=DEFAULT_THICKNESS, pts=[]):
#         """Constructor.

#         * `colour: ` a (r,g,b,alpha) tuple.
#         * `thickness: ` an int representing the thickness of this stroke.
#         * `pts: ` the points defining this polyline.
#         """
#         super(Line, self).__init__()
#         self.colour = colour
#         self.thickness = thickness
#         self.pts = pts


import recordtype
Line = recordtype.recordtype('Line', [('colour', (0,0,0,0)), ('thickness', 1), ("pts", [])])
"""A `Line` represents a single stroke of the annotations or doodles the user draws in the
infinite surface that the `Card`s are drawn on. These are drawn on top of the `Card`s.

It is a `recordtype` (a mutable named tuple), with fields aliases for "colour", "thickness",
and "pts".
"""



class Annotation(utils.Publisher):
    """`Annotation` is the set of all `Line`s over an `AnnotatedDeck` of `Card`s."""
    lines = LoudSetterLines()
    Add = utils.AddDesc("lines")
    Remove = utils.RemoveDesc("lines")

    def __init__(self, lines=[]):
        """Constructor.

        * `lines: ` a list of `Line`s.
        """
        super(Annotation, self).__init__()
        self.lines = lines



##########################
# Collections of Cards
##########################

class CardGroup(utils.Publisher):
    """A list of `Card`s. Grouped `Card`s have meaning together. A `Card` may
    belong to more than one group. If all the `Card`s in one group are also in
    another group, the smaller group is considered nested in the larger one.
    """
    members = LoudSetterMembers()
    Add = utils.AddDesc("members")
    Remove = utils.RemoveDesc("members")

    def __init__(self, members=[]):
        """Constructor.

        * `members: ` a list of identification numbers from `Card`s.
        """
        super(CardGroup, self).__init__()
        self.members = members



class Deck(utils.Publisher):
    """It's a collection of `Card`s that share a common topic. It can also hold
    many `CardGroup`s.
    """
    name = LoudSetterName()
    cards = LoudSetterCards()
    groups = LoudSetterGroups()

    AddCard = utils.AddDesc("cards")
    RemoveCard = utils.RemoveDesc("cards")
    AddGroup = utils.AddDesc("groups")
    RemoveGroup = utils.RemoveDesc("groups")

    def __init__(self, name="", cards=[], groups=[]):
        """Constructor.

        * `name: ` the name of this `Deck`.
        * `cards: ` a list of `Card`s.
        * `groups: ` a list of `CardGroup`s.
        """
        super(Deck, self).__init__()
        self.name = name
        self.cards = cards
        self.groups = groups



##################################
# Collections of mixed objects
##################################

class AnnotatedDeck(Deck):
    """A collection of `Card`s that can be annotated on."""

    def __init__(self, name="", cards=[], groups=[], lines=[]):
        """Constructor.

        * `name: ` the name of this `Deck`.
        * `cards: ` a list of `Card`s.
        * `groups: ` a list of `CardGroup`s.
        * `lines: ` a list of `Line`s.
        """
        super(AnnotatedDeck, self).__init__(name=name, cards=cards, groups=groups)
        self.annotation = Annotation(lines=lines)




class Box(utils.Publisher):
    """A `Box` holds various `Deck`s. It is the equivalent of a file at
    application level: every `Box` is stored in one file and every file
    loads one `Box`.
    """
    name = LoudSetterName()
    path = LoudSetterPath()
    decks = LoudSetterDecks()

    AddDeck = utils.AddDesc("decks")
    RemoveDeck = utils.RemoveDesc("decks")

    def __init__(self, name="", path="", decks=[]):
        """Constructor.

        * `name: ` the name of this `Box`.
        * `path: ` the path to the file on disk.
        * `decks: ` a list of `Deck`s (or `AnnotatedDeck`s).
        """
        super(Box, self).__init__()
        self.name = name
        self.path = path
        self.decks = decks
