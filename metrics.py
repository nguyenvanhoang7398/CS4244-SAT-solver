class Metrics(object):
    def __init__(self, sat, exec_time, pick_branching_num, check_clause_status_time):
        self.sat = sat
        self.exec_time = exec_time
        self.pick_branching_num = pick_branching_num
        self.check_clause_status_time = check_clause_status_time
    def __iter__(self):
        yield {
            'sat': self.sat,
            'exec_time': self.exec_time,
            'pick_branching_num': self.pick_branching_num,
            'check_clause_status_time': self.check_clause_status_time
        }.items()