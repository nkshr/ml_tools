class image_info:
    def __init__(self):
        self.name=''
        self.rank = -1
        self.rank_in_class = -1
        self.prob=-1
        self.top5=[[-1, -1] for i in range(5)]
