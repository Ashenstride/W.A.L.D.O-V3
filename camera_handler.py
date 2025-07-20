import cv2
import base64
from openai import OpenAI

class CameraAI:
    def __init__(self, cam_id, model, api_key, endpoint):
        self.cam_id = cam_id
        self.model = model
        self.api_key = api_key
        self.endpoint = endpoint
        self.client = OpenAI(api_key=api_key, base_url=endpoint)

    def query(self, prompt, image=None):
        frame = image
        if frame is None:
            return f"[Camera {self.cam_id}] No image available."
        _, buffer = cv2.imencode('.jpg', frame)
        img_b64 = base64.b64encode(buffer).decode()

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{img_b64}"}}
                ]
            }
        ]

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=300,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"[Camera {self.cam_id}] Error: {e}"

def get_active_camera_ais(config_data):
    # Build for as many cameras as you want
    camera_ais = {}
    # Example for 4 cameras (indices 0,1,2,3)
    for cam_id in range(4):
        # Only build if a config exists for this cam_id
        if f"model_{cam_id}" in config_data and f"apikey_{cam_id}" in config_data and f"llava_endpoint_{cam_id}" in config_data:
            ai = CameraAI(
                cam_id=cam_id,
                model=config_data.get(f"model_{cam_id}"),
                api_key=config_data.get(f"apikey_{cam_id}"),
                endpoint=config_data.get(f"llava_endpoint_{cam_id}")
            )
            camera_ais[cam_id] = ai
    return camera_ais
