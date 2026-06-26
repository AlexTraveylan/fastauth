from faker import Faker

from fastauth.models.schemas import GoogleUserInfo

fake = Faker()


class TestGoogleUserInfo:
    def test_accepts_minimal_payload_without_names(self) -> None:
        # Given
        email = fake.email()
        sub = fake.uuid4()

        # When
        info = GoogleUserInfo(email=email, sub=sub)

        # Then
        assert info.given_name is None
        assert info.family_name is None
        assert info.name is None
        assert info.email_verified is False

    def test_keeps_given_name_when_provided(self) -> None:
        # Given
        given_name = fake.first_name()

        # When
        info = GoogleUserInfo(email=fake.email(), sub=fake.uuid4(), given_name=given_name)

        # Then
        assert info.given_name == given_name
