# from appsec_secrets import Conjur
# from unittest import mock
#
#
# @mock.patch("scripts.appsec_secrets.TheLogs.function_exception")
# @mock.patch("scripts.appsec_secrets.TheLogs.log_info")
# @mock.patch("scripts.appsec_secrets.requests.request")
# @mock.patch.object(Conjur, "set_environment_variables")
# @mock.patch.object(Conjur, "set_conjur_secrets")
# @mock.patch.object(Conjur, "get_auth_token")
# def test_conjur(get_auth_token_mock, set_conjur_secrets_mock, set_environment_variables_mock,
#                 request_mock, log_info_mock, function_exception_mock):
#     conjur = Conjur('')
#     get_auth_token_mock.assert_called_once()
#     set_conjur_secrets_mock.assert_called_once()
#     set_environment_variables_mock.assert_called_once()
#
#
# @mock.patch("scripts.appsec_secrets.TheLogs.log_info")
# @mock.patch("scripts.appsec_secrets.requests.request")
# def test_conjur_get_auth_token(request_mock, log_info_mock, monkeypatch):
#     monkeypatch.setenv('CONJUR_API_KEY', 'unit_test')
#     conjur = Conjur('', set_env=False)
#     request_mock.assert_called_once()
#
#
# @mock.patch("scripts.appsec_secrets.TheLogs.function_exception")
# @mock.patch("scripts.appsec_secrets.TheLogs.log_info")
# @mock.patch("scripts.appsec_secrets.requests.request", side_effect=Exception)
# def test_conjur_get_auth_token_exception(request_mock, log_info_mock, function_exception_mock,
#                                          monkeypatch):
#     monkeypatch.setenv('CONJUR_API_KEY', 'unit_test')
#     conjur = Conjur('', set_env=False)
#     function_exception_mock.assert_called_once()
#
#
# @mock.patch("scripts.appsec_secrets.TheLogs.function_exception")
# @mock.patch("scripts.appsec_secrets.TheLogs.log_info")
# @mock.patch("scripts.appsec_secrets.requests.request")
# def test_conjur_set_environment_variables(request_mock, log_info_mock, function_exception_mock):
#     conjur = Conjur('', set_env=True)
#     response_mock = mock.MagicMock()
#     response_mock.text = 'text'
#     request_mock.return_value = response_mock
#     conjur.set_conjur_secrets()
#     assert request_mock.call_count == len(conjur.conjur_secrets) + 2
#
#
# @mock.patch("scripts.appsec_secrets.TheLogs.function_exception")
# @mock.patch("scripts.appsec_secrets.TheLogs.log_info")
# @mock.patch("scripts.appsec_secrets.requests.request")
# @mock.patch("os.environ.get", return_value=['test' * 59])
# def test_set_environment_variables(os_get_mock, request_mock, log_info_mock,
#                                    function_exception_mock):
#     conjur = Conjur('')
#     # Sometimes an extra call is done when running the test individually.
#     env_variable_count = len(conjur.env_variables)
#     assert os_get_mock.call_count in (env_variable_count, env_variable_count + 1)
