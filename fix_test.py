import re

with open("tests/tools/test_verify_images.py", "r") as f:
    content = f.read()

content = content.replace("mocker.patch('src.tools.verify_images.requests.get')", "mocker.patch('src.tools.verify_images.requests.get')")
