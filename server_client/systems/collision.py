from phecs import World

from server_client.components import Collider, Position, Velocity


def collision_sys(world: World):
    for entA, posA, velA, colA in world.find(Position, Velocity, Collider):
        colA.x = posA.x
        colA.y = posA.y
        for entB, posB, colB in world.find(Position, Collider):
            if entA == entB:
                continue
            colB.x = posB.x
            colB.y = posB.y
            if colliders_collide(colA, colB):
                centerA_x = colA.x + colA.width / 2
                centerA_y = colA.y + colA.height / 2
                centerB_x = colB.x + colB.width / 2
                centerB_y = colB.y + colB.height / 2

                diff_x = centerA_x - centerB_x
                diff_y = centerA_y - centerB_y

                overlap_x = colA.width / 2 + colB.width / 2 - abs(diff_x)
                overlap_y = colA.height / 2 + colB.height / 2 - abs(diff_y)

                if overlap_x < overlap_y:
                    velA.x *= -1
                    if diff_x > 0:
                        posA.x += overlap_x
                    else:
                        posA.x -= overlap_x
                else:
                    velA.y *= -1
                    if diff_y > 0:
                        posA.y += overlap_y
                    else:
                        posA.y -= overlap_y


def colliders_collide(colA, colB):
    return (
        colA.x < colB.x + colB.width
        and colA.x + colA.width > colB.x
        and colA.y < colB.y + colB.height
        and colA.y + colA.height > colB.y
    )
