python-3.7.2.exe InstallAllUsers=0 Include_launcher=0 Include_test=0 SimpleInstall=1 SimpleInstallDescription="Just for me, no test suite."
python -m pip install --upgrade pip --trusted-host pypi.org --trusted-host files.pythonhosted.org -q
pip install -r requirements.txt --trusted-host pypi.org --trusted-host files.pythonhosted.org
