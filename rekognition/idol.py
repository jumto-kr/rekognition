from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional, ClassVar, Any

REKOGNITION_EXTERNAL_IMAGE_ID_REGEX = re.compile(r'[a-zA-Z0-9_.\-:]+')


@dataclass(frozen=True)
class Idol:
    idol_id: str
    image_s3_bucket_name: str
    image_s3_object_key: str
    image_id: Optional[str] = None
    face_id: Optional[str] = None

    EXTERNAL_IMAGE_ID_SEPARATOR: ClassVar[str] = ':SEP:'
    EXTERNAL_IMAGE_ID_DIRECTORY_SEPARATOR: ClassVar[str] = ':DIR:'
    EXTERNAL_IMAGE_ID_PERCENT: ClassVar[str] = ':PER:'
    EXTERNAL_IMAGE_ID_TILDE: ClassVar[str] = ':TILDE:'
    KEYS_FOR_EXTERNAL_IMAGE_ID: ClassVar[tuple[str]] = ('idol_id', 'image_s3_bucket_name', 'image_s3_object_key')

    @classmethod
    def from_external_image_id(cls, external_image_id: str, image_id: Optional[str] = None, face_id: Optional[str] = None) -> Idol:
        assert cls.EXTERNAL_IMAGE_ID_SEPARATOR in external_image_id
        splited = external_image_id.split(cls.EXTERNAL_IMAGE_ID_SEPARATOR)
        assert len(splited) == len(cls.KEYS_FOR_EXTERNAL_IMAGE_ID)
        return cls(**dict(zip(cls.KEYS_FOR_EXTERNAL_IMAGE_ID, splited)), image_id=image_id, face_id=face_id)

    CONFIDENCE_THRESHOLD: ClassVar[float] = 90.
    @classmethod
    def from_face_dict_aws(cls, face_dict: dict[str, Any]) -> Idol:
        assert face_dict.get('Confidence') > cls.CONFIDENCE_THRESHOLD
        idol = Idol.from_external_image_id(external_image_id=face_dict['ExternalImageId'], image_id=face_dict.get('ImageId'), face_id=face_dict.get('FaceId'))
        return idol

    def to_external_image_id(self) -> str:
        clauses = [getattr(self, key) for key in self.KEYS_FOR_EXTERNAL_IMAGE_ID]
        replacing_plans = [
            ('/', self.EXTERNAL_IMAGE_ID_DIRECTORY_SEPARATOR),
            ('%', self.EXTERNAL_IMAGE_ID_PERCENT),
            ('~', self.EXTERNAL_IMAGE_ID_TILDE)
        ]
        def encode(clause: str) -> str:
            for from_str, to_str in replacing_plans:
                clause = clause.replace(from_str, to_str)
            return clause
        clauses = list(map(encode, clauses))
        external_image_id = self.EXTERNAL_IMAGE_ID_SEPARATOR.join(clauses)
        assert REKOGNITION_EXTERNAL_IMAGE_ID_REGEX.fullmatch(external_image_id), f'{external_image_id} does not match {REKOGNITION_EXTERNAL_IMAGE_ID_REGEX.pattern}'
        return external_image_id
