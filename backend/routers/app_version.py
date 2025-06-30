from fastapi import APIRouter
from setuptools_scm import get_version

router = APIRouter()
@router.get(
    "/",
    summary="Get App Version"
)
def get_app_version():
    return get_version(version_scheme="no-guess-dev")