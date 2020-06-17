import os

cwd = os.getcwd()
print(os.getcwd())
os.system('cd docs && make clean')
os.system('cd docs && sphinx-apidoc -o source ..')
os.system('cd docs && make html')
os.system('cd docs && sphinx-build -b rinoh source _build/rinoh')
# os.system('cd docs && firefox build/html/index.html &')

