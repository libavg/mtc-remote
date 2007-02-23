# ===========================================================================
# File:		OSC.py
# Author:	Stefan Kersten <steve@k-hornz.de>
# Contents:	PyOSC client module
# ===========================================================================
# $Id: OSC.py,v 1.2 2000/11/28 20:09:59 steve Exp steve $
# ===========================================================================
#
# Copyright (C) 2000 Stefan Kersten
#
# This module is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#
# ===========================================================================

"""Python classes for OpenSoundControl library client functionality.

Inspired by Markus Gaelli's classes for Squeak.

The OSC homepage is at

	http://cnmat.cnmat.berkeley.edu/OpenSoundControl/

This module provides support for OSC client functionality. The classes
Message, Bundle and TimeTag can be used to construct proper OSC
messages; the resulting binary string can then be sent over a network
with the standard `socket()' calls.

Note that the OSC library currently relies on UDP, so you will
most likely use the `SOCK_DGRAM' protocol in your application.

Classes:

Message     		-- Single OSC message with arguments
Bundle			-- Groups of OSC messages with timing information
TimeTag    		-- Real valued time type for OSC bundles

Functions:

binary_value		-- Construct a BinaryValue from a Python type
tt			-- Construct a new TimeTag from an existing one or
			   a numeric value

Exceptions:

TypeError

"""

__revision__ = "$Revision: 1.2 $"

import math
import socket
import cStringIO
import struct
import types


class BinaryValue:
    """Abstract value holder.

    BinaryValue's subclasses know how to convert their value
    into a binary representation suitable for usage with OSC.
    """
    def __init__(self, value):
        self._value = value

    def get_value(self):
        """Return the value the receiver is holding."""
        return self._value
    
    def get_binary_value(self):
        """Return the binary representation of the receiver's value."""
        pass

    def __repr__(self):
        return '<' + \
               str(self.__class__.__name__) + \
               ' instance, value=' + \
               str(self.get_value()) + \
               '>'
    
class BinaryInteger(BinaryValue):
    """Holds an integer value (32 bit).

    BinaryInteger(value) -> BinaryInteger

    value	-- integer
    """
    def get_binary_value(self):
        return struct.pack('l', long(self._value))

class BinaryFloat(BinaryValue):
    """Holds a floating point value (32 bit).

    BinaryFloat(value) -> BinaryFloat

    value	-- float
    """
    def get_binary_value(self):
        return struct.pack('f', self._value)

class BinaryString(BinaryValue):
    """Holds a string value.

    BinaryString(value) -> BinaryString

    value	-- string
    
    The strings binary representation is padded with NULL chars
    to make its length a multiple of 4.
    """
    def get_binary_value(self):
        value = self._value
        size = len(value)
        return struct.pack('%ds%dx' % (size, 4 - (size % 4)), value)

def binary_value(value):
    """Return an appropriate BinaryValue according to value's type.

    Private.

    Exceptions:
    	TypeError	-- the type of value cannot be handled
    """
    t = type(value)
    # Integer
    if t == types.IntType or t == types.LongType:
        return BinaryInteger(value)
    # Float
    if t == types.FloatType:
        return BinaryFloat(value)
    # String
    if t == types.StringType:
        return BinaryString(value)
    raise TypeError, 'invalid OSC-type ' + str(t)


class TimeTag(BinaryValue):
    """Real valued data type for OSC timing information.

    TimeTag(value) -> TimeTag

    value	-- an instance of TimeTag or a numeric value
    
    The current time-value can be retrieved with two methods:

    get_value		-- Returns the floating point value of the receiver
    get_values		-- Returns a tuple of integers (seconds, fraction),
    			   representing the integer part in seconds and the
                           fractional part in nanoseconds respectively; this
                           is the format actually used in OSC.
    """
    def __init__(self, value):
        if isinstance(value, TimeTag):
            value = value._value
        else:
            try:
                value = float(abs(value))
            except:
                raise TypeError, 'TimeTag can only be created from another TimeTag or a number'
        BinaryValue.__init__(self, value)
    
    def get_values(self):
        """Return the tuple (seconds, fraction).

        See class comment.
        """
        fract, int = math.modf(self._value)
        return (long(int), long(fract * 1e9))

    def add(self, number):
        """Add number to the receiver's time value and return a new TimeTag."""
        return self.__class__(self._value + number)

    def sub(self, number):
        """Subtract number from the receiver's time value and return a new TimeTag.

        Values less than zero are truncated to zero.
        """
        delta = self._value - number
        if delta < 0:
            return self.__class__(0)
        else:
            return self.__class__(delta)

    def delta(self, timetag):
        """Return the difference between the receiver and timetag as a float."""
        return self._value - timetag._value

    def __cmp__(self, timetag):
        """Comparison is defined between TimeTag(s) and numbers."""
        value = self._value
        ovalue = timetag._value
        if value < ovalue:
            return -1
        if value > ovalue:
            return 1
        return 0

    def __coerce__(self, other):
        return (self, self.__class__(other))

    def get_binary_value(self):
        seconds, fraction = self.get_values()
        return struct.pack('ll', seconds, fraction)

def tt(object):
    """Constructor function for convenience.

    Returns a new TimeTag.
    """
    return TimeTag(object)


class Packet:
    """Abstract base class for all OSC-related containers.

    Has methods for retrieving the proper binary representation
    and its size.
    """
    def __init__(self, *packets):
        stream = cStringIO.StringIO()
        self.write_packets(packets, stream)
        self._data = stream.getvalue()

    def get_packet(self):
        """Return the binary representation of the receiver's contents.

        This data is in the proper OSC format and can be sent over a
        socket.
        """
        return self._data

    def get_size(self):
        """Return the size of the receiver's binary data."""
        return len(self._data)
    
    def write_packets(self, packets, stream):
        """Write packets on stream.

        Private.

        Override in subclasses for specific behavior.
        """
        pass

    def __repr__(self):
        return '<' + \
               str(self.__class__.__name__) + \
               ' instance, size=' + \
               str(self.get_size()) + \
               '>'

    # For testing purposes only:    
    def sendto(self, address, port):
        """Send the receiver's data over a UDP socket.

        Use for testing only; use functions from the socket
        module instead.
        """
        s = socket.socket(socket.SOCK_DGRAM, socket.AF_INET)
        packet = self.get_packet()
        s.sendto(packet, (address, port))

    def sendto_me(self, port):
        """Send the receiver's data over a UDP socket to the local machine.

        See the comment for sendto().
        """
        self.sendto('localhost', port)


class Message(Packet):
    """Single OSC message with arguments.

    Message(*values) -> Message
    
    values 	-- OSC basic types (integer, float, string)
    		   values[0] should be a address string (unchecked)
    """
    def write_packets(self, packets, stream):
        for value in packets:
            bin_value = binary_value(value)
            stream.write(bin_value.get_binary_value())


class Bundle(Packet):
    """OSC container type with timing information.

    Bundle(*packets) -> Bundle

    packets	-- subclasses of Packet
		   packets[0] must be a TimeTag instance

    """
    def write_packets(self, packets, stream):
        # Write '#bundle' preamble
        bundle = BinaryString('#bundle')
        stream.write(bundle.get_binary_value())
        # Write timetag
        try:
            stream.write(packets[0].get_binary_value())
        except:
            raise TypeError, 'packets[0] must be a TimeTag'
        # Write all packets, prefixed with a byte count
        for packet in packets[1:]:
            data = packet.get_packet()
            size = BinaryInteger(len(data))
            stream.write(size.get_binary_value())
            stream.write(data)


def _example(host='localhost', port=2222):
    import socket

    print "\n--- PyOSC example ---\n"

    m1 = Message('/spam/and/eggs', 2278, 12.0, 'Who has got my MoJo, eh?')
    m2 = Message('/scoo/bee/doo', 1.0, 'Minime has it.', 2.345, 45.76, 2.312, 999.00238)
    m3 = Message('/oops/i/did-it', 'again', 12341, 'Ouch!')

    i = 1
    for m in [m1, m2, m3]:
        data = m.get_packet()
        size = len(data)
        print 'Message %d (size %d):' % (i, size)
        print data
        print

    t = tt(0)
    b = Bundle(t, m1,
               Bundle(t.add(3.56), m1, m2),
               Bundle(t.add(3.67), m3))
    data = b.get_packet()
    size = len(data)
    print 'Bundle (size %d):' % (size,)
    print data
    print

    print "\nCreating socket ..."
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print "Sending packets:"

    for p in [m1, m2, m3, b]:
        s.sendto(p.get_packet(), (host, port))

    print "Exiting ..."

if __name__ == "__main__":
    _example()


