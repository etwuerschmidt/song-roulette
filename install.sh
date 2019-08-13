#!/bin/sh
MOD1=${1:-none}
for file in *; do
	if [[ -d $file ]]; then
		if [[ "$MOD1" != "none" ]]; then
			if [[ "$file" == "$MOD1" ]]; then
				echo "Installing module for $file"
				cd $file
				python setup.py install > NUL
				cd ..
				echo "Installation complete"
				exit
			fi
		else
			echo "Installing module for $file"
			cd $file
			python setup.py install > NUL
			cd ..
		fi
	fi
done
echo "Installation complete"
exit