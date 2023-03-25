# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import tictactoe_pb2 as tictactoe__pb2


class TicTacToeStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Ack = channel.unary_unary(
                '/TicTacToe/Ack',
                request_serializer=tictactoe__pb2.AckRequest.SerializeToString,
                response_deserializer=tictactoe__pb2.AckResponse.FromString,
                )
        self.Time = channel.unary_unary(
                '/TicTacToe/Time',
                request_serializer=tictactoe__pb2.TimeRequest.SerializeToString,
                response_deserializer=tictactoe__pb2.TimeResponse.FromString,
                )
        self.ReceiveTime = channel.unary_unary(
                '/TicTacToe/ReceiveTime',
                request_serializer=tictactoe__pb2.SetTime.SerializeToString,
                response_deserializer=tictactoe__pb2.SetTimeResponse.FromString,
                )
        self.ReceiveTimeString = channel.unary_unary(
                '/TicTacToe/ReceiveTimeString',
                request_serializer=tictactoe__pb2.SetTimeString.SerializeToString,
                response_deserializer=tictactoe__pb2.SetTimeResponse.FromString,
                )
        self.Move = channel.unary_unary(
                '/TicTacToe/Move',
                request_serializer=tictactoe__pb2.MoveRequest.SerializeToString,
                response_deserializer=tictactoe__pb2.MoveResponse.FromString,
                )
        self.Election = channel.unary_unary(
                '/TicTacToe/Election',
                request_serializer=tictactoe__pb2.ElectionMessage.SerializeToString,
                response_deserializer=tictactoe__pb2.ElectionResponse.FromString,
                )
        self.Coordinator = channel.unary_unary(
                '/TicTacToe/Coordinator',
                request_serializer=tictactoe__pb2.CoordinatorMessage.SerializeToString,
                response_deserializer=tictactoe__pb2.ElectionResponse.FromString,
                )
        self.GetGameBoard = channel.unary_unary(
                '/TicTacToe/GetGameBoard',
                request_serializer=tictactoe__pb2.BoardRequest.SerializeToString,
                response_deserializer=tictactoe__pb2.BoardResponse.FromString,
                )
        self.UpdatePlayers = channel.unary_unary(
                '/TicTacToe/UpdatePlayers',
                request_serializer=tictactoe__pb2.UpdateMessage.SerializeToString,
                response_deserializer=tictactoe__pb2.Empty.FromString,
                )


class TicTacToeServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Ack(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Time(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ReceiveTime(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ReceiveTimeString(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Move(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Election(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Coordinator(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetGameBoard(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def UpdatePlayers(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_TicTacToeServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Ack': grpc.unary_unary_rpc_method_handler(
                    servicer.Ack,
                    request_deserializer=tictactoe__pb2.AckRequest.FromString,
                    response_serializer=tictactoe__pb2.AckResponse.SerializeToString,
            ),
            'Time': grpc.unary_unary_rpc_method_handler(
                    servicer.Time,
                    request_deserializer=tictactoe__pb2.TimeRequest.FromString,
                    response_serializer=tictactoe__pb2.TimeResponse.SerializeToString,
            ),
            'ReceiveTime': grpc.unary_unary_rpc_method_handler(
                    servicer.ReceiveTime,
                    request_deserializer=tictactoe__pb2.SetTime.FromString,
                    response_serializer=tictactoe__pb2.SetTimeResponse.SerializeToString,
            ),
            'ReceiveTimeString': grpc.unary_unary_rpc_method_handler(
                    servicer.ReceiveTimeString,
                    request_deserializer=tictactoe__pb2.SetTimeString.FromString,
                    response_serializer=tictactoe__pb2.SetTimeResponse.SerializeToString,
            ),
            'Move': grpc.unary_unary_rpc_method_handler(
                    servicer.Move,
                    request_deserializer=tictactoe__pb2.MoveRequest.FromString,
                    response_serializer=tictactoe__pb2.MoveResponse.SerializeToString,
            ),
            'Election': grpc.unary_unary_rpc_method_handler(
                    servicer.Election,
                    request_deserializer=tictactoe__pb2.ElectionMessage.FromString,
                    response_serializer=tictactoe__pb2.ElectionResponse.SerializeToString,
            ),
            'Coordinator': grpc.unary_unary_rpc_method_handler(
                    servicer.Coordinator,
                    request_deserializer=tictactoe__pb2.CoordinatorMessage.FromString,
                    response_serializer=tictactoe__pb2.ElectionResponse.SerializeToString,
            ),
            'GetGameBoard': grpc.unary_unary_rpc_method_handler(
                    servicer.GetGameBoard,
                    request_deserializer=tictactoe__pb2.BoardRequest.FromString,
                    response_serializer=tictactoe__pb2.BoardResponse.SerializeToString,
            ),
            'UpdatePlayers': grpc.unary_unary_rpc_method_handler(
                    servicer.UpdatePlayers,
                    request_deserializer=tictactoe__pb2.UpdateMessage.FromString,
                    response_serializer=tictactoe__pb2.Empty.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'TicTacToe', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class TicTacToe(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Ack(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/TicTacToe/Ack',
            tictactoe__pb2.AckRequest.SerializeToString,
            tictactoe__pb2.AckResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Time(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/TicTacToe/Time',
            tictactoe__pb2.TimeRequest.SerializeToString,
            tictactoe__pb2.TimeResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def ReceiveTime(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/TicTacToe/ReceiveTime',
            tictactoe__pb2.SetTime.SerializeToString,
            tictactoe__pb2.SetTimeResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def ReceiveTimeString(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/TicTacToe/ReceiveTimeString',
            tictactoe__pb2.SetTimeString.SerializeToString,
            tictactoe__pb2.SetTimeResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Move(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/TicTacToe/Move',
            tictactoe__pb2.MoveRequest.SerializeToString,
            tictactoe__pb2.MoveResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Election(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/TicTacToe/Election',
            tictactoe__pb2.ElectionMessage.SerializeToString,
            tictactoe__pb2.ElectionResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Coordinator(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/TicTacToe/Coordinator',
            tictactoe__pb2.CoordinatorMessage.SerializeToString,
            tictactoe__pb2.ElectionResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetGameBoard(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/TicTacToe/GetGameBoard',
            tictactoe__pb2.BoardRequest.SerializeToString,
            tictactoe__pb2.BoardResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def UpdatePlayers(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/TicTacToe/UpdatePlayers',
            tictactoe__pb2.UpdateMessage.SerializeToString,
            tictactoe__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
