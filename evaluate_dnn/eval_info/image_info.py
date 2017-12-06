class image_info:
    def __init__(self):
        self.name=''
        self.rank = -1
        self.rank_in_class = -1
        self.prob=-1
        self.top5_labels=[]

    def __str__(self):
        text = '{},{},{},{},'.format(
            self.name,
            self.rank,
            self.rank_in_class,
            self.prob
        )
        
        for label in self.top5_labels:
            text += '{},{},'.format(label[0], label[1])

        text += '\n'
        return text
