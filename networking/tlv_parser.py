import struct


class TLVParser:
    def __init__(self, tag_definitions):
        self.tag_definitions = tag_definitions

    def read_tlv(self, data, offset, get_tag=False):
        """
        Reads a single TLV element from the data stream.

        Args:
            data: The byte stream containing the TLV data.
            offset: The current offset within the data stream.

        Returns:
            A tuple containing the parsed value and the updated offset.

        Raises:
            ValueError: If the data format is invalid or an unknown tag is encountered.
            :param get_tag:
        """
        # Read tag size from configuration
        tag_size = self.tag_definitions.tag_size

        if len(data) < offset + tag_size:
            raise ValueError("Incomplete data: Tag missing")

        tag = int.from_bytes(data[offset:offset + tag_size], byteorder='big')
        offset += tag_size

        # Read length size from configuration
        length_size = self.tag_definitions.length_size

        if len(data) < offset + length_size:
            raise ValueError("Incomplete data: Length missing")

        length = int.from_bytes(data[offset:offset + length_size], byteorder='big')
        offset += length_size
        if len(data) < offset + length:
            raise ValueError(f"Incomplete data: Value length {length} exceeds remaining data {len(data)}")

        value = data[offset:offset + length]
        offset += length

        # Use dictionary for tag handling
        unpack_func = self.tag_definitions.get(tag)
        if unpack_func:
            value = unpack_func["unpack_func"](value)
        else:
            raise ValueError(f"Unknown tag: {tag}")

        if get_tag:
            return tag, value, offset

        return value, offset

    def parse_tlv(self, data, offset):
        """
        Parses a complete TLV stream.

        Args:
            data: The byte stream containing the TLV data.
            offset: The current offset within the data stream.

        Returns:
            A list of parsed TLV elements.
        """
        fields = []
        while offset < len(data):
            field, offset = self.read_tlv(data, offset)
            fields.append(field)
        return fields

    def encode_tlv(self, tag, value):
        encoded_tlv = bytearray()

        encoded_tlv.extend(struct.pack("!H", tag))

        # Use dictionary for tag handling
        pack_func = self.tag_definitions.get(tag)["pack_func"]
        if pack_func:
            encoded_value = pack_func(value)
        else:
            return b''

        encoded_tlv.extend(struct.pack("!H", len(encoded_value)))
        encoded_tlv.extend(encoded_value)

        return encoded_tlv

    def encode_tlv_packet(self, packet_id, fields):
        """
        Encodes a TLV packet.

        Args:
            packet_id: The ID of the packet.
            fields: A list of tuples containing tag and value.

        Returns:
            The encoded TLV packet as a byte array.
        """
        packet = bytearray()
        packet.extend(struct.pack("!H", packet_id))
        for tag, value in fields:
            packet.extend(self.encode_tlv(tag, value))

        return struct.pack("!H", len(packet) + 2) + packet


class TLVDefinitions:
    def __init__(self, tag_size=2, length_size=2, tag_mappings=None):
        if tag_mappings is None:
            tag_mappings = dict()
        self.tag_size = tag_size
        self.length_size = length_size
        self.tag_mappings = tag_mappings

    def get(self, key, default=None):
        return self.tag_mappings.get(key, default)
