from pathlib import Path
import yaml

BASE_DIR      = Path(__file__).resolve().parent.parent
PROMOS_PATH = BASE_DIR / "data" / "promos.yml"

def cargar_promos(path: Path = PROMOS_PATH) -> dict:
    with path.open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)
    
def get_servicio(serv_id: str) -> dict | None:
    catalogo = cargar_promos()
    for s in catalogo["fisioterapia"]:
        if s["id"] == serv_id:
            return s
    return None