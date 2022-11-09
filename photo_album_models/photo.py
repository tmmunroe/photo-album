
class PhotoModel:
    def __init__(self, base64Encoding:str):
        self.base64Encoding = base64Encoding
    
    def format_response(self):
        return self.base64Encoding
