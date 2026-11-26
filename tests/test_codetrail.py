import json
import subprocess
import pytest
from typer.testing import CliRunner
from codetrail import core
from codetrail.cli import app

@pytest.fixture
def repo(tmp_path):
    def git(*args):
        subprocess.run(['git','-C',str(tmp_path),*args],check=True,capture_output=True)
    git('init')
    (tmp_path/'README.md').write_text('# Synthetic project',encoding='utf-8')
    (tmp_path/'main.py').write_text('import math\n\ndef compute():\n    raise RuntimeError("never execute this")\n',encoding='utf-8')
    (tmp_path/'view.ts').write_text('export class View {}',encoding='utf-8')
    (tmp_path/'private.py').write_text('private_value=1',encoding='utf-8')
    (tmp_path/'untracked.py').write_text('untracked=1',encoding='utf-8')
    git('add','README.md','main.py','view.ts','private.py')
    (tmp_path/'.gitignore').write_text('private.py\n',encoding='utf-8')
    return tmp_path

def test_map_symbols_ignore_rules_and_read_only(repo,monkeypatch):
    monkeypatch.setattr(core,'model_result',lambda *a,**kw:pytest.fail('Unexpected LLM path'))
    before=(repo/'main.py').read_bytes()
    result=core.scan(repo)
    files={f['file']:f for f in result['files']}
    assert set(files)=={'README.md','main.py','view.ts'}
    assert files['main.py']['symbols']==[{'name':'compute','line':3}]
    assert files['main.py']['imports']==['math']
    assert files['view.ts']['symbols']==[{'name':'View','line':1}]
    assert result['steps'][0]['file']=='README.md'
    assert (repo/'main.py').read_bytes()==before
    assert result==core.scan(repo)

def test_invalid_repository(tmp_path):
    with pytest.raises(ValueError,match='Git'):
        core.scan(tmp_path)

def test_reject_fake_path_from_stub(repo,monkeypatch):
    fake=core.Trail(steps=[core.Step(file='../outside.py',line=1,explanation='bad',question='bad?')])
    monkeypatch.setattr(core,'model_result',lambda *a,**kw:fake)
    with pytest.raises(ValueError,match='validation'):
        core.scan(repo,ai=True)

def test_limit_oversized_file(repo):
    (repo/'main.py').write_text('#'+'x'*100_001,encoding='utf-8')
    assert 'main.py' not in {f['file'] for f in core.scan(repo)['files']}

def test_cli(repo):
    result=CliRunner().invoke(app,[str(repo),'--json'])
    assert result.exit_code==0,result.output
    assert json.loads(result.output)['mode']=='local'
