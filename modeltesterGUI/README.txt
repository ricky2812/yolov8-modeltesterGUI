folder structure: 
Apple_detection
    - package
        - src 
            - weights

Things to Edit: 

1. Create respective folders

Setup.py: 
1. change name according to your use case
2. Add the python package in install_requires list as in as reqirements.txt format
3. in entry point provide the same name

run.py: 
1. in run.py -> move all the main content to main function. 

MANIFEST.in: 
1. Include your python sub folder dependencies (ex: Models)

Execution: 
pip3 install build

python3 -m build 

Testing: 

pip3 install dist/Apple_detection.tar.gz
