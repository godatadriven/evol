from pytest import fixture


@fixture(scope='function')
def readme_code() -> str:
    content = []
    in_code_block = False
    with open('../README.md') as readme_file:
        for line in readme_file.readlines():
            if in_code_block:
                if line == '```\n':
                    in_code_block = False
                    return ''.join(content)
                else:
                    content.append(line)
            elif line == '```python\n':
                in_code_block = True


def test_readme(readme_code):
    exec(readme_code, globals())
