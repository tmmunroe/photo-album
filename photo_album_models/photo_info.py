
class PhotoInfoModel:
    def __init__(self, url: str, labels: list):
        self.url = url
        self.labels = labels
    
    def format_response(self):
        resp = { "url": self.url }
        if self.labels:
            resp["labels"] = self.labels
        return resp
