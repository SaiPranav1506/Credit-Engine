import sys
print('START test_import_src')
sys.path.append('c:/Fintech/credit_engine')
try:
    import src
    print('ok', src)
except Exception as e:
    print('error', e)
    import traceback
    traceback.print_exc()
print('END test_import_src')
