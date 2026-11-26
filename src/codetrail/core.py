import ast
import re
import subprocess
from pathlib import Path
from pydantic import BaseModel, Field
from .support import read_text, model_result

class Step(BaseModel):
    file: str
    line: int = Field(ge=1)
    explanation: str = Field(min_length=1, max_length=800)
    question: str = Field(min_length=1, max_length=400)
class Trail(BaseModel):
    steps: list[Step] = Field(min_length=1, max_length=12)

def scan(root: Path, goal='Understand the architecture', ai=False):
    root = root.resolve(strict=True)
    if not root.is_dir() or len(goal)>1500:
        raise ValueError('Provide a local Git repository and a goal up to 1500 characters.')
    try:
        # ls-files does not run project code, hooks, or repository-defined commands.
        process = subprocess.run(['git','-C',str(root),'ls-files','--cached','--exclude-standard','-z'],
                                 capture_output=True, timeout=20, check=True)
    except (OSError, subprocess.SubprocessError) as exc:
        raise ValueError('Unable to list Git-tracked files. Check Git and repository path.') from exc
    paths = sorted(set(process.stdout.decode('utf-8').strip('\0').split('\0')))
    if len(paths)>5000:
        raise ValueError('Maximum 5,000 tracked files.')
    # Also exclude tracked files matching current ignore rules; ls-files alone includes them.
    ignored = subprocess.run(['git','-C',str(root),'check-ignore','--no-index','--stdin','-z'],
                             input=process.stdout, capture_output=True, timeout=20)
    if ignored.returncode not in (0,1):
        raise ValueError('Unable to apply repository ignore rules.')
    excluded = set(ignored.stdout.decode('utf-8').split('\0'))
    items, total, skipped = [], 0, 0
    for name in paths:
        relative = Path(name)
        if not name or name in excluded or relative.suffix not in ('.py','.js','.ts','.tsx','.jsx','.md','.toml','.json'):
            skipped += 1
            continue
        if any(part.startswith('.') or part in ('node_modules','vendor','dist','build') for part in relative.parts):
            skipped += 1
            continue
        path = root / relative
        if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(root):
            skipped += 1
            continue
        if path.stat().st_size>100_000:
            skipped += 1
            continue
        if total + path.stat().st_size>2_000_000:
            skipped += 1
            continue
        try:
            text = read_text(path, 100_000)
        except (ValueError, OSError):
            skipped += 1
            continue
        total += len(text.encode('utf-8'))
        symbols, imports = [], []
        if path.suffix == '.py':
            try:
                tree = ast.parse(text)
                for node in ast.walk(tree):
                    if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)):
                        symbols.append({'name':node.name,'line':node.lineno})
                    if isinstance(node,ast.Import):
                        imports.extend(a.name for a in node.names)
                    elif isinstance(node,ast.ImportFrom):
                        imports.append(node.module or '.')
            except SyntaxError:
                pass
        elif path.suffix in ('.js','.ts','.jsx','.tsx'):
            for number, line in enumerate(text.splitlines(),1):
                match = re.search(r'\b(?:function|class|interface)\s+(\w+)',line)
                if match:
                    symbols.append({'name':match.group(1),'line':number})
        items.append({'file':name, 'lines':max(1,len(text.splitlines())),
                      'symbols':symbols[:30], 'imports':imports[:30]})
    if not items:
        raise ValueError('No supported tracked text files found. Commit source files first.')
    terms = set(re.findall(r'\w+',goal.lower()))
    def priority(item):
        name = item['file'].lower()
        base = 30 if name.endswith('readme.md') else 20 if name.endswith(('pyproject.toml','package.json')) else 10 if Path(name).stem in ('main','app','cli','index') else 0
        return -(base + 5*sum(term in name for term in terms)), name
    selected = sorted(items,key=priority)[:12]
    steps = [{'file':i['file'],'line':i['symbols'][0]['line'] if i['symbols'] else 1,
              'explanation': 'Start with project context.' if i['file'].lower().endswith('.md') else 'Inspect this module and its declared symbols; ordering is heuristic.',
              'question':'What inputs does this file accept, and where do they go next?'} for i in selected]
    if ai:
        response = model_result(Trail, 'Create a learning path for the goal. Use only supplied '
            'files and symbol line numbers (or line 1). Module relationships are inferred, '
            'not confirmed runtime behavior. Do not invent symbols or dependencies.',
            {'goal':goal,'map':selected})
        lookup = {i['file']: {1} | {s['line'] for s in i['symbols']} for i in selected}
        for step in response.steps:
            if step.file not in lookup or step.line not in lookup[step.file]:
                raise ValueError('Generated path or line failed validation; learning path withheld.')
        steps = [s.model_dump() for s in response.steps]
    return {'goal':goal,'mode':'ai' if ai else 'local','files':items,'skipped_files':skipped,'steps':steps,
            'note':'Python symbols use AST; JS/TS symbols use a limited regex heuristic. No code is executed. AI receives only selected paths, symbols, and import names, not source bodies.'}

def markdown(result):
    out = ['# CodeTrail learning path','',result['goal'],'',f"Indexed {len(result['files'])} files; skipped {result['skipped_files']}.",'']
    for index, step in enumerate(result['steps'],1):
        out.extend([f"## {index}. {step['file']}:{step['line']}",'',step['explanation'],'',step['question'],''])
    out.append(result['note'])
    return '\n'.join(out)
