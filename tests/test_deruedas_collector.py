import unittest.mock as mock
from src.ingest.collectors import deruedas

class TestDeRuedasCollector:
    """Verifica el scraping de microdatos y boxes de equipamiento."""

    @mock.patch("requests.get")
    def test_deruedas_mapping(self, mock_get):
        # Simulamos un pedazo del HTML de DeRuedas que vimos antes
        html_content = """
        <meta itemprop="brand" content="Hyundai" />
        <meta itemprop="model" content="HB20" />
        <meta itemprop="price" content="31500000" />
        <div class="box-destacado">Motor<br><b>1.6 lts</b></div>
        <div class="box-destacado">Potencia<br><b>126 cv</b></div>
        """
        mock_resp = mock.Mock()
        mock_resp.status_code = 200
        mock_resp.text = html_content
        mock_get.return_value = mock_resp

        # Aquí probamos la función de detalle (la que realmente tiene la info para tasar)
        res = deruedas._scrape_detail("https://www.deruedas.com.ar/test?cod=123")

        assert res["make"] == "Hyundai"
        assert res["price_value"] == 31500000.0
        assert "1.6 lts" in res["engine"]
        assert res["power_hp"] == 126.0