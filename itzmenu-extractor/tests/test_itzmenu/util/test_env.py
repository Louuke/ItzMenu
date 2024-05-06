from itzmenu.util import env


class TestEnv:

    def test_is_test_running(self):
        assert env.is_running_tests()
