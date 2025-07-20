"""Launcher fixing API key fallback."""
import sys, os, traceback, pprint, pathlib

from gui_main_window import WALDOApp
from camera_calibration import camera_calibration
from ai_interface_router import InterfaceAIRouter
from my_interface_ai_handler import InterfaceAI
from config_utils import load_config, CONFIG_PATH   # CONFIG_PATH comes from the helper

# ──────────────────────────────────────────────────────────────────────────────
def main():
    demo = "--demo" in sys.argv
    cfg = load_config()          # 1️⃣  cfg now exists

    # DEBUG print ­– shows exactly what was loaded
    print("[DEBUG] Config file used →", CONFIG_PATH)
    pprint.pp(cfg)
    # ──────────────────────────────────────────────────────────────────────────

    # Fallback: put key into the env if it isn’t there already
    if not os.getenv("OPENAI_API_KEY"):
        key = cfg.get("interface_apikey") or cfg.get("apikey_0")
        if key:
            os.environ["OPENAI_API_KEY"] = key

    if demo:
        os.environ["OPENAI_API_KEY"] = "sk-demo-placeholder"

    try:
        interface_ai = InterfaceAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            model=cfg.get("interface_model") or cfg.get("model_0"),
            endpoint=cfg.get("llava_endpoint_0"),
        )

        app = WALDOApp(None)
        router = InterfaceAIRouter(interface_ai, cfg, camera_calibration, app=app)
        app.router = router
        app.mainloop()

    except Exception as e:
        print(f"[FATAL] {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()
