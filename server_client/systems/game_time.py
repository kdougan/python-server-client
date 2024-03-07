import time

from server_client.mod import GameClient
from server_client.types import ServerTimeRequest, ClientState, ServerState


def game_time_sys(state: ClientState | ServerState, client: GameClient | None = None):
    state.game_clock += state.dt

    if (
        isinstance(state, ClientState)
        and client
        and time.time() - state.last_sync > 5.0
    ):
        state.last_sync = time.time()
        client.send_message(bytes(ServerTimeRequest()))
