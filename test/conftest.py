import pytest
import os

@pytest.hookimpl()
def pytest_sessionfinish(session, exitstatus):
    for file in ["tst.json", "tst_type_error.json", "tst_bad_json.json"]:
        if os.path.isfile(file):
            os.remove(file)
    
