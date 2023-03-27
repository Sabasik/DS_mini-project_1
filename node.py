import sys
import grpc
import tictactoe_pb2
import tictactoe_pb2_grpc
import time
import re
import random
import tictactoe
from concurrent import futures
from datetime import datetime, timedelta
from threading import Timer

pattern_set_symbol = re.compile("Set-symbol (\d), ([OX])")
pattern_list_board = re.compile("List-board")
pattern_start_game = re.compile("Start-game")
pattern_set_node_time = re.compile("Set-node-time (.*) (\d\d:\d\d:\d\d)")
pattern_set_time_out = re.compile("Set-time-out (players|game-master) (\d+(\.\d*)?)")

player_1_symbol = "X"
player_2_symbol = "O"


def print_help():
    print("""
    This is a TicTacToe node.
    Use -p to assign a port to the node. Example -p 5051.
    Use -n to assign a name to the node. Example -n MyNode.
    Default port is 5051 and default name is node.

    Required (ip aadresses of other nodes):
        -node2 x.x.x.x:xxxx
        -node3 x.x.x.x:xxxx

    Example command: python node.py -p 8080 -n MyNode -node2 192.168.1.212:5051 -node3 192.168.1.217:5051""")


def array_index(array, element):
    try:
        return array.index(element)
    except:
        return -1


def element_or_default(array, index, default):
    try:
        return array[index]
    except:
        return default


def node_port(args):
    default_port = 5051

    port_index = array_index(args, '-p') + 1
    if port_index != 0:
        return element_or_default(args, port_index, default_port)
    return default_port


def node_name(args):
    default_name = 'node'

    name_index = array_index(args, '-n') + 1
    if name_index != 0:
        return element_or_default(args, name_index, default_name)
    return default_name


def node_id(args):
    default_id = random.randint(1, 4000)

    id_index = array_index(args, '-i') + 1
    if id_index != 0:
        return int(element_or_default(args, id_index, default_id))
    return default_id


def other_nodes(args):
    node2_index = array_index(args, '-node2')
    if node2_index == -1:
        raise ValueError('-node2 missing')

    node2_value = element_or_default(args, node2_index + 1, '')
    if not node2_value:
        raise ValueError('-node2 value is missing')

    node3_index = array_index(args, '-node3')
    if node3_index == -1:
        raise ValueError('-node3 missing')

    node3_value = element_or_default(args, node3_index + 1, '')
    if not node3_value:
        raise ValueError('-node3 value is missing')

    return node2_value, node3_value


class TicTacToeServicer(tictactoe_pb2_grpc.TicTacToeServicer):
    def __init__(self, id, name, node2, node3):
        self.id = id
        self.name = name
        self.coordinator = None

        self.node2 = node2
        self.node3 = node3

        self.node2name = None
        self.node3name = None

        self.node2id = None
        self.node3id = None

        self.received_diff = False
        self.time_diff = 0

        self.game_board = None
        self.turn = None
        self.player_1 = None
        self.player_2 = None
        self.waiting_start = False
        self.has_game_started = False

        self.node2_is_active = False
        self.node3_is_active = False

        self.timeout_requested = False
        self.other_player_req_timeout = False
        self.coordinator_timeout_length = None

    def Ack(self, request, context):
        return tictactoe_pb2.AckResponse(name=self.name, id=self.id)

    def wait_for_others(self):
        while True:
            if not self.node2name:
                try:
                    with grpc.insecure_channel(self.node2) as channel:
                        stub = tictactoe_pb2_grpc.TicTacToeStub(channel)
                        response = stub.Ack(tictactoe_pb2.AckRequest())

                        self.node2name = response.name
                        self.node2id = response.id

                        print('Node2 ({}) is ready'.format(self.node2name))
                except:
                    print('Waiting for Node2 to connect...')

            if not self.node3name:
                try:
                    with grpc.insecure_channel(self.node3) as channel:
                        stub = tictactoe_pb2_grpc.TicTacToeStub(channel)
                        response = stub.Ack(tictactoe_pb2.AckRequest())

                        self.node3name = response.name
                        self.node3id = response.id

                        print('Node3 ({}) is ready'.format(self.node3name))
                except:
                    print('Waiting for Node3 to connect...')

            if self.node2name and self.node3name:
                print('Node2 ({}) and Node3 ({}) are ready'.format(self.node2name, self.node3name))
                return True

            time.sleep(0.5)

    def Start(self, request, context):
        return tictactoe_pb2.StartResponse(ready=self.waiting_start)

    def ask_status(self):
        node2_start = False
        node3_start = False
        while not(node2_start and node3_start):
            if not node2_start:
                try:
                    with grpc.insecure_channel(self.node2) as channel:
                        stub = tictactoe_pb2_grpc.TicTacToeStub(channel)
                        response = stub.Start(tictactoe_pb2.StartMessage())
                        node2_start = response.ready
                except:
                    raise ConnectionError('{} missing'.format(self.node2name))
            
            if not node3_start:
                try:
                    with grpc.insecure_channel(self.node3) as channel:
                        stub = tictactoe_pb2_grpc.TicTacToeStub(channel)
                        response = stub.Start(tictactoe_pb2.StartMessage())
                        node3_start = response.ready
                except:
                    raise ConnectionError('{} missing'.format(self.node3name))
            
            if not node2_start:
                print('Waiting for {} to join new game...'.format(self.node2name))

            if not node3_start:
                print('Waiting for {} to join new game...'.format(self.node3name))
            
            print()
            time.sleep(1)

    def Restart(self, request, context):
        timeout = request.timeout
        if timeout:
            print('Game restarted by timeout. Enter "Start-game" to start a new game.')
        else:
            restart_id = request.node_id
            restart_name = request.node_name
            print('Game restarted by {}#{}. Enter "Start-game" to start a new game.'.format(restart_name, restart_id))
        self.reset_fields()
        return tictactoe_pb2.Empty()
    
    def restart_game(self, timeout = False):
        self.reset_fields()
        try:
            with grpc.insecure_channel(self.node2) as channel:
                stub = tictactoe_pb2_grpc.TicTacToeStub(channel)
                _ = stub.Restart(tictactoe_pb2.RestartMessage(node_id=self.id, node_name=self.name, timeout=timeout))
        except:
            raise ConnectionError('{} missing'.format(self.node2name))
        
        try:
            with grpc.insecure_channel(self.node3) as channel:
                stub = tictactoe_pb2_grpc.TicTacToeStub(channel)
                _ = stub.Restart(tictactoe_pb2.RestartMessage(node_id=self.id, node_name=self.name, timeout=timeout))
        except:
            raise ConnectionError('{} missing'.format(self.node3name))
        if timeout:
            print('Game restarted by timeout. Enter "Start-game" to start a new game.')
        else:
            print('Game restarted. Enter "Start-game" to start a new game.')

    def Time(self, request, context):
        time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] + "Z"
        return tictactoe_pb2.TimeResponse(time=time)

    def ReceiveTime(self, request, context):
        if self.received_diff:
            return tictactoe_pb2.SetTimeResponse(time_accepted=False)
        
        # print('{} received time diff {}'.format(self.name, request.time_diff))

        self.received_diff = True
        self.time_diff = request.time_diff
        return tictactoe_pb2.SetTimeResponse(time_accepted=True)

    def ReceiveTimeString(self, request, context):
        print('{} received new time {}'.format(self.name, request.time))
        current_datetime = datetime.utcnow() + timedelta(milliseconds=self.time_diff)
        future_datetime = datetime.combine(current_datetime.date(), datetime.strptime(request.time, '%H:%M:%S').time())
        self.time_diff = (future_datetime - datetime.utcnow()) / timedelta(milliseconds=1)
        print("New UTC time:", datetime.utcnow() + timedelta(milliseconds=self.time_diff))
        return tictactoe_pb2.SetTimeResponse(time_accepted=True)

    def sync_time(self):
        # Node 2 time
        try:
            with grpc.insecure_channel(self.node2) as channel:
                stub = tictactoe_pb2_grpc.TicTacToeStub(channel)
                request_start = time.time()
                response = stub.Time(tictactoe_pb2.TimeRequest())
                request_end = time.time()
                current_local_time = datetime.utcnow()

                rtt = request_end - request_start
                estimated_node2_time = datetime.strptime(response.time, "%Y-%m-%d %H:%M:%S.%fZ") + timedelta(
                    seconds=(rtt / 2))

                node2_time_diff = -(current_local_time - estimated_node2_time)
        except:
            raise ConnectionError('{} missing'.format(self.node2name))

        # Node 3 time
        try:
            with grpc.insecure_channel(self.node3) as channel:
                stub = tictactoe_pb2_grpc.TicTacToeStub(channel)
                request_start = time.time()
                response = stub.Time(tictactoe_pb2.TimeRequest())
                request_end = time.time()
                current_local_time = datetime.utcnow()

                rtt = request_end - request_start
                estimated_node3_time = datetime.strptime(response.time, "%Y-%m-%d %H:%M:%S.%fZ") + timedelta(
                    seconds=(rtt / 2))

                node3_time_diff = -(current_local_time - estimated_node3_time)
        except:
            raise ConnectionError('{} missing'.format(self.node3name))

        local_time_diff = (node3_time_diff + node2_time_diff) / 3
        node2_time_diff = -(node2_time_diff - local_time_diff) / timedelta(milliseconds=1)
        node3_time_diff = -(node3_time_diff - local_time_diff) / timedelta(milliseconds=1)
        local_time_diff = local_time_diff / timedelta(milliseconds=1)
        if not self.received_diff:
            # print('{} is sending time information'.format(self.name))
            try:
                with grpc.insecure_channel(self.node2) as channel:
                    stub = tictactoe_pb2_grpc.TicTacToeStub(channel)
                    response = stub.ReceiveTime(tictactoe_pb2.SetTime(time_diff=node2_time_diff))
                    node2_accepted = response.time_accepted
                     # print('Node2 accepted: ', response.time_accepted)
            except:
                raise ConnectionError('{} missing'.format(self.node2name))

            if node2_accepted:
                try:
                    with grpc.insecure_channel(self.node3) as channel:
                        stub = tictactoe_pb2_grpc.TicTacToeStub(channel)
                        response = stub.ReceiveTime(tictactoe_pb2.SetTime(time_diff=node3_time_diff))
                        node3_accepted = response.time_accepted
                        # print('Node3 accepted: ', response.time_accepted)
                except:
                    raise ConnectionError('{} missing'.format(self.node3name))

            if node2_accepted and node3_accepted:
                self.time_diff = local_time_diff

    def send_coordinator_message(self, target_node, target_name):
        try:
            with grpc.insecure_channel(target_node) as channel:
                stub = tictactoe_pb2_grpc.TicTacToeStub(channel)
                _ = stub.Coordinator(tictactoe_pb2.CoordinatorMessage(coordinator_id=self.id))
        except:
            raise ConnectionError('{} missing'.format(target_name))

    def send_election_message(self, target_node, target_name):
        try:
            with grpc.insecure_channel(target_node) as channel:
                stub = tictactoe_pb2_grpc.TicTacToeStub(channel)
                response = stub.Election(tictactoe_pb2.ElectionMessage(id=self.id))
                node_status = response.acknowledgement
        except:
            raise ConnectionError('{} missing'.format(target_name))
        return node_status

    # Election is implemented with Bullying algorithm
    def start_election(self):
        # Send Victory message immediately
        if self.id > self.node2id and self.id > self.node3id:
            self.send_coordinator_message(self.node2, self.node2name)
            self.send_coordinator_message(self.node3, self.node2name)

            self.coordinator = self.id

        # Check if nodes with higher id are available
        elif self.id < self.node2id and self.id < self.node3id:
            node2_status = self.send_election_message(self.node2, self.node2name)
            node3_status = self.send_election_message(self.node3, self.node3name)

            if not (node2_status or node3_status):
                self.coordinator = self.id

        # Check if node 2 is available
        elif self.id < self.node2id:
            node2_status = self.send_election_message(self.node2, self.node2name)

            if not (node2_status):
                self.send_coordinator_message(self.node3, self.node3name)

                self.coordinator = self.id

        # Check if node 3 is available
        else:
            node3_status = self.send_election_message(self.node3, self.node3name)

            if not (node3_status):
                self.send_coordinator_message(self.node2, self.node2name)

                self.coordinator = self.id

    def Election(self, request, context):
        sender_id = request.id
        response = sender_id < self.id  # OK
        return tictactoe_pb2.ElectionResponse(acknowledgement=response)

    def Coordinator(self, request, context):
        self.coordinator = request.coordinator_id
        return tictactoe_pb2.ElectionResponse(acknowledgement=True)

    def Move(self, request, context):
        if request.player_id == self.node2id:
            self.node2_is_active = True
        elif request.player_id == self.node3id:
            self.node3_is_active = True
        if request.player_id != self.turn:
            return tictactoe_pb2.MoveResponse(
                success=False,
                fail_message="It is the other player's turn!")
        elif (request.player_id == self.player_1 and request.symbol != player_1_symbol):
            return tictactoe_pb2.MoveResponse(
                success=False,
                fail_message="You can't set symbol {}! Your symbol is {}.".format(request.symbol, player_1_symbol))
        elif (request.player_id == self.player_2 and request.symbol != player_2_symbol):
            return tictactoe_pb2.MoveResponse(
                success=False,
                fail_message="You can't set symbol {}! Your symbol is {}.".format(request.symbol, player_2_symbol))
        elif self.game_board[request.tile - 1] != " ":
            return tictactoe_pb2.MoveResponse(
                success=False,
                fail_message="Tile {} is already filled with {}.".format(request.tile,
                                                                         self.game_board[request.tile - 1]))
        else:
            self.game_board[request.tile - 1] = request.symbol
            if self.turn == self.player_1:
                self.turn = self.player_2
            else:
                self.turn = self.player_1
            print("{} set at {}.".format(request.symbol, request.tile))
            self.check_end()
            return tictactoe_pb2.MoveResponse(
                success=True,
                fail_message="Success!")

    def UpdatePlayers(self, request, context):
        self.has_game_started = request.has_game_started
        print(request.update_message)
        return tictactoe_pb2.Empty()

    def GetGameBoard(self, request, context):
        if self.game_board:
            if request.player_id == self.node2id:
                self.node2_is_active = True
            elif request.player_id == self.node3id:
                self.node3_is_active = True
            return tictactoe_pb2.BoardResponse(
                board=self.game_board,
                timestamp=str(datetime.utcnow() + timedelta(milliseconds=self.time_diff)),
                success=True)
        return tictactoe_pb2.BoardResponse(
            board=self.game_board,
            timestamp=str(datetime.utcnow() + timedelta(milliseconds=self.time_diff)),
            success=False)

    def process_command(self, command):
        m = pattern_set_symbol.match(command)
        if m:
            self.set_symbol(int(m.group(1)), m.group(2))
            return
        m = pattern_list_board.match(command)
        if m:
            self.list_board()
            return
        m = pattern_set_node_time.match(command)
        if m:
            self.set_node_time(m.group(1), m.group(2))
            return
        m = pattern_set_time_out.match(command)
        if m:
            self.set_time_out(m.group(1), float(m.group(2)))
            return
        m = pattern_start_game.match(command)
        if m:
            self.start_game()
            return
        print("Unknown command!")

    def set_symbol(self, position, symbol):
        if not self.has_game_started:
            print("Game has not started yet!")
            return
        print("Set symbol", symbol, position)
        if self.coordinator == self.id:
            print("Game master cannot set symbols!")
        else:
            if self.coordinator == self.node2id:
                try:
                    with grpc.insecure_channel(self.node2) as channel:
                        stub = tictactoe_pb2_grpc.TicTacToeStub(channel)
                        response = stub.Move(tictactoe_pb2.MoveRequest(
                            tile=position,
                            symbol=symbol,
                            player_id=self.id))
                except:
                    raise ConnectionError('{} missing'.format(self.node2name))
            else:
                try:
                    with grpc.insecure_channel(self.node3) as channel:
                        stub = tictactoe_pb2_grpc.TicTacToeStub(channel)
                        response = stub.Move(tictactoe_pb2.MoveRequest(
                            tile=position,
                            symbol=symbol,
                            player_id=self.id))
                except:
                    raise ConnectionError('{} missing'.format(self.node3name))
            if response.success:
                print("Move accepted!")
            else:
                print(response.fail_message)

    def list_board(self):
        if not self.has_game_started:
            print("Game has not started yet!")
            return
        response = False
        if self.coordinator == self.id:
            response = self.GetGameBoard(tictactoe_pb2.BoardRequest(player_id = self.id), None)
        elif self.coordinator == self.node2id:
            try:
                with grpc.insecure_channel(self.node2) as channel:
                    stub = tictactoe_pb2_grpc.TicTacToeStub(channel)
                    response = stub.GetGameBoard(tictactoe_pb2.BoardRequest(player_id = self.id))
            except:
                raise ConnectionError('{} missing'.format(self.node2name))
        elif self.coordinator == self.node3id:
            try:
                with grpc.insecure_channel(self.node3) as channel:
                    stub = tictactoe_pb2_grpc.TicTacToeStub(channel)
                    response = stub.GetGameBoard(tictactoe_pb2.BoardRequest(player_id = self.id))
            except:
                raise ConnectionError('{} missing'.format(self.node3name))
        if not response or not response.success:
            print("No board found :(")
        else:
            print(response.timestamp, ',', tictactoe.print_board_list(response.board))

    def set_node_time(self, node_name, time):
        print("Set node time", node_name, time)
        if self.name == node_name:
            current_datetime = datetime.utcnow() + timedelta(milliseconds=self.time_diff)
            future_datetime = datetime.combine(current_datetime.date(), datetime.strptime(time, '%H:%M:%S').time())
            self.time_diff = (future_datetime - datetime.utcnow()) / timedelta(milliseconds=1)
            print("New UTC time:", datetime.utcnow() + timedelta(milliseconds=self.time_diff))
        elif self.coordinator == self.id:
            if self.node2name == node_name:
                try:
                    with grpc.insecure_channel(self.node2) as channel:
                        stub = tictactoe_pb2_grpc.TicTacToeStub(channel)
                        response = stub.ReceiveTimeString(tictactoe_pb2.SetTimeString(time=time))
                        print(self.node2name, 'accepted:', response.time_accepted)
                except:
                    raise ConnectionError('{} missing'.format(self.node2name))
            elif self.node3name == node_name:
                try:
                    with grpc.insecure_channel(self.node3) as channel:
                        stub = tictactoe_pb2_grpc.TicTacToeStub(channel)
                        response = stub.ReceiveTimeString(tictactoe_pb2.SetTimeString(time=time))
                        print(self.node3name, 'accepted:', response.time_accepted)
                except:
                    raise ConnectionError('{} missing'.format(self.node3name))
            else:
                print(node_name, "is not a valid node name.")
        else:
            print("Only the game master can change time of other nodes.")

    def Timeout(self, request, context):
        origin_id = request.node_id
        origin_name = request.node_name
        timeout_length = request.timeout_len

        # TODO: if the message is not from coordinator, send info to other player instead asking for confirmation
        if origin_id != self.coordinator:
            # Confirmation from other player
            if self.timeout_requested and not self.other_player_req_timeout:
                print('{} accepted the timeout request'.format(origin_name))
                self.other_player_req_timeout = True
                self.start_timeout_timer(timeout_length)
            
            # Other player canceling, possibly received response from server
            elif self.other_player_req_timeout:
                # Ask for confirmation
                print('{} cancelled timeout'.format(origin_name))
                self.timeout_requested = False
                self.other_player_req_timeout = False
                if self.timer is not None:
                    self.timer.cancel()
                self.timer = None
            
            # Other player asking for confirmation
            else:
                # TODO: timeout has to be canceled as well
                # Ask user for input
                confirmation = input('Do you accept timeout request (yes/no): ')
                if origin_id == self.node2id:
                    origin_node = self.node2
                else:
                    origin_node = self.node3
                if confirmation.lower() == 'yes':
                    self.send_timeout(origin_node, origin_name, timeout_length)
                    self.timeout_requested = True
                    self.other_player_req_timeout = True
                    print('Timeout has been set')
                else:
                    pass # Nothing needs to be done
        else:
            timeout_message = 'New time-out for players = {} minutes'.format(timeout_length)
            print(timeout_message)
        return tictactoe_pb2.Empty()

    def send_timeout(self, target_node, target_name, length):
        try:
            with grpc.insecure_channel(target_node) as channel:
                stub = tictactoe_pb2_grpc.TicTacToeStub(channel)
                _ = stub.Timeout(tictactoe_pb2.TimeoutRequest(node_id=self.id, node_name=self.name, timeout_len=length))
        except:
            raise ConnectionError('{} missing'.format(target_name))
        
    def start_timeout_timer(self, time = None):
        if self.timer is not None:
            self.timer.cancel()
        if time is None:
            # Default inactivity timer
            self.timer = Timer(60, self.restart_by_timeout)
        else:
            self.timer = Timer(60 * time, self.restart_by_timeout)
        self.timer.start()

    def restart_by_timeout(self):
        if self.node2_is_active or self.node3_is_active:
            self.node2_is_active = False
            self.node3_is_active = False
            self.start_timeout_timer(self.coordinator_timeout_length)
        else:
            self.restart_game(True)

    def set_time_out(self, role, time):
        if not self.has_game_started:
            print("Game has not started yet! The roles have not been set.")
            return
        # For server, double verification is needed
        is_coordinator = self.coordinator == self.id
        if role == 'game-master' and is_coordinator:
            print('Can\'t set timeout to yourself')
            return
        
        if not is_coordinator and role == 'players':
            print('You can only set time-out to game-master')
            return

        if is_coordinator:
            self.send_timeout(self.node2, self.node2name, float(time))
            self.send_timeout(self.node3, self.node3name, float(time))
            print('New time-out for players = {} minutes'.format(time))
            self.start_timeout_timer(time)
        else:
            self.timeout_requested = True
            if self.node2id != self.coordinator:
                self.send_timeout(self.node2, self.node2name, float(time))
            else:
                self.send_timeout(self.node3, self.node3name, float(time))

    def start_game(self):
        if self.has_game_started:
            print("Game has already started!")
            confirmation = input('Are you sure you want to start a new game (yes/no): ')
            if confirmation.lower() == 'yes':
                self.restart_game()
            else:
                print('Continuing game')
            return
        
        print("Game setup. Please wait...")
        # Resetting fiels as this might be restart scenario
        self.reset_fields()
        # Wait for other nodes to join new game
        self.waiting_start = True
        self.ask_status()
        self.waiting_start = False

        # Time sync
        self.sync_time()

        while self.time_diff is None:
            print('{} waiting for time sync...'.format(self.name))
            time.sleep(0.5)
        
        print('Time synchronization completed')
        # Leader election
        while not self.coordinator:
            self.start_election()
            print('Waiting for coordinator to be elected...')
            time.sleep(0.25)

        print('Coordinator elected')
        if self.id == self.coordinator:
            print('You are selected as coordinator')
            self.init_game()
            self.start_timeout_timer()
        else:
            if self.node2id == self.coordinator:
                print('{} selected as coordinator'.format(self.node2name))
            else:
                print('{} selected as coordinator'.format(self.node3name))

        # Game loop
        print('{} setup completed. Game is ready\n'.format(self.name))


    def check_end(self):
        is_end, result = tictactoe.check_end_list(self.game_board)
        if is_end:
            result_text = tictactoe.get_result(result) + " With the board " + tictactoe.print_board_list(
                self.game_board) + "."
            print(result_text)
            try:
                with grpc.insecure_channel(self.node2) as channel:
                    stub = tictactoe_pb2_grpc.TicTacToeStub(channel)
                    stub.UpdatePlayers(tictactoe_pb2.UpdateMessage(
                        update_message=result_text,
                        has_game_started=False
                    ))
            except:
                raise ConnectionError('{} missing'.format(self.node2name))
            try:
                with grpc.insecure_channel(self.node3) as channel:
                    stub = tictactoe_pb2_grpc.TicTacToeStub(channel)
                    stub.UpdatePlayers(tictactoe_pb2.UpdateMessage(
                        update_message=result_text,
                        has_game_started=False
                    ))
            except:
                raise ConnectionError('{} missing'.format(self.node3name))
            self.reset_fields()

    def reset_fields(self):
        self.coordinator = None
        self.timer = None

        self.received_diff = False
        self.time_diff = 0

        self.game_board = None
        self.turn = None
        self.player_1 = None
        self.player_2 = None
        self.has_game_started = False

        self.node2_is_active = False
        self.node3_is_active = False

        self.timeout_requested = False
        self.other_player_req_timeout = False
        self.coordinator_timeout_length = None

    def init_game(self):
        self.game_board = tictactoe.blank_board_list()
        random_bit = random.randint(0, 1)
        if random_bit == 0:
            self.player_1 = self.node2id
            self.player_2 = self.node3id
            try:
                with grpc.insecure_channel(self.node2) as channel:
                    stub = tictactoe_pb2_grpc.TicTacToeStub(channel)
                    stub.UpdatePlayers(tictactoe_pb2.UpdateMessage(
                        update_message='You are player 1 and using symbol ' + player_1_symbol + ". It's your turn!",
                        has_game_started=True
                    ))
            except:
                raise ConnectionError('{} missing'.format(self.node2name))
            try:
                with grpc.insecure_channel(self.node3) as channel:
                    stub = tictactoe_pb2_grpc.TicTacToeStub(channel)
                    stub.UpdatePlayers(tictactoe_pb2.UpdateMessage(
                        update_message='You are player 2 and using symbol ' + player_2_symbol,
                        has_game_started=True
                    ))
            except:
                raise ConnectionError('{} missing'.format(self.node3name))
        else:
            self.player_1 = self.node3id
            self.player_2 = self.node2id
            try:
                with grpc.insecure_channel(self.node3) as channel:
                    stub = tictactoe_pb2_grpc.TicTacToeStub(channel)
                    stub.UpdatePlayers(tictactoe_pb2.UpdateMessage(
                        update_message='You are player 1 and using symbol ' + player_1_symbol + ". It's your turn!",
                        has_game_started=True
                    ))
            except:
                raise ConnectionError('{} missing'.format(self.node3name))
            try:
                with grpc.insecure_channel(self.node2) as channel:
                    stub = tictactoe_pb2_grpc.TicTacToeStub(channel)
                    stub.UpdatePlayers(tictactoe_pb2.UpdateMessage(
                        update_message='You are player 2 and using symbol ' + player_2_symbol,
                        has_game_started=True
                    ))
            except:
                raise ConnectionError('{} missing'.format(self.node2name))
        self.turn = self.player_1
        self.has_game_started = True

    def QuitGame(self, request, context):
        node_id = request.node_id
        node_name = request.node_name
        self.has_game_started = False
        print('{}#{} left the game. Current game ended.'.format(node_name, node_id))
        return tictactoe_pb2.Empty()

    def send_quit_game(self):
        try:
            with grpc.insecure_channel(self.node2) as channel:
                stub = tictactoe_pb2_grpc.TicTacToeStub(channel)
                _ = stub.QuitGame(tictactoe_pb2.QuitMessage(node_id=self.id, node_name=self.name))
        except:
            pass

        try:
            with grpc.insecure_channel(self.node3) as channel:
                stub = tictactoe_pb2_grpc.TicTacToeStub(channel)
                _ = stub.QuitGame(tictactoe_pb2.QuitMessage(node_id=self.id, node_name=self.name))
        except:
            pass


def serve():
    if array_index(sys.argv, '--help') != -1:
        print_help()
        return

    # Server config
    id = node_id(sys.argv)
    name = node_name(sys.argv)
    port = node_port(sys.argv)
    node2, node3 = other_nodes(sys.argv)

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))

    servicer = TicTacToeServicer(id, name, node2, node3)
    tictactoe_pb2_grpc.add_TicTacToeServicer_to_server(servicer, server)

    server.add_insecure_port('0.0.0.0:{}'.format(port))
    server.start()

    print('Started TicTacToe node#{} {} on port {}'.format(id, name, port))
    print('Node2: {}'.format(node2))
    print('Node3: {}\n'.format(node3))

    # Wait for other nodes to become available
    servicer.wait_for_others()

    try:
        while True:
            user_command = input('{}>'.format(name))
            servicer.process_command(user_command)
    except KeyboardInterrupt:
        servicer.send_quit_game()
        server.stop(0)


if __name__ == '__main__':
    serve()
