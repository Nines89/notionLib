import keyring

SERVICE = "NotionAutomation"

def save_key(profile_name: str, api_key: str):
    keyring.set_password(SERVICE, profile_name, api_key)

def get_key(profile_name: str) -> str | None:
    return keyring.get_password(SERVICE, profile_name)

def delete_key(profile_name: str):
    try:
        keyring.delete_password(SERVICE, profile_name)
    except keyring.errors.PasswordDeleteError:
        pass

def list_profiles() -> list[str]:
    """
    keyring non espone un'API nativa per listare le credenziali.
    Usiamo un file JSON locale solo per i NOMI dei profili (non le chiavi).
    """
    import json, pathlib
    path = _profiles_path()
    if path.exists():
        return json.loads(path.read_text())
    return []

def save_profile_name(profile_name: str):
    import json, pathlib
    profiles = list_profiles()
    if profile_name not in profiles:
        profiles.append(profile_name)
        _profiles_path().write_text(json.dumps(profiles))

def remove_profile_name(profile_name: str):
    import json
    profiles = [p for p in list_profiles() if p != profile_name]
    _profiles_path().write_text(json.dumps(profiles))

def _profiles_path():
    import pathlib
    return pathlib.Path.home() / ".notion_automation_profiles.json"