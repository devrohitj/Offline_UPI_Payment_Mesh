from typing import List
from copy import deepcopy

from schemas import MeshPacket


class VirtualDevice:

    def __init__(
        self,
        device_id: str,
        has_internet: bool = False
    ):

        self.device_id = device_id

        self.has_internet = has_internet

        self.packets: List[MeshPacket] = []


    def receive_packet(
        self,
        packet: MeshPacket
    ):

        if packet.ttl <= 0:
            return

        for existing in self.packets:

            if existing.packet_id == packet.packet_id:
                return

        self.packets.append(
            deepcopy(packet)
        )


    def broadcast(
        self,
        peers: list
    ):

        for packet in list(self.packets):

            if packet.ttl <= 1:
                continue

            forwarded = MeshPacket(
                packet_id=packet.packet_id,
                ttl=packet.ttl - 1,
                created_at=packet.created_at,
                ciphertext=packet.ciphertext
            )

            for peer in peers:

                if peer.device_id == self.device_id:
                    continue

                peer.receive_packet(
                    forwarded
                )


class MeshNetwork:

    def __init__(self):

        self.devices = {}

        self.add_device("phone-alice")

        self.add_device("phone-bob")

        self.add_device("stranger-1")

        self.add_device("stranger-2")

        self.add_device(
            "phone-bridge",
            has_internet=True
        )


    def add_device(
        self,
        device_id: str,
        has_internet: bool = False
    ):

        device = VirtualDevice(
            device_id,
            has_internet
        )

        self.devices[device_id] = device


    def inject_packet(
        self,
        device_id: str,
        packet: MeshPacket
    ):

        device = self.devices.get(
            device_id
        )

        if not device:
            return

        device.receive_packet(packet)


    def gossip_round(self):

        peers = list(
            self.devices.values()
        )

        for device in peers:

            device.broadcast(peers)


    def flush_bridges(
        self,
        handler
    ):

        results = []

        for device in self.devices.values():

            if not device.has_internet:
                continue

            for packet in device.packets:

                result = handler(packet)

                results.append(result)

        return results