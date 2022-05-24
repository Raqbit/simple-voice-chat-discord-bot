import uuid
from dataclasses import dataclass
from typing import NamedTuple

from packets.voice.packet import DecodableVoicePacket, EncodableVoicePacket
from util import Buffer


@dataclass
class MicPacket(EncodableVoicePacket):
    ID = 0x01

    data: bytes
    whispering: bool
    sequence: int

    def to_buf(self) -> bytes:
        return Buffer.pack_varint(len(self.data)) + self.data + \
               Buffer.pack("l?", self.sequence, self.whispering)


@dataclass
class SoundPacket:
    sender: uuid.UUID
    data: bytes
    sequence: int


@dataclass
class PlayerSoundPacket(SoundPacket, DecodableVoicePacket):
    ID = 0x02

    whispering: bool

    @classmethod
    def from_buf(cls, buf: Buffer) -> 'PlayerSoundPacket':
        sender = buf.unpack_uuid()
        data_len = buf.unpack_varint()
        data = buf.read(data_len)
        (sequence, whispering) = buf.unpack("l?")

        return cls(
            sender=sender,
            data=data,
            sequence=sequence,
            whispering=whispering
        )


@dataclass
class GroupSoundPacket(SoundPacket, DecodableVoicePacket):
    ID = 0x03

    @classmethod
    def from_buf(cls, buf: Buffer) -> 'GroupSoundPacket':
        sender = buf.unpack_uuid()
        data_len = buf.unpack_varint()
        data = buf.read(data_len)
        sequence = buf.unpack("l")

        return cls(
            sender=sender,
            data=data,
            sequence=sequence,
        )


class Location(NamedTuple):
    x: float
    y: float
    z: float


@dataclass
class LocationSoundPacket(SoundPacket, DecodableVoicePacket):
    ID = 0x04

    location: Location

    @classmethod
    def from_buf(cls, buf: Buffer) -> 'LocationSoundPacket':
        sender = buf.unpack_uuid()
        location = Location(*buf.unpack("ddd"))
        data_len = buf.unpack_varint()
        data = buf.read(data_len)
        sequence = buf.unpack("l")

        return cls(
            sender=sender,
            location=location,
            data=data,
            sequence=sequence,
        )


@dataclass
class AuthenticatePacket(EncodableVoicePacket):
    ID = 0x05

    player_uuid: uuid.UUID
    secret: uuid.UUID

    def to_buf(self) -> bytes:
        return Buffer.pack_uuid(self.player_uuid) + \
               Buffer.pack_uuid(self.secret)


@dataclass
class AuthenticateAckPacket(DecodableVoicePacket):
    ID = 0x06

    @classmethod
    def from_buf(cls, buf: Buffer) -> 'AuthenticateAckPacket':
        return cls()


@dataclass
class PingPacket(EncodableVoicePacket, DecodableVoicePacket):
    ID = 0x07

    id: uuid.UUID
    timestamp: int

    def to_buf(self) -> bytes:
        return Buffer.pack_uuid(self.id) + Buffer.pack("l", self.timestamp)

    @classmethod
    def from_buf(cls, buf: Buffer) -> 'PingPacket':
        ping_id = buf.unpack_uuid()
        timestamp = buf.unpack("l")

        return cls(
            id=ping_id,
            timestamp=timestamp
        )


@dataclass
class KeepAlivePacket(EncodableVoicePacket):
    ID = 0x08

    def to_buf(self) -> bytes:
        return b""