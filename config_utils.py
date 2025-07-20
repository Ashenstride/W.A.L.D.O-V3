import json, os, pathlib, importlib

# -----------------------------------------------------------------------------
# Resolve a writable config directory
# -----------------------------------------------------------------------------
def _default_config_dir() -> pathlib.Path:
    """Return a user‑specific config folder, preferring platformdirs if present."""
    try:
        # Import only if the module exists (avoids hard dependency)
        spec = importlib.util.find_spec("platformdirs")
        if spec:
            from platformdirs import user_config_dir
            return pathlib.Path(user_config_dir("WALDO"))
    except Exception:
        pass  # any error → fallback to home

    return pathlib.Path.home() / ".waldo"

_CFG_DIR = _default_config_dir()
_CFG_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_PATH = _CFG_DIR / "waldo_config.json"

# -----------------------------------------------------------------------------
def _load(path: pathlib.Path):
    if path and path.exists():
        with open(path, "r") as f:
            return json.load(f)
    return None

def load_config():
    """Look for a config file in three locations, return {} if none found."""
    # 1. Preferred user directory
    cfg = _load(CONFIG_PATH)
    if cfg is not None:
        return cfg

    # 2. Path set in env var
    env_path = os.getenv("WALDO_CONFIG_PATH")
    cfg = _load(pathlib.Path(env_path) if env_path else None)
    if cfg is not None:
        return cfg

    # 3. waldo_config.json in current working directory
    cfg = _load(pathlib.Path.cwd() / "waldo_config.json")
    return cfg or {}

def save_config(cfg: dict):
    _CFG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)
