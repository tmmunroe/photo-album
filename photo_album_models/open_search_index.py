
class OpenSearchIndexModel:
    def __init__(self, bucket, objectKey, createdTimestamp, labels):
        self.bucket = bucket
        self.objectKey = objectKey
        self.createdTimestamp = createdTimestamp
        self.labels = labels
    
    @staticmethod
    def from_dict(index_model_dict):
        return OpenSearchIndexModel(
            index_model_dict['bucket'],
            index_model_dict['objectKey'],
            index_model_dict['createdTimestamp'],
            index_model_dict['labels']
        )

    def to_dict(self):
        return {
            'bucket': self.bucket,
            'objectKey': self.objectKey,
            'createdTimestamp': self.createdTimestamp,
            'labels': self.labels
            }
    
    