"""High‑level robot‑arm command stub.

Replace `_send` with your actual serial / ROS / API call.
"""
import re, threading, time, sys

# Example transport layer -------------------------------------------------
def _send(cmd: str):
    """Send a raw command string to the arm (stubbed)."""
    print(f"[ARM] {cmd}", file=sys.stderr)
    # TODO: serial_port.write(f"{cmd}\n".encode())

# Public API --------------------------------------------------------------
def handle_robot_arm_command(command: str):
    """Parse natural‑language command and forward to the arm driver."""
    cmd_lc = command.lower()

    if "open" in cmd_lc:
        threading.Thread(target=_send, args=("CLAW OPEN",), daemon=True).start()
        return "Claw opened."

    if "close" in cmd_lc:
        threading.Thread(target=_send, args=("CLAW CLOSE",), daemon=True).start()
        return "Claw closed."

    if "move to" in cmd_lc:
        coords = re.findall(r"[-+]?[0-9]*\.?[0-9]+", command)
        if len(coords) == 3:
            threading.Thread(target=_send, args=(f"MOVE {','.join(coords)}",), daemon=True).start()
            return f"Moving arm to {coords}"
        return "Command not recognized: missing coordinates."

    return f"Command not recognized: {command}"