class image_info:
    def __init__(self):
        self.name=''
        self.rank = -1
        self.rank_in_class = -1
        self.prob=-1
        self.top5=[{'class_id' : -1, 'prob' : -1} for i in range(5)] #class_id, prob
