from abstractprocessor import AbsProcessor

class SimpleProcessor(AbsProcessor):
    def __init__(self):
        pass

    def process(self, job, data):
        return data

def load():
    return SimpleProcessor()