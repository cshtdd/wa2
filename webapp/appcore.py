from flask import jsonify
from flask import abort
from wa.factory.apifactory import ApiFactory
from wa.factory.enginefactory import EngineFactory
from wa.api.freeforall import FreeForAll
from wa.extapi.citkeys import CitKeys


class AppCore(object):
    def __init__(self):
        self.disable_debug = False

    def retrieve_data_test(self, api_key, latitude_str, longitude_str):
        if self._disable_debug():
            self._abort_wrapper(404)
            return
        result = ApiFactory.create_dummy_response(float(latitude_str), float(longitude_str))
        return self._jsonify_wrapper(result.__dict__)

    def _abort_wrapper(self, response_code):
        abort(response_code)

    def _jsonify_wrapper(self, value):
        return jsonify(value)

    def _disable_debug(self):
        def _disable_uwsgi_debug():
            try:
                from uwsgi import opt
                return "true" == opt["disable_debug"].decode()  # pragma: no cover
            except:
                return False
        return self.disable_debug or _disable_uwsgi_debug()

    def retrieve_data_staging(self, api_key, latitude_str, longitude_str):
        if self._disable_debug():
            self._abort_wrapper(404)
            return
        key_validator = FreeForAll()
        api_key_reader = CitKeys()
        return self._retrieve_data_json(
            api_key, latitude_str, longitude_str, key_validator, api_key_reader
        )

    def retrieve_data_production(self, api_key, latitude_str, longitude_str):
        return self._retrieve_data_json(api_key, latitude_str, longitude_str)

    def _retrieve_data_json(
            self, api_key, latitude_str, longitude_str, key_validator=None, api_key_reader=None
    ):
        api_response = AppCore._retrieve_data(
            api_key, latitude_str, longitude_str, key_validator, api_key_reader
        )
        return self._jsonify_wrapper(api_response.__dict__)

    @staticmethod
    def _retrieve_data(
            api_key, latitude_str, longitude_str, key_validator, api_key_reader
    ):
        data_retriever_controller = AppCore._create_controller(key_validator, api_key_reader)
        return data_retriever_controller.get(api_key, latitude_str, longitude_str)

    @staticmethod
    def _create_controller(key_validator, api_key_reader):
        data_retriever = EngineFactory.create_data_retriever(api_key_reader)
        return ApiFactory.create_data_retriever_controller(data_retriever, key_validator)
