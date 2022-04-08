# Detecting idol stars with Amazon Rekognition

## [search_face.py](rekognition/search_face.py)
```
ic| search_face_by_image(image_bytes=image_bytes, collection_id=collection_id, max_matches=max_matches, threshold=threshold): {'Face': {'BoundingBox': {'Height': 0.35677599906921387, 'Left': 0.25514501333236694, 'Top': 0.11943300068378448, 'Width': 0.3492020070552826}, 'Confidence': 99.99979400634766,
'ExternalImageId': 'idol-blackpink-30000699785.jpg', 'FaceId': '9839c593-8514-43c6-b673-10ca7b4e511b', 'ImageId': 'e036a8de-f2b7-30fa-954f-969bb87886db', 'IndexFacesModelVersion': '6.0'}, 'Similarity': 99.95624542236328}
```

## [flask_app](flask_app/)
1. API server in charge of models
2. Basic frontend (When INCLUDE_VIEWS = True)