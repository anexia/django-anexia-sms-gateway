from unittest.mock import Mock, patch

from django.test import TestCase, override_settings
from requests import HTTPError

from django_anexia_sms_gateway.sms import send_sms

DEFAULT_URL = "https://engine.anexia-it.com/api/sms/v1/message.json"


def build_response(content=b'{"id": 42}', json_value=None):
    """A stand-in for the requests.Response returned by the gateway."""
    response = Mock()
    response.content = content
    response.json.return_value = json_value if json_value is not None else {"id": 42}
    return response


class SendSmsTestCase(TestCase):
    """Tests for `send_sms`, with the gateway call itself mocked out."""

    def test_does_nothing_while_inactive(self):
        """
        No settings at all means ASGW_ACTIVE defaults to False: the gateway must
        not be called, so an unconfigured project never sends real messages.
        """
        with patch("django_anexia_sms_gateway.sms.request") as request:
            result = send_sms("hello", "+436641234567")

        request.assert_not_called()
        self.assertIsNone(result)

    @override_settings(ASGW_ACTIVE=True, ASGW_API_TOKEN="secret-token")
    def test_sends_message_with_defaults(self):
        """An active gateway posts to the default URL with GSM encoding."""
        response = build_response()

        with patch(
            "django_anexia_sms_gateway.sms.request",
            return_value=response,
        ) as request:
            result = send_sms("hello", "+436641234567")

        request.assert_called_once_with(
            method="POST",
            url=DEFAULT_URL,
            headers={
                "Authorization": "Token secret-token",
                "Content-Type": "application/json",
            },
            json={
                "destination": "+436641234567",
                "message": "hello",
                "encoding": "GSM",
            },
        )
        response.raise_for_status.assert_called_once()
        self.assertEqual(result, {"id": 42})

    @override_settings(
        ASGW_ACTIVE=True,
        ASGW_API_TOKEN="secret-token",
        ASGW_ENCODING="UTF8",
        ASGW_SINGLE_MESSAGE_URL="https://example.test/api/sms/v1/message.json",
    )
    def test_honours_url_and_encoding_overrides(self):
        """ASGW_SINGLE_MESSAGE_URL and ASGW_ENCODING override the defaults."""
        with patch(
            "django_anexia_sms_gateway.sms.request",
            return_value=build_response(),
        ) as request:
            send_sms("hällo", "+436641234567")

        _, kwargs = request.call_args
        self.assertEqual(kwargs["url"], "https://example.test/api/sms/v1/message.json")
        self.assertEqual(kwargs["json"]["encoding"], "UTF8")

    @override_settings(ASGW_ACTIVE=True, ASGW_API_TOKEN="secret-token")
    def test_returns_none_on_empty_response_body(self):
        """A 2xx with no body yields None rather than a JSON decode error."""
        response = build_response(content=b"")

        with patch("django_anexia_sms_gateway.sms.request", return_value=response):
            result = send_sms("hello", "+436641234567")

        self.assertIsNone(result)
        response.json.assert_not_called()

    @override_settings(ASGW_ACTIVE=True, ASGW_API_TOKEN="secret-token")
    def test_propagates_gateway_errors(self):
        """raise_for_status is called, so gateway failures reach the caller."""
        response = build_response()
        response.raise_for_status.side_effect = HTTPError("400 Client Error")

        with patch("django_anexia_sms_gateway.sms.request", return_value=response):
            with self.assertRaises(HTTPError):
                send_sms("hello", "+436641234567")
