import json
import pathlib
import unittest.mock as mock
import pytest
from src.ingest.collectors import v6

FIXTURES = pathlib.Path(__file__).parent / "fixtures"

def _load_fixture(name: str) -> str:
    # Para V6, simulamos el HTML que contiene el script
    raw_data = json.loads((FIXTURES / "v6_response_fragment.json").read_text())
    # Creamos un string que simule el bloque de Next.js que encontramos con regex
    return f'self.__next_f.push([1,"initialVehicle\\":{json.dumps(raw_data).replace('"', '\\"')}\\"specsComplete\\":true"])'

class TestV6Collector:
    """Verifica la extracción de specs técnicas desde el JSON de Next.js."""

    @mock.patch("requests.get")
    def test_v6_search_extracts_tech_specs(self, mock_get):
        # Setup del mock
        mock_resp = mock.Mock()
        mock_resp.status_code = 200
        mock_resp.text = _load_fixture("v6_response_fragment.json")
        mock_get.return_value = mock_resp

        # Ejecución
        results = v6.search("Ford", "Mustang")

        # Verificaciones
        assert len(results) > 0
        res = results[0]
        assert res["source"] == "v6"
        assert res["make"] == "Ford"
        assert res["power_hp"] == 487.0
        assert res["torque_nm"] == 560.0
        assert res["transmission"] == "AT"
        assert res["mileage"] == 15000

    @mock.patch("requests.get")
    def test_v6_handles_api_error(self, mock_get):
        mock_get.side_effect = Exception("Conexión fallida")
        results = v6.search("Ford", "Mustang")
        assert results == []