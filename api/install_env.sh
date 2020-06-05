#!/bin/bash
source parse_config.sh
eval $(parse_yaml config.conf "config_")
VIRTDIR="/tmp/virtualenv/"${config_virtualenv_dir}
VIRTNAME=${config_virtualenv_name}
PIPS=(${config_virtualenv_pips})

export LC_ALL=C
#sudo apt-get update
sudo apt-get -y install python3-dev python3-pip
sudo pip3 install virtualenv
mkdir -p ${VIRTDIR}
pushd ${VIRTDIR}
#initiate minion environment
virtualenv -p python3 ${VIRTNAME}
source ${VIRTNAME}/bin/activate
#install needed python modules
for i in ${PIPS[@]}; do                                                         # install needed pips
    if [[ ${i} = *"=="* ]]; then
        echo "NOT UPGRADING"
        pip3 install --index-url=https://pypi.python.org/simple/ ${i}
    else
        pip3 install --index-url=https://pypi.python.org/simple/ --upgrade ${i}
    fi
done
pip3 freeze
popd
deactivate
