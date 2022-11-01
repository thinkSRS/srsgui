from rga import RGA100


def get_rga(task) -> RGA100:
    return task.get_instrument('dut').rga
