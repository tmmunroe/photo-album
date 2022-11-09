from photo_album_models.photo import PhotoModel

class SearchResponseModel:
    def __init__(self, photos=None):
        self._photos = photos if photos else []
    
    def add_photo(self, photo: PhotoModel):
        self._photos.append(photo)

    def format_response(self):
        return {
            "results": [ photo.format_response() for photo in self._photos ]
        }
