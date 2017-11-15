# -*- coding: utf-8 -

import logging
log = logging.getLogger(__name__)

import asyncio

import pkg_resources
import socket
import ssl
import struct
import sys

try:
    PROTOBUF_VERSION = pkg_resources.get_distribution('protobuf').version
except pkg_resources.DistributionNotFound:
    PROTOBUF_VERSION = 'unknown'

if PROTOBUF_VERSION.startswith('3'):
    from . import proto_pb2 as pb
else:
    from . import pb

class Event(object):
    def __init__(self, event=None, params=None):
        if event:
            self.event = event
        elif params:
            self.event = pb.Event()
            for key, value in params.items():
                setattr(self, key, value)
        else:
            self.event = pb.Event()

    def __getattr__(self, name):
        if name == 'metric':
            name = 'metric_f'
        if name in set(f.name for f in pb.Event.DESCRIPTOR.fields):
            return getattr(self.event, name)

    def __setattr__(self, name, value):
        if name == 'metric':
            name = 'metric_f'
        if name == 'tags':
            self.event.tags.extend(value)
        elif name == 'attributes':
            if type(value) == dict:
                for key, val in value.items():
                    a = self.event.attributes.add()
                    a.key = key
                    if isinstance(val, bytes):
                        val = val.decode('utf-8')
                    elif not isinstance(val, str):
                        val = str(val)
                    a.value = str(val)
            else:
                raise TypeError("'attributes' parameter must be type 'dict'")
        elif name in set(f.name for f in pb.Event.DESCRIPTOR.fields):
            setattr(self.event, name, value)
        else:
            object.__setattr__(self, name, value)

    def __str__(self):
        return str(self.event)

class Message(object):
    def __init__(self, message=None, events=None, raw=None, query=None):
        if raw:
            self.message = pb.Msg().FromString(raw)
        elif message:
            self.message = message
        elif events:
            self.message = pb.Msg()
            self.message.events.extend([e.event for e in events])
        else:
            self.message = pb.Msg()
    
    def __getattr__(self, name):
        if name in set(f.name for f in pb.Msg.DESCRIPTOR.fields):
            return getattr(self.message, name)

    def __setattr__(self, name, value):
        if name in set(f.name for f in pb.Msg.DESCRIPTOR.fields):
            setattr(self.message, name, value)
        else:
            object.__setattr__(self, name, value)

    # Special-case the `events` field so we get boxed objects
    @property
    def events(self):
        return [Event(event=e) for e in self.message.events]

    @property
    def raw(self):
        return self.message.SerializeToString()

class Client(object):
    def __init__(self, loop, host='127.0.0.1', port=5555, transport=None):
        self.host = host
        self.port=port
        self.loop = loop
        self.transport = transport

    async def write(self, message):
        try:
            reader, writer = await asyncio.open_connection(self.host, self.port, loop=self.loop)
            writer.write(struct.pack('!I', len(message)) + message)
            log.debug("Reading Riemann Response Length Header")
            response = await reader.read(4)
            rxlen = struct.unpack('!I', response)[0]
            log.debug("Reading Riemann Response")
            riemann_response = await reader.read(rxlen)
            return riemann_response
        except Exception as msg:
            print(msg)

    async def transmit(self, message):
        print('transmitting')
        for i in range(2):
            try:
                raw = await self.write(message.raw)
                print(raw)
                return Message(raw=raw)
            except Exception as err:
                print(err)
        return Message()

    async def send(self, *events):
        message = Message(events=[Event(params=event) for event in events])
        response = await self.transmit(message)
        return response.ok

    