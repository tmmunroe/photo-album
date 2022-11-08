from photo_album_models.photo_info import PhotoInfoModel

class SearchResponseModel:
    def __init__(self, photo_infos=None):
        self._photo_infos = photo_infos if photo_infos else []
    
    def add_photo_info(self, photo_info: PhotoInfoModel):
        self._photo_infos.append(photo_info)

    def format_response(self):
        return {
            "results": [ info.format_response() for info in self._photo_infos ]
        }
