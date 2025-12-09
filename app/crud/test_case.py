from .base import CRUDBase
from app.models.test_case import TestCase

class CRUDTestCase(CRUDBase):
    pass


crud_test_case = CRUDTestCase(TestCase, 'id_test_case')