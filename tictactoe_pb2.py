# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: tictactoe.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0ftictactoe.proto\"\x0c\n\nAckRequest\"\'\n\x0b\x41\x63kResponse\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\n\n\x02id\x18\x02 \x01(\x05\"\x0e\n\x0cStartMessage\"\x1e\n\rStartResponse\x12\r\n\x05ready\x18\x01 \x01(\x08\"4\n\x0eRestartMessage\x12\x0f\n\x07node_id\x18\x01 \x01(\x05\x12\x11\n\tnode_name\x18\x02 \x01(\t\"\r\n\x0bTimeRequest\"\x1c\n\x0cTimeResponse\x12\x0c\n\x04time\x18\x01 \x01(\t\"\x1c\n\x07SetTime\x12\x11\n\ttime_diff\x18\x01 \x01(\x02\"\x1d\n\rSetTimeString\x12\x0c\n\x04time\x18\x01 \x01(\t\"(\n\x0fSetTimeResponse\x12\x15\n\rtime_accepted\x18\x01 \x01(\x08\"\x1d\n\x0f\x45lectionMessage\x12\n\n\x02id\x18\x01 \x01(\x05\"+\n\x10\x45lectionResponse\x12\x17\n\x0f\x61\x63knowledgement\x18\x01 \x01(\x08\",\n\x12\x43oordinatorMessage\x12\x16\n\x0e\x63oordinator_id\x18\x01 \x01(\x05\">\n\x0bMoveRequest\x12\x0c\n\x04tile\x18\x01 \x01(\x05\x12\x11\n\tplayer_id\x18\x02 \x01(\x05\x12\x0e\n\x06symbol\x18\x03 \x01(\t\"5\n\x0cMoveResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x14\n\x0c\x66\x61il_message\x18\x02 \x01(\t\"\x0e\n\x0c\x42oardRequest\"B\n\rBoardResponse\x12\r\n\x05\x62oard\x18\x01 \x03(\t\x12\x11\n\ttimestamp\x18\x02 \x01(\t\x12\x0f\n\x07success\x18\x03 \x01(\x08\"A\n\rUpdateMessage\x12\x16\n\x0eupdate_message\x18\x01 \x01(\t\x12\x18\n\x10has_game_started\x18\x02 \x01(\x08\"1\n\x0bQuitMessage\x12\x0f\n\x07node_id\x18\x01 \x01(\x05\x12\x11\n\tnode_name\x18\x02 \x01(\t\"\x07\n\x05\x45mpty2\x9f\x04\n\tTicTacToe\x12\"\n\x03\x41\x63k\x12\x0b.AckRequest\x1a\x0c.AckResponse\"\x00\x12(\n\x05Start\x12\r.StartMessage\x1a\x0e.StartResponse\"\x00\x12$\n\x07Restart\x12\x0f.RestartMessage\x1a\x06.Empty\"\x00\x12%\n\x04Time\x12\x0c.TimeRequest\x1a\r.TimeResponse\"\x00\x12+\n\x0bReceiveTime\x12\x08.SetTime\x1a\x10.SetTimeResponse\"\x00\x12\x37\n\x11ReceiveTimeString\x12\x0e.SetTimeString\x1a\x10.SetTimeResponse\"\x00\x12%\n\x04Move\x12\x0c.MoveRequest\x1a\r.MoveResponse\"\x00\x12\x31\n\x08\x45lection\x12\x10.ElectionMessage\x1a\x11.ElectionResponse\"\x00\x12\x37\n\x0b\x43oordinator\x12\x13.CoordinatorMessage\x1a\x11.ElectionResponse\"\x00\x12/\n\x0cGetGameBoard\x12\r.BoardRequest\x1a\x0e.BoardResponse\"\x00\x12)\n\rUpdatePlayers\x12\x0e.UpdateMessage\x1a\x06.Empty\"\x00\x12\"\n\x08QuitGame\x12\x0c.QuitMessage\x1a\x06.Empty\"\x00\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'tictactoe_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _ACKREQUEST._serialized_start=19
  _ACKREQUEST._serialized_end=31
  _ACKRESPONSE._serialized_start=33
  _ACKRESPONSE._serialized_end=72
  _STARTMESSAGE._serialized_start=74
  _STARTMESSAGE._serialized_end=88
  _STARTRESPONSE._serialized_start=90
  _STARTRESPONSE._serialized_end=120
  _RESTARTMESSAGE._serialized_start=122
  _RESTARTMESSAGE._serialized_end=174
  _TIMEREQUEST._serialized_start=176
  _TIMEREQUEST._serialized_end=189
  _TIMERESPONSE._serialized_start=191
  _TIMERESPONSE._serialized_end=219
  _SETTIME._serialized_start=221
  _SETTIME._serialized_end=249
  _SETTIMESTRING._serialized_start=251
  _SETTIMESTRING._serialized_end=280
  _SETTIMERESPONSE._serialized_start=282
  _SETTIMERESPONSE._serialized_end=322
  _ELECTIONMESSAGE._serialized_start=324
  _ELECTIONMESSAGE._serialized_end=353
  _ELECTIONRESPONSE._serialized_start=355
  _ELECTIONRESPONSE._serialized_end=398
  _COORDINATORMESSAGE._serialized_start=400
  _COORDINATORMESSAGE._serialized_end=444
  _MOVEREQUEST._serialized_start=446
  _MOVEREQUEST._serialized_end=508
  _MOVERESPONSE._serialized_start=510
  _MOVERESPONSE._serialized_end=563
  _BOARDREQUEST._serialized_start=565
  _BOARDREQUEST._serialized_end=579
  _BOARDRESPONSE._serialized_start=581
  _BOARDRESPONSE._serialized_end=647
  _UPDATEMESSAGE._serialized_start=649
  _UPDATEMESSAGE._serialized_end=714
  _QUITMESSAGE._serialized_start=716
  _QUITMESSAGE._serialized_end=765
  _EMPTY._serialized_start=767
  _EMPTY._serialized_end=774
  _TICTACTOE._serialized_start=777
  _TICTACTOE._serialized_end=1320
# @@protoc_insertion_point(module_scope)
