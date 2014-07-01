from unittest import TestCase
from nose.plugins.attrib import attr
from extapi.citkeys import CitKeys
from factory.enginefactory import EngineFactory
from bo.datarequest import DataRequest
from forecastio import load_forecast
from extapi.dataresponsebuilder import DataResponseBuilder
from bo import precipitationtype


@attr("integration")
class TestIntegrationEngine(TestCase):
    def setUp(self):
        key_retriever = CitKeys()
        self.api_key = key_retriever.key()
        self.data_retriever = EngineFactory.create_data_retriever(key_retriever)

    def _call_api_directly(self, lat, lng):
        datapoint = load_forecast(self.api_key, lat, lng).currently()
        result = {
            "summary": datapoint.summary,
            "precipIntensity": datapoint.precipIntensity,
            "precipProbability": datapoint.precipProbability,
            "precipType": None
        }
        if datapoint.precipIntensity > 0:
            result["precipType"] = datapoint.precipType
        return result

    def _validate_api_call(self, latitude, longitude):
        response = self.data_retriever.retrieve(DataRequest(latitude, longitude))
        api_response = self._call_api_directly(latitude, longitude)

        self.assertEquals(api_response["summary"], response.summary_str)
        self.assertEquals(
            DataResponseBuilder.intensity_type(api_response["precipIntensity"]),
            response.intensity
        )
        self.assertEquals(
            api_response["precipProbability"] * 100,
            response.pop_percent
        )
        if not api_response["precipType"]:
            self.assertEquals(precipitationtype.NONE, response.precipitation)
        else:
            self.assertEquals(
                DataResponseBuilder.precipitation_type_from_str(api_response["precipType"]),
                response.precipitation
            )

    def test_retrieves_correct_data_for_hialeah_33012(self):
        self._validate_api_call(25.86, -80.30)

    def test_retrieves_correct_data_for_lax_90045(self):
        self._validate_api_call(33.96, -118.39)
