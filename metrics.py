class Metrics(object):
    def __init__(self, sat, exec_time, pick_branching_num):
        self.sat = sat
        self.exec_time = exec_time
        self.pick_branching_num = pick_branching_num
    def __iter__(self):
        yield {
            'sat': self.sat,
            'exec_time': self.exec_time,
            'pick_branching_num': self.pick_branching_num
        }.items()