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

pattern_set_symbol = re.compile("Set-symbol (\d), ([OX])")
pattern_list_board = re.compile("List-board")
pattern_start_game = re.compile("Start-game")
pattern_set_node_time = re.compile("Set-node-time (.*) (\d\d:\d\d:\d\d)")
pattern_set_time_out = re.compile("Set-time-out (players|game-master) (\d+(\.\d*)?)")

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
        self.node3id= None

        self.received_diff = False
        self.time_diff = 0

        self.game_board = None

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
                    print('Waiting for Node2...')
            
            if not self.node3name:
                try:
                    with grpc.insecure_channel(self.node3) as channel:
                        stub = tictactoe_pb2_grpc.TicTacToeStub(channel)
                        response = stub.Ack(tictactoe_pb2.AckRequest())

                        self.node3name = response.name
                        self.node3id = response.id

                        print('Node3 ({}) is ready'.format(self.node3name))
                except:
                    print('Waiting for Node3...')

            if self.node2name and self.node3name:
                print('Node2 ({}) and Node3 ({}) are ready'.format(self.node2name, self.node3name))
                return True
            
            time.sleep(0.5)

    def Time(self, request, context):
        time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] + "Z"
        return tictactoe_pb2.TimeResponse(time=time)
    
    def ReceiveTime(self, request, context):
        if self.received_diff:
            return tictactoe_pb2.SetTimeResponse(time_accepted=False)
        print('{} received time diff {}'.format(self.name, request.time_diff))
        self.received_diff = True
        self.time_diff = request.time_diff
        return tictactoe_pb2.SetTimeResponse(time_accepted=True)
    
    def ReceiveTimeString(self, request, context):
        print('{} received new time {}'.format(self.name, request.time))
        current_datetime = datetime.utcnow()+timedelta(milliseconds=self.time_diff)
        future_datetime = datetime.combine(current_datetime.date(),datetime.strptime(request.time,'%H:%M:%S').time())
        self.time_diff = (future_datetime-datetime.utcnow())/timedelta(milliseconds=1)
        print("New UTC time:", datetime.utcnow()+timedelta(milliseconds=self.time_diff))
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
                estimated_node2_time = datetime.strptime(response.time, "%Y-%m-%d %H:%M:%S.%fZ") + timedelta(seconds=(rtt / 2))

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
                estimated_node3_time = datetime.strptime(response.time, "%Y-%m-%d %H:%M:%S.%fZ") + timedelta(seconds=(rtt / 2))

                node3_time_diff = -(current_local_time - estimated_node3_time)
        except:
            raise ConnectionError('{} missing'.format(self.node3name))
        
        local_time_diff = (node3_time_diff + node2_time_diff) / 3
        node2_time_diff = -(node2_time_diff - local_time_diff) / timedelta(milliseconds=1)
        node3_time_diff = -(node3_time_diff - local_time_diff) / timedelta(milliseconds=1)
        local_time_diff = local_time_diff / timedelta(milliseconds=1)
        if not self.received_diff:
            print('{} is sending time information'.format(self.name))
            try:
                with grpc.insecure_channel(self.node2) as channel:
                    stub = tictactoe_pb2_grpc.TicTacToeStub(channel)
                    response = stub.ReceiveTime(tictactoe_pb2.SetTime(time_diff=node2_time_diff))
                    node2_accepted = response.time_accepted
                    print('Node2 accepted: ', response.time_accepted)
            except:
                raise ConnectionError('{} missing'.format(self.node2name))
            
            if node2_accepted:
                try:
                    with grpc.insecure_channel(self.node3) as channel:
                        stub = tictactoe_pb2_grpc.TicTacToeStub(channel)
                        response = stub.ReceiveTime(tictactoe_pb2.SetTime(time_diff=node3_time_diff))
                        node3_accepted = response.time_accepted
                        print('Node3 accepted: ', response.time_accepted)
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
        response = sender_id < self.id # OK
        return tictactoe_pb2.ElectionResponse(acknowledgement=response)

    def Coordinator(self, request, context):
        self.coordinator = request.coordinator_id
        return tictactoe_pb2.ElectionResponse(acknowledgement=True)

    def Move(self, request, context):
        pass
    
    def MakeAMove(self, tile):
        pass

    def GetGameBoard(self, request, context):
        if self.game_board:
            return tictactoe_pb2.BoardResponse(board=self.game_board, success=True)
        return tictactoe_pb2.BoardResponse(board=self.game_board, success=False)

    def process_command(self, command):
        m = pattern_set_symbol.match(command)
        if m:
            self.set_symbol(int(m.group(1)),m.group(2))
            return
        m = pattern_list_board.match(command)
        if m:
            self.list_board()
            return
        m = pattern_set_node_time.match(command)
        if m:
            self.set_node_time(m.group(1),m.group(2))
            return
        m = pattern_set_time_out.match(command)
        if m:
            self.set_time_out(m.group(1),float(m.group(2)))
            return
        m = pattern_start_game.match(command)
        if m:
            self.start_game()
            return
        print("Unknown command!")

    def set_symbol(self, position, symbol):
        print("Set symbol",symbol, position)
    
    def list_board(self):
        if self.game_board:
            game_board = self.game_board
        else:
            try:
                with grpc.insecure_channel(self.node2) as channel:
                    stub = tictactoe_pb2_grpc.TicTacToeStub(channel)
                    response = stub.GetGameBoard(tictactoe_pb2.BoardRequest())
                    success = response.success
                    game_board = response.board
            except:
                raise ConnectionError('{} missing'.format(self.node2name))
            if not success:
                try:
                    with grpc.insecure_channel(self.node3) as channel:
                        stub = tictactoe_pb2_grpc.TicTacToeStub(channel)
                        response = stub.GetGameBoard(tictactoe_pb2.BoardRequest())
                        success = response.success
                        game_board = response.board
                except:
                    raise ConnectionError('{} missing'.format(self.node3name))
            if not success:
                print("No board found :(")
                return
        tictactoe.print_board(game_board)
    
    def set_node_time(self, node_name, time):
        print("Set node time",node_name,time)
        if self.name == node_name:
            current_datetime = datetime.utcnow()+timedelta(milliseconds=self.time_diff)
            future_datetime = datetime.combine(current_datetime.date(),datetime.strptime(time,'%H:%M:%S').time())
            self.time_diff = (future_datetime-datetime.utcnow())/timedelta(milliseconds=1)
            print("New UTC time:", datetime.utcnow()+timedelta(milliseconds=self.time_diff))
        elif self.coordinator == self.id:
            if self.node2name == node_name:
                try:
                    with grpc.insecure_channel(self.node2) as channel:
                        stub = tictactoe_pb2_grpc.TicTacToeStub(channel)
                        response = stub.ReceiveTimeString(tictactoe_pb2.SetTimeString(time=time))
                        print(self.node2name,'accepted:', response.time_accepted)
                except:
                    raise ConnectionError('{} missing'.format(self.node2name))
            elif self.node3name == node_name:
                try:
                    with grpc.insecure_channel(self.node3) as channel:
                        stub = tictactoe_pb2_grpc.TicTacToeStub(channel)
                        response = stub.ReceiveTimeString(tictactoe_pb2.SetTimeString(time=time))
                        print(self.node3name,'accepted:', response.time_accepted)
                except:
                    raise ConnectionError('{} missing'.format(self.node3name))
            else:
                print(node_name, "is not a valid node name.")
        else:
            print("Only the game master can change time of other nodes.")

    
    def set_time_out(self, role, time):
        print("Set time-out",role,time)
    
    def start_game(self):
        print("Start game")

    def print_node_name(self):
        print('{}>'.format(self.name),end="")

    def init_game(self):
        self.game_board = tictactoe.blank_board()
    



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

    # Time sync
    servicer.sync_time()

    while servicer.time_diff is None:
        print('{} waiting for time sync...'.format(servicer.name))
        time.sleep(0.25)

    # Leader election
    while not servicer.coordinator:
        servicer.start_election()
        print('Waiting for coordinator to be elected...')
        time.sleep(0.25)

    if servicer.id == servicer.coordinator:
        servicer.init_game()
        print('{} selected as coordinator'.format(servicer.name))

    # Game loop
    print('{} setup completed. Game is ready'.format(servicer.name))
    try:
        while True:
            # TODO: game loop stuff
            user_command = input('{}>'.format(name))
            servicer.process_command(user_command)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    serve()