import cv2
import numpy as np
import requests

dvr_address = 'http://10.201.2.244'
dvr_port = 8090
top_oid = 3
side_oid = 4
top_scale = 10.8
side_scale = 12.7
cams = { #oid, scale
    't_side': (1, 1),
    'a_top': (3, 10.8),
    'a_side': (4, 12.7)
}

class Cam:
    def __init__(self, side):
        self.oid, self.scale = cams[side]

    def getPhoto(self):
        resp = requests.request('GET', f'{dvr_address}:{dvr_port}/photo.jpg?oid={self.oid}')
        nar = np.fromstring(resp.content, np.uint8)
        return cv2.imdecode(nar, cv2.IMREAD_GRAYSCALE)