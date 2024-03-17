import itz_menu.utils as utils


class TestUtils:

    def test_bytes_to_sha256(self, week_menu: bytes):
        checksum = utils.bytes_to_sha256(week_menu)
        assert checksum == 'c0f2190a1b6536ff868fe2436993e25814c763c98db8068ca4c27ce78dfb68a6'

    def test_timestamp_to_date(self):
        date = utils.timestamp_to_date(1710691628)
        assert date == '17.03.2024'

    def test_is_test_running(self):
        assert utils.is_test_running()
