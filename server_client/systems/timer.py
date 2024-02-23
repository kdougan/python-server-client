from phecs import World

from server_client.components import Timer


def timer_sys(world: World, dt: float):
    for ent, timer in world.find(Timer):
        timer.time += dt
        if timer.time > timer.interval:
            timer.callback()
            timer.time = 0
            if not timer.repeat:
                world.remove(ent, Timer)
