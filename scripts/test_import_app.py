import sys
# simulate what api.py does
sys.path.append(str('c:/Fintech'))
# also ensure credit_engine is on path
sys.path.append(str('c:/Fintech/credit_engine'))

try:
    import credit_engine.app as app
    print('imported credit_engine.app', flush=True)
    print('calling get_fraud...', flush=True)
    f = app.get_fraud()
    print('got fraud detector', f, flush=True)
except Exception as e:
    print('error', e)
    import traceback; traceback.print_exc()
