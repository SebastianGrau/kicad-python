#  Copyright 2014 Piers Titus van der Torren <pierstitus@gmail.com>
#  Copyright 2015 Miguel Angel Ajo <miguelangel@ajo.es>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
pcbnew = __import__('pcbnew')

from kicad.pcbnew import drawing
from kicad.pcbnew.module import Module
from kicad.pcbnew.track import Track
from kicad.pcbnew.via import Via
from kicad import units


class Board(object):
    def __init__(self, board=None):
        """Convenience wrapper for pcbnew Board"""
        if board is None:
            # if no board is given create a new board
            board = pcbnew.BOARD()
        self._board = board

    @property
    def native_obj(self):
        return self._board

    def add(self, obj):
        self._board.Add(obj.native_obj)
        return obj

    @property
    def modules(self):
        m = self._board.GetModules().begin()
        while m is not None:
            yield Module(m)
            m = m.Next()

    @staticmethod
    def from_editor(self):
        return Board(board=pcbnew.GetCurrentBoard())

    @staticmethod
    def load(self, filename):
        """Save a board file."""
        return Board(pcbnew.LoadBoard(filename))

    def save(self, filename=None):
        """Save the board to a file.

        filename should have .kicad_pcb extention.
        """
        if filename is None:
            filename = self._board.GetFileName()
        self._board.Save(filename)

    def create_module(self, ref, position=(0, 0)):
        """Create new module on the board"""
        return self.add(Module(ref, position, board=self))

    def copy_module(self, original, ref, position=(0, 0)):
        """Create a copy of an existing module on the board"""
        return self.add(Module.copy(original, board=self))

    @property
    def default_width(self, width=None):
        b = self._board
        return (
            float(b.GetDesignSettings().GetCurrentTrackWidth()) /
            units.DEFAULT_UNIT_IUS)

    def add_track_segment(self, start, end, layer='F.Cu', width=None):
        """Create a track segment."""

        track = Track(width or self.default_width,
                      start, end, layer, board=self)
        self._board.Add(track.native_obj)
        return track

    def get_layer(self, name):
        return self._board.GetLayerID(name)

    def add_track(self, coords, layer='F.Cu', width=None):
        """Create a track polyline.

        Create track segments from each coordinate to the next.
        """
        for n in range(len(coords) - 1):
            self.add_track_segment(coords[n], coords[n + 1],
                                   layer=layer, width=width)

    @property
    def default_via_size(self):
        return (float(self._board.GetDesignSettings().GetCurrentViaSize()) /
                units.DEFAULT_UNIT_IUS)

    @property
    def default_via_drill(self):
        via_drill = self._board.GetDesignSettings().GetCurrentViaDrill()
        if via_drill > 0:
            return (float(via_drill) / units.DEFAULT_UNIT_IUS)
        else:
            return 0.2

    def add_via(self, coord, layer_pair=('B.Cu', 'F.Cu'), size=None,
                drill=None):
        """Create a via on the board

        Args:
            coord: Position of the via
            layer_pair: Tuple of the connected layers (for example
                        ('B.Cu', 'F.Cu'))
            size: size of via in mm, or None for current selection
            drill: size of drill in mm, or None for current selection
        """
        return self.add(
            Via(coord, layer_pair, size or self.default_via_size,
                drill or self.default_via_drill, board=self))

    def add_line(self, start, end, layer='F.SilkS', width=0.15):
        """Create a graphic line on the board"""
        return self.add(
            drawing.Segment(start, end, layer, width, board=self))

    def add_polyline(self, coords, layer='F.SilkS', width=0.15):
        """Create a graphic polyline on the board"""
        for n in range(len(coords) - 1):
            self.add_line(coords[n], coords[n + 1], layer=layer, width=width)

    def add_circle(self, center, radius, layer='F.SilkS', width=0.15):
        """Create a graphic circle on the board"""
        return self.add(
            drawing.Circle(center, radius, layer, width, board=self))

    def add_arc(self, center, radius, start_angle, stop_angle,
                layer='F.SilkS', width=0.15):
        """Create a graphic arc on the board"""
        return self.add(
            drawing.Arc(center, radius, start_angle, stop_angle,
                        layer, width, board=self))
        #start_coord = radius * cmath.exp(math.radians(start_angle-90)*1j)
        #start_coord = Point._from_tuple((start_coord.real, start_coord.imag))
        #
        #angle = stop_angle - start_angle
        #a = pcbnew.DRAWSEGMENT(self._board)
        #a.SetShape(pcbnew.S_ARC)
        #a.SetCenter(Point._from_tuple(center))
        #a.SetArcStart(start_coord)
        #a.SetAngle(angle*10)
        #a.SetLayer(_get_layer(layer))
        #a.SetWidth(width * DEFAULT_UNIT_IUS)
        #a.SetLocalCoord()
        #self._board.Add(a)
        #return a