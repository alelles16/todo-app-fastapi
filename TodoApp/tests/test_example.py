import pytest

class Student:
    def __init__(self, first_name: str, last_name: str, major: str, years: int):
        self.first_name = first_name
        self.last_name = last_name
        self.major = major
        self.years = years


@pytest.fixture
def student():
    return Student('John', 'Smith', 'Computer Science', 3)


def test_person_init(student):
    assert student.first_name == 'John', 'First name should be John'
    assert student.last_name == 'Smith', 'Last name should be Smith'
    assert student.major == 'Computer Science', 'Major should be Computer Science'
    assert student.years == 3, 'Years should be 3'
