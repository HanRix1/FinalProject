import pytest

from auth.repository import UserRepository

@pytest.fixture
def get_session():
    ...

@pytest.fixture
def user_repo(session):
    return UserRepository(session)

@pytest.mark.usefixtures("client")
class Test:

    @pytest.fixture(autouse=True)
    def set_up(self, client, user_repo):
        self.user_repo = user_repo
        self.client = client


    # def test
