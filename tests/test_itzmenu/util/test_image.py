import itzmenu.util.image as image


class TestImage:

    def test_bytes_to_sha256(self, week_menu: bytes):
        checksum = image.bytes_to_sha256(week_menu)
        assert checksum == 'c0f2190a1b6536ff868fe2436993e25814c763c98db8068ca4c27ce78dfb68a6'
