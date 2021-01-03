import logging
import gameroom as gr
import networking as nw
import msgcreation as mc
import traceback

class RoomNotExistsException(Exception):
    pass

def handle_ChatMessageReq(resources, sender_conn, msg):
    try:
        rooms = resources['rooms']
        if msg['room_code'] not in rooms:
            raise RoomNotExistsException()

        room = rooms[msg['room_code']]
        with room.lock:
            room.handle_ChatMessageReq(msg, sender_conn)

    except:
        logging.error(
            '[handle_ChatMessageReq] Room with code {} not found'.format(msg.room_code))


def handle_CreateRoomReq(resources, sender_conn, msg):
    try:
        rooms = resources['rooms']
        room_code = mc.generate_unique_code(8, rooms)
        room = gr.Room(msg['user_name'], sender_conn, room_code)

        resp = mc.build_ok_create_room_resp(room_code)
        rooms[room_code] = room
        sender_conn.send(resp)

        logging.debug(
            '[handle_CreateRoomReq] Created new room with room code {}'.format(room_code))

    except:
        logging.error(
            '[handle_CreateRoomReq] Error ocured when handling message {}'.format(msg))

        resp = mc.build_not_ok_create_room_resp()
        sender_conn.send(resp)

def handle_JoinRoomReq(resources, sender_conn, msg):
    try:
        rooms = resources['rooms']
        if msg['room_code'] not in rooms:
            raise RoomNotExistsException()

        room = rooms[msg['room_code']]

        with room.lock:
            room.handle_JoinRoomReq(msg, sender_conn)

    except RoomNotExistsException:
        info = 'Room with code {} not found'.format(msg['room_code'])
        nw.send_NOT_OK_JoinRoomResp_with_info(sender_conn, info)

    except:
        logging.error('[handle_JoinRoomReq] Error occurred when handling message{}'.format(msg))
        resp = mc.build_not_ok_join_room_resp()
        sender_conn.send(resp)


def handle_ExitClientReq(resources, sender_conn, msg):
    try:
        code = msg['room_code']
        rooms = resources['rooms']
        room = rooms[code]

        with room.lock:
            room.handle_ExitClientReq(msg, sender_conn)

        if room.num_of_members() == 0:
            del rooms[code]
            logging.info('[handle_ExitClientReq] Room with code {} deleted (0 players)'.format(code))
            
    except:
        logging.error('[handle_ExitClientReq] Error ocured when handling message {}'.format(msg))


def handle_StartGameReq(resources, sender_conn, msg):
    try:
        user_name = msg['user_name']
        room_code = msg['room_code']

        rooms = resources['rooms']
        room = rooms[room_code]

        with room.lock:
            room.start_game(user_name)

            resp = mc.build_start_game_resp_ok()
            sender_conn.send(resp)

            artist, words_to_select = room.enter_word_selection_state()

            start_game_bc = {'msg_name': 'StartGameBc', 'artist': artist}
            room.broadcast_message(start_game_bc)

    except gr.StartedNotByOwnerException:
        resp = mc.build_start_game_resp_not_ok('Only room owner can start the game!')
        sender_conn.send(resp)
    
    except gr.NotEnaughPlayersException:
        resp = mc.build_start_game_resp_not_ok('There must be at least 2 players to start the game!')
        sender_conn.send(resp)
    
    except:
        logging.error('[handle_StartGameReq] Error ocured when handling message {}'.format(msg))
        resp = mc.build_start_game_resp_not_ok()
        sender_conn.send(resp)
