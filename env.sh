#! /usr/bin/env sh
#
# Setup virtualenv

if [ $# -ne 1 ]; then
  command=`basename $0`
  echo "Usage: ${command} <enviroment name>" 1>&2
  exit 1
fi

ENV_NAME=$1
VIRTUALENV="virtualenv-1.10.1"

# Download ez_setup.py
wget https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py

# Download virtualenv
curl -O https://pypi.python.org/packages/source/v/virtualenv/${VIRTUALENV}.tar.gz
tar xvfz ${VIRTUALENV}.tar.gz
cp ${VIRTUALENV}/virtualenv.py virtualenv.py
rm -rf ${VIRTUALENV} ${VIRTUALENV}.tar.gz

# Setup virtualenv
python virtualenv.py ${ENV_NAME}
${ENV_NAME}/bin/python ez_setup.py
${ENV_NAME}/bin/easy_install pip

# Install flask
${ENV_NAME}/bin/pip install -r requirements.txt

# Cleanup
rm ez_setup.py* virtualenv.py* setuptools*.zip

echo "You can use virtualenv by typing \"source ${ENV_NAME}/bin/activate\"."
echo "Disable virtuallenv \"deactivate\"."

