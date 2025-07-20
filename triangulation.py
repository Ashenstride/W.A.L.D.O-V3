import numpy as np

def triangulate_3d_position(camera_calibration: dict, pixel_coords: dict):
    """Simple two‑camera triangulation with basic sanity checks.

    Args:
        camera_calibration: mapping cam_id -> calibration dict (pos, focal_length, cx, cy).
        pixel_coords: mapping cam_id -> (x, y) pixel tuples OR None for invalid.

    Returns:
        World-space (X, Y, Z) list rounded to 2 dp, or str with error.
    """
    # Filter out invalid results first
    valid = {cid: pt for cid, pt in pixel_coords.items() if pt}
    if len(valid) < 2:
        return "Need two good camera views."

    cam_ids = list(valid.keys())[:2]
    cam1, cam2 = cam_ids
    (x1, y1), (x2, y2) = valid[cam1], valid[cam2]

    cam1_info = camera_calibration[cam1]
    cam2_info = camera_calibration[cam2]

    baseline = np.linalg.norm(np.array(cam1_info['pos']) - np.array(cam2_info['pos']))  # metres
    f = cam1_info.get('focal_length', 1000)  # pixels
    cx = cam1_info.get('cx', 320)
    cy = cam1_info.get('cy', 240)

    disparity = abs(x1 - x2)
    if disparity < 1:  # too small → unreliable depth
        return "Disparity too small for reliable depth."

    Z = f * baseline / disparity
    X = (x1 - cx) * Z / f
    Y = (y1 - cy) * Z / f
    return [round(float(X), 2), round(float(Y), 2), round(float(Z), 2)]