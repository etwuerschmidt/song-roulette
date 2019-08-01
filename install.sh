#!/bin/sh
echo "Installing latest modules"
cd Slack
python setup.py install 
cd ../Spotify
python setup.py install 
echo "Installation complete"