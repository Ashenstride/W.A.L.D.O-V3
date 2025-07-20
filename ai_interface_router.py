from camera_handler import get_active_camera_ais
from triangulation import triangulate_3d_position
from robot_arm_controller import handle_robot_arm_command
from dictionary import CAMERA_KEYWORDS, TRIANGULATION_KEYWORDS, ARM_KEYWORDS
import re

class InterfaceAIRouter:
    """Routes user prompts to either the interface LLM or camera AIs and injects
    per‑instance personality / role prompts from the WALDO config."""

    def __init__(self, interface_ai_instance, config_data, camera_calibration, app):
        self.interface_ai = interface_ai_instance
        self.config_data = config_data
        self.camera_calibration = camera_calibration
        self.app = app  # WALDOApp instance (for live frames)
        self.conversation_history = []

    # ---------------------------------------------------------------------
    def process_prompt(self, prompt: str):
        prompt_lc = prompt.lower()
        camera_ais = get_active_camera_ais(self.config_data)

        # Try to pick a camera explicitly mentioned (by index or name) --------
        cam_id = 0
        for idx in camera_ais:
            name = self.config_data.get(f"camera_name_{idx}", f"camera {idx+1}").lower()
            if f"camera {idx+1}" in prompt_lc or name in prompt_lc:
                cam_id = idx
                break

        # 1. CAMERA routing --------------------------------------------------
        if any(word in prompt_lc for word in CAMERA_KEYWORDS):
            if cam_id in camera_ais:
                frame = self.app.latest_frames.get(cam_id)
                if frame is not None:
                    camera_answer = camera_ais[cam_id].query(prompt, image=frame)
                    self._remember(prompt, camera_answer)
                    return camera_answer
                return "[Error: Could not capture camera frame.]"
            return "[Error: No camera available.]"

        # 2. TRIANGULATION ---------------------------------------------------
        elif any(word in prompt_lc for word in TRIANGULATION_KEYWORDS):
            object_name = prompt
            pixel_coords = {}
            for cam_id, cam_ai in camera_ais.items():
                frame = self.app.latest_frames.get(cam_id)
                reply = cam_ai.query(f"Locate the {object_name}. Give only x,y pixel coordinates.", image=frame)
                try:
                    pixel_coords[cam_id] = self._parse_coords(reply)
                except ValueError:
                    pixel_coords[cam_id] = None
            world_pos = triangulate_3d_position(self.camera_calibration, pixel_coords)
            self._remember(prompt, str(world_pos))
            return f"The estimated world position vector is: {world_pos}"

        # 3. ROBOT ARM -------------------------------------------------------
        elif any(word in prompt_lc for word in ARM_KEYWORDS):
            arm_result = handle_robot_arm_command(prompt)
            self._remember(prompt, arm_result)
            return f"[Robot Arm]: {arm_result}"

        # 4. GENERAL LLM -----------------------------------------------------
        personality = self.config_data.get("interface_personality", "")
        roles = self.config_data.get("interface_roles", "")
        personality_block = f"Personality: {personality}. " if personality else ""
        roles_block = f"Roles: {roles}. " if roles else ""

        system_message = {
            "role": "system",
            "content": (
                f"{personality_block}{roles_block}"
                "You are a multimodal robot AI with access to three tools: "
                "1. CAMERA, which can answer visual questions about any camera's live feed (use: CALL_CAMERA('prompt')). "
                "2. TRIANGULATE, which can estimate 3D object positions using multiple cameras (use: CALL_TRIANGULATE('object name')). "
                "3. ARM, which can operate the robot arm and end effector (use: CALL_ARM('command')). "
                "If you use any tool, I will run it and insert the result as TOOL_RESULT. "
                "Otherwise, answer the user directly. Be natural, concise, and show some personality!"
            )
        }

        messages = [system_message] + self.conversation_history + [{"role": "user", "content": prompt}]
        reply = self.interface_ai.chat(messages)
        if isinstance(reply, dict):  # safeguard
            reply = reply.get("content", str(reply))
        self._remember(prompt, reply)
        return reply

    # ---------------------------------------------------------------------
    def _parse_coords(self, reply: str):
        matches = re.findall(r"(\d+)", reply)
        if len(matches) >= 2:
            return int(matches[0]), int(matches[1])
        raise ValueError("No coordinates found.")

    def _remember(self, user_msg: str, ai_msg: str):
        """Append to shared history for better conversation context."""
        self.conversation_history.append({"role": "user", "content": user_msg})
        self.conversation_history.append({"role": "assistant", "content": ai_msg})
