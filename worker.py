"""Optional queue entry for schedulers without a container runtime socket."""
import json
import os
from pathlib import Path
import subprocess
import time

os.umask(0o077)
queue = Path(os.getenv('LAOWANG_QUEUE_DIR', '/queue'))
data = Path(os.getenv('LAOWANG_DATA_DIR', '/data'))
queue.mkdir(parents=True, exist_ok=True)


def respond(stem, value):
    temporary = stem.with_suffix('.tmp')
    temporary.write_text(json.dumps(value))
    temporary.replace(stem.with_suffix('.result'))


for pending in queue.glob('*.running'):
    respond(pending, {'exit_code':125, 'error':'worker_restarted_no_replay'})
    pending.unlink()
print('Laowang worker ready; browser starts only on request', flush=True)
while True:
    for request in sorted(queue.glob('*.request')):
        running = request.with_suffix('.running')
        request.rename(running)
        try:
            job = json.loads(running.read_text())
            if job.get('store') not in ('laowang', 'status') or not 0 <= time.time()-job['created'] <= 300:
                raise ValueError('invalid_or_expired_request')
            cmd = ['node', str(Path(__file__).with_name('sign.cjs'))]
            if job['store']=='status': cmd.append('--status')
            started = time.time()
            with running.with_suffix('.log').open('w') as log:
                process = subprocess.run(['timeout','--kill-after=15','300',*cmd],stdout=log,stderr=subprocess.STDOUT)
            output = data/'result.json'
            result = json.loads(output.read_text()) if output.exists() and output.stat().st_mtime >= started else {}
            outcome = {'success':process.returncode==0 and result.get('sign_in_confirmed') is True,
                       'reason':None if result.get('sign_in_confirmed') else result.get('status','result_missing')}
            response = {'exit_code':process.returncode,'outcome':outcome,'finished':time.time()}
        except Exception as error:
            response = {'exit_code':125,'error':type(error).__name__}
        respond(running,response)
        running.unlink()
    time.sleep(1)
