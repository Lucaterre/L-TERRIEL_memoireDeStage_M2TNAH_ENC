#!/bin/sh

# requirements sur slave
#(sudo) apt-install python-pip
#(sudo) apt install virtualenv

echo "### ----- BUILDING ENVIRONMENT ----- ###"
virtualenv venv -p python3
. venv/bin/activate  # "source venv/bin/activate" fails
python --version
echo ">> getting requirements"
pip install -r requirements.txt

echo "### ----- LINTER ----- ###"
# this test will need to be better applied further in the developpement
# because it supposes that every python file that needs testing is in Tool, on the same level...
#for entry in KB-app/*.py
#do
    #pylint-fail-under --fail_under 6.0 $entry
    # adjust grade if necessary
    # will use .pylintrc in master
#done

#ADD (Lucas) :
# - add tests Pylint on others directory
#

for entry in KB-app/kraken_benchmark.py
do
    pylint-fail-under --fail_under 7.0 $entry
    # adjust grade if necessary
    # will use .pylintrc in master
done

for entry in KB-app/kb_report/*.py
do
    pylint-fail-under --fail_under 7.0 $entry
    # adjust grade if necessary
    # will use .pylintrc in master
done

for entry in KB-app/kb_utils/*.py
do
    pylint-fail-under --fail_under 7.0 $entry
    # adjust grade if necessary
    # will use .pylintrc in master
done

for entry in KB-app/STS_Tools/SynSemTS.py
do
    pylint-fail-under --fail_under 7.0 $entry
    # adjust grade if necessary
    # will use .pylintrc in master
done


# echo "### ----- TEST ----- ###"
# test.py for additional functional tests
# python test.py
